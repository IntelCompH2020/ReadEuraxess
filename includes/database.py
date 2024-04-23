'''sudo apt-get update
sudo apt-get install libpq-dev python-dev
sudo pip install psycopg2
'''

import psycopg2
from datetime import datetime


class psql:

	_conexion__ = ''
	#_saveValues__ = ['job_opportunity', 'job_id', 'description', 'job_title', 'job_summary', 'job_description', 'research_field', 'main_research_field', 'sub_research_field', 'researcher_profile', 'type_of_contract', 'job_status', 'hours_per_week', 'job_start_date', 'application_deadline', 'science4refugees', 'additional_information', 'comment', 'info_website', 'eu_funding', 'framework_programme', 'job_reference_number', 'work_location', 'nr_job_positions', 'job_organisation_institute', 'job_country', 'job_city', 'hiring_org_inst', 'organisation_institute', 'organisation_institute_type', 'country', 'e_mail', 'website', 'application_details', 'how_to_apply', 'application_email']

	def __init__( self, db, host, user, passwd, ):
		try:
			cad = ("host='%s' dbname='%s' user='%s' password='%s'" % (host, db, user, passwd))
			self._conexion__ = psycopg2.connect(cad)
			print ('Conectado a %s' % (db))
		except Exception as E:
			print ('imposible conectarse a la base de datos, %s' % (E))

	def insertJobs (self,jobs, keys, filedatetime):

		date = datetime.fromtimestamp(filedatetime).strftime('%Y/%m/%d')

		keysStr 	= 'INSERT INTO  job ( ' + (',').join ([ ('"%s"' % (key)) for key in keys]) + ') VALUES (' 
		#generamos una lista que contiene la cadena %s tantas veces como valores a insertar:
		values 		= (',').join(["%s" for key in keys])

		valuesList = list ()
		
		for job in jobs:
			#si algun campo no existe en el trabajo, se pone a nulo:
			for key in keys:
				job[key] = job.get(key, None)
			
			job['downloadtime'] = date
			job['updatetime'] = date
			

			valuesList.append ([job[key] for key in keys])
		
		
		#sql = keysStr + values + ') ON CONFLICT (job_id) DO UPDATE SET job_status=excluded.job_status, updatetime=NOW()'
		#Se actualizan casi todos los campos porque, muchas veces, en las ofertas repetidas las últimas tienen muchos más campos rellenados.
		sql = keysStr + values + ") ON CONFLICT (job_id) DO UPDATE SET "\
			"job_status=excluded.job_status, required_languages=excluded.required_languages, language_level=excluded.language_level, language=excluded.language,"\
			"benefits=excluded.benefits,city=excluded.city, application_deadline=excluded.application_deadline, type_of_contract=excluded.type_of_contract,"\
			"hours_per_week=excluded.hours_per_week,years_of_research_experience=excluded.years_of_research_experience,additional_requirements=excluded.additional_requirements,"\
			"degree=excluded.degree,discipline=excluded.discipline,required_education_level=excluded.required_education_level,job_start_date=excluded.job_start_date,"\
			"required_research_experiences=excluded.required_research_experiences,main_research_field=excluded.main_research_field,nr_job_positions=excluded.nr_job_positions,"\
			"work_location=excluded.work_location,organisation_institute=excluded.organisation_institute,organisation_institute_type=excluded.organisation_institute_type,"\
			"job_summary=excluded.job_summary,job_description=excluded.job_description,description=excluded.description, updatetime='"+ date +"' "

 		
		cur = self._conexion__.cursor()
		cur.executemany(sql, valuesList)
		self._conexion__.commit()

