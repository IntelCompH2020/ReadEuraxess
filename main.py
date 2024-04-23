import xml.etree.ElementTree as ET
import re
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
from datetime import datetime
import os
import argparse
import configparser


class jobParser ():

	__listJobs_ = list ()

	def __init__ (self, xmlFile):

		#On creation of the objet we will process the given XML file
		#1. We extract all job offers in the file
		#2. We process each job offer with function self.__extractJobData_

		try:
			with open(xmlFile, 'r',encoding='utf-8') as f:
				data = f.read()

			escape_illegal_xml_characters = lambda x: re.sub(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]', '', x)
			

			tree = ET.ElementTree(ET.fromstring(escape_illegal_xml_characters(data)))

			#tree = ET.parse(xmlFile, parser = ET.XMLParser(encoding = 'utf-8'))
			root = tree.getroot()
			
			jobs = [job for job in root.iter('job-opportunity')]

			self.__listJobs_ = [self.__extractJobData_(job) for job in jobs]

		except Exception as E:
			print ('Error while processing file, %s, %s' % (xmlFile, E))
			exit()

	def __extractJobData_ (self, job):
		jobsDict = dict()
		for data  in job.iter():
			jobsDict[data.tag.replace('-','_')] = data.text
		return jobsDict

	def getListJobs (self):
		return self.__listJobs_

	def getIds (self):
		return [job['job_id'] for job in self.__listJobs_]

	def getKeys (self, position = 0):
		return self.__listJobs_[position].keys()

	def getJob (self, position):
		return self.__listJobs_[position]


if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Scripts to generate a CSV file including all job offers from the Euraxess site')
	parser.add_argument('-c','--config', help='Configuration file to use', default='config.cf')
	parser.add_argument('--resetCSV', help='Reset CSV and process all files', action='store_true')
	argus = parser.parse_args()

	config = configparser.ConfigParser()
	config.read( argus.config )

	rawdata_path = Path(config['euraxess']['path'])
	csv_file = Path(config['euraxess']['csv_file'])
	p_extension = config['euraxess']['proc_extension']
	fields = config['euraxess']['fields'].split(',')

	#Generate a sorted list with all files to process, and remove those
	#that have already been processed
	#
	#We sort using file names, which should include the date of creation
	#E.g.: jobs_2022-02-10_06/12/01.xml 
	files = [el for el in sorted(rawdata_path.iterdir()) if el.name.startswith('jobs')]
	if not argus.resetCSV:
		files = [el for el in files if not el.name.endswith(p_extension)]

	#We need to keep track of first downloadtime for each offer, which will be the 
	#data of publication. We create a dictionary job_id : downloadtime for that
	#If reset_CSV or non-existing CSV, the dictionary is initially empty
	if (argus.resetCSV) or (not csv_file.is_file()):
		published = {}
		#Delete if exists and creates empty file
		csv_file.unlink(missing_ok=True)
	else:
		df = pd.read_csv(csv_file, low_memory=False)
		published = {el[0]:el[1] for el in df[['job_id', 'published']].values.tolist()}

	for thisfile in files:
		
		print ('Processing %s' % (thisfile))
		listJobs = jobParser (thisfile)
		jobsInFile = listJobs.getListJobs()
		
		#Keep only desired values and filling with empty
		#strings not existing keys in each offer
		df = pd.DataFrame(jobsInFile)
		df = df.filter(items=fields)
		df['job_id'] = df['job_id'].apply(int)
		#We add the last update time according
		#to present file name, which is in format jobs_date_time.xml
		thisFileDate = datetime.strptime ( (thisfile.name.split('_')[1]), "%Y-%m-%d")
		df['updatetime'] = thisFileDate

		#Lastly, we need to set publication dates. We start by updating dictionary "published"
		#including new pairs job_id : thisFileDate for new job offers
		new_job_ids = [el for el in df.job_id.values.tolist() if el not in published.keys()]
		for el in new_job_ids:
			published[el] = thisFileDate
		df['published'] = df['job_id'].map(published)

		#We are done, just need to update the CSV file
		try:
			euraxess_df = pd.read_csv(csv_file)
		except:
			euraxess_df = pd.DataFrame()
			if not argus.resetCSV:
				print('CSV file not present or not containing valid dataframe')

		#We will next append new offers, and drop rows with duplicated ids
		#keeping the last occurrence of a job offer. In this way, we keep 
		#the original publication time, but update updatetime for repeated offers
		euraxess_df = pd.concat([euraxess_df, df], ignore_index=True)
		euraxess_df.drop_duplicates(subset='job_id', keep='last', inplace=True, ignore_index=False)
		euraxess_df.sort_values(['job_id'], ascending=True, inplace=True)
				
		#We save the dataframe back to disk and rename processed directory
		#This is not very efficient, but we can make sure that only processed
		#directories are marked as such
		euraxess_df.to_csv(csv_file, index=False)
				
		if not (thisfile.name.endswith (p_extension)):
			thisfile.rename(thisfile.as_posix().replace('xml',p_extension))
