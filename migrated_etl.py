#--------------------------------------------------------------
# Imports
#--------------------------------------------------------------
import config
import json
import requests

import great_expectations as ge
import os.path
import pandas as pd

from prefect import Flow
from prefect import Parameter
from prefect import Task
from prefect import context
from prefect import task
from prefect.schedules import IntervalSchedule
from prefect.tasks.great_expectations import RunGreatExpectationsValidation
from prefect.tasks.shell import ShellTask

countries_url = 'https://calendarific.com/api/v2/countries'
holidays_url = 'https://calendarific.com/api/v2/holidays'

years = ['2021','2022','2023','2024','2025','2026','2027']

countries_params = {
	'api_key': config.CALENDARIFIC_KEY
}


holidays_params = countries_params
holidays_params['year'] = 2021
holidays_params['country'] = 'DE'
holidays_params['type'] = 'national,local'

# Define checkpoint task
validation_task = RunGreatExpectationsValidation()


def get_from_json_api(url,params):
	response = requests.get(url,params)
	data	 = json.loads(response.text)
	return data

#--------------------------------------------------------------
# Define custom task functions
#--------------------------------------------------------------
@task
def get_schema(sql_file):
	with open(sql_file) as f:
		schema = f.read()
	return schema

@task 
def get_countries():
	#logger = context.get("logger")
	#logger.info("Extracting countries")

	return get_from_json_api(countries_url, countries_params)

# Transform the countries in JSON to extract each ISO code
@task 
def transform_countries(countries_json):
	#Parse json to get only country codes
	country_list = jq.compile('.response.countries[] | ."iso-3166"').input(countries_json).text()
	#Clean the result and convert to a list
	country_list = country_list.translate(str.maketrans('"',' ','\n')).split()

	print(country_list)
	return country_list

#Get holidays for each of the countries	
@task
def get_holidays_for_country(country_list):
	
	json_file = []
	holiday_list = []
	big_list = ''

	for country in country_list:
		holidays_params['country'] = country
		holidays_json = get_from_json_api(holidays_url,holidays_params)
		#holiday_list = holiday_list + list(jq.iter('.response.holidays[] | [paths(scalars) as $path | {"key": $path | join("_"), "value": getpath($path)}] | from_entries',holidays_json))


	return holiday_list

# Task for picking the relevant columns from json and converting it to csv
@task
def transform_holidays(holiday_list):
	
	#print(holidays_json.len())
	#holidays_list = jq.compile('.response.holidays[] | [paths(scalars) as $path | {"key": $path | join("_"), "value": getpath($path)}] | from_entries').input(holidays_json).text()
	
	df = pd.DataFrame(holiday_list)
	df = df[['name','country_id','country_name','date_iso','locations','states','type_0','type_1']]
	df = df[df.type_0 != 'Season']
	#df = pandas.read_json(open('holidays.json','r',encoding='utf8'), lines=True)
	df.to_csv('data/holiday_no_work.csv')

	return df

# Task for retrieving batch kwargs including csv dataset
@task
def get_batch_kwargs(datasource_name, dataset):
    dataset = ge.read_csv(dataset)
    return {"dataset": dataset, "datasource": datasource_name}

#--------------------------------------------------------------
# Instantiate task classes
#--------------------------------------------------------------
run_in_bash = ShellTask(name='run a command in bash')



def main():
	#schedule = IntervalSchedule(start_date=datetime.utcnow() + timedelta(seconds=1), interval=timedelta(minutes=1))

	with Flow("ETL") as flow:
		

		#postgres_connect = run_in_bash(command = 'psql -U tomek -h soobrosa-1789.postgres.pythonanywhere-services.com -p 11789 -d postgres')
		
		if (os.path.exists('data/holiday_no_work.csv') is False):
			print("hello")
			countries_json = get_countries()
			country_list = transform_countries(countries_json)
			holidays_list = get_holidays_for_country(country_list)
			holidays = transform_holidays(holidays_list)

		datasource_name = Parameter("datasource_name")
		dataset = Parameter("dataset")
		batch_kwargs = get_batch_kwargs(datasource_name, dataset)

		expectation_suite_name = Parameter("expectation_suite_name")
		validation_task(
			batch_kwargs=batch_kwargs,
			expectation_suite_name=expectation_suite_name,
	    )


	flow.run(
    parameters={
		"datasource_name": "data__dir",
		"dataset": "data/holiday_no_work.csv",
		"expectation_suite_name": "holiday_no_work.warning",
    },)

if __name__ == "__main__":
	main()



'name','description','country_id','country_name','date_iso','locations','states','type_0','type_1'
