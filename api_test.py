import unittest
import requests
import api
import pytest

def addTwoNumbers(a,b):
	return a + b

class ApiTest(unittest.TestCase):
	API_URL = "http://127.0.0.1:5051/api"
	GET_IP_LOCATION_URL = "{}/ip_location".format(API_URL)
	GET_HOLIDAYS_URL = "{}/get_holidays".format(API_URL)
	GET_COUNTRY_HOLIDAYS_URL = "{}/get_country_holidays".format(API_URL)
	GET_IP_HOLIDAYS_URL = "{}/get_ip_holidays".format(API_URL)
	GET_IP_DENSITY_URL = "{}/get_ip_density".format(API_URL)

	def test1(self):
		c = addTwoNumbers(5,10)
		self.assertEqual(c,15)
	@pytest.mark.xfail
	def test2(self):
		c = addTwoNumbers(5,10)
		self.assertNotEqual(c,10)


	def test_ip_location(self):
		r = requests.get(ApiTest.GET_IP_LOCATION_URL, params={'ip':'178.62.37.124'})
		self.assertEqual(r.status_code, 200)
		self.assertEqual(len(r.json()),4)
		self.assertIn('city_name', r.json())
		self.assertEqual('New Taipei', r.json()['city_name'])
		# 178.62.37.124
		#{"city_name":"New Taipei","country_iso":"tw","region_iso":"nwt","region_name":"New Taipei"}
		
	def test_holidays(self):
		r = requests.get(ApiTest.GET_HOLIDAYS_URL)
		self.assertEqual(r.status_code, 200)

	def test_country_holidays(self):
		r = requests.get(ApiTest.GET_COUNTRY_HOLIDAYS_URL, params={'country':'de'})
		self.assertEqual(r.status_code, 200)

	def test_ip_holidays(self):
		r = requests.get(ApiTest.GET_IP_HOLIDAYS_URL, params={'ip':'178.62.37.124'})
		self.assertEqual(r.status_code, 200)

	def test_ip_density(self):
		r = requests.get(ApiTest.GET_IP_DENSITY_URL, params={'ip':'178.62.37.124'})
		self.assertEqual(r.status_code,200)

#if __name__=='__main__':
#	unittest.main()