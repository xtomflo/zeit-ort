#--------------------------------------------------------------
# Imports
#--------------------------------------------------------------
from prefect import task, Flow, Task, context
from prefect.tasks.shell import ShellTask
from prefect.schedules import IntervalSchedule
import config
import requests
import json
import jq
import pandas as pd

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

	#holidays_params['country'] = 'DE'  


	for country in country_list:
		holidays_params['country'] = country
		holidays_json = get_from_json_api(holidays_url,holidays_params)
		holiday_list = holiday_list + list(jq.iter('.response.holidays[] | [paths(scalars) as $path | {"key": $path | join("_"), "value": getpath($path)}] | from_entries',holidays_json))


	'''
	 
		print(f' Pulling holidays for: {country}')
		df = pd.json_normalize(holidays_json)
		print(df)
		# Flattening the returned json completely
		holidays_list = jq.compile('.response.holidays[] | [paths(scalars) as $path | {"key": $path | join("_"), "value": getpath($path)}] | from_entries').input(holidays_json).text()
		print(holidays_list)

		big_list += holidays_list

	
	new_list = big_list.replace('\n',',\n')

	f = open('holidaytext.json','w')
	f.write(new_list)
	f.close()

	#pdb.set_trace()
	df = pd.read_json(new_list, lines=True)
	#df = pd.DataFrame(eval(new_list))
	df.to_json("holidays.json")
	'''
	return holiday_list


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


#--------------------------------------------------------------
# Instantiate task classes
#--------------------------------------------------------------
run_in_bash = ShellTask(name='run a command in bash')



def main():
	#schedule = IntervalSchedule(start_date=datetime.utcnow() + timedelta(seconds=1), interval=timedelta(minutes=1))

	with Flow("ETL") as flow:
		
		#transform_holidays.set_upstream(get_holidays_for_country)

		#postgres_connect = run_in_bash(command = 'psql -U tomek -h soobrosa-1789.postgres.pythonanywhere-services.com -p 11789 -d postgres')
		countries_json = get_countries()

		country_list = transform_countries(countries_json)

		holidays_list = get_holidays_for_country(country_list)

		holidays = transform_holidays(holidays_list)


	flow.run()

if __name__ == "__main__":
	main()



'name','description','country_id','country_name','date_iso','locations','states','type_0','type_1'
