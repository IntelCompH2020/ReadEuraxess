# ReadEuraxess
Generation of a dataset including published offers from Euraxess

## Setting up the ingestion system

The process is composed of two phases:

   1. Daily download of offers
   
      This is a simple process that needs to be set up as a cron process. Everyday the following command should be run:
   
      ```> wget -O - "ANONYMIZED_EURAXESS_JOBPOSTS_URL" --output-document=[your_path]/jobs_`date +%Y-%m-%d_%H:%M:%S`.xml```

<div style="background-color: yellow; color: black; padding: 10px; border-radius: 5px; margin: 20px 0;">
    <strong>Warning:</strong> Permision to crawl this dataset should be granted by the website owners. You should refer to them to get the URL that should be used in the previous terminal command line.
</div>
Permision to crawl this dataset should be granted by the website owners

   3. To consolidate all downloaded data (since offers appear repeteade in the retrieved files) we need to run the following python script

      ```> python main.py -c config_file```
   
      This scripts processes the downloades XML files, extracts the necessasry information, and consolidates the offers in a final CSV file
      
The script keeps track of downloaded files that have already been processed. If the whole dataset wants to be regenerated from scratch, `Step 2` needs to be carried out activating the `--resetCSV` flag.

![This project has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 101004870. H2020-SC6-GOVERNANCE-2018-2019-2020 / H2020-SC6-GOVERNANCE-2020](https://github.com/IntelCompH2020/.github/blob/main/profile/banner.png)
