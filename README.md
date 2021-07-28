# zeit&ort

### Feature enrichment API for Data Science and Analytics.

###### Providing temporal and geographical information to ease and speed up data gathering process. 

---

 Final Project for Pipeline - Data Engineering Academy
 by Tomek Florek

---



#### Based on a given IP Address the API returns:
- the location
- population density score 
- current and near weather -
- current and near public holidays in specific locations.

The API supports these features on the global scale for up to 5 years in the future.


##### Data Sources:

- [Calendarific API](https://calendarific.com/)

- [MaxMind GeoLite2 Database](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data)

- [OpenCellID Database](https://opencellid.org/downloads.php)

- [OpenWeatherMap API](https://openweathermap.org/api)

 The project is built using: 

- Mix of Makefile and Python for the ETL

- CI/CD with Github Actions, using pytest & flake8 

- API built using FastAPI framework

- GCP Compute Engine hosting

- SQLite Database

  

### Try it out here

[API Documentation](http://35.234.75.114:8000/docs) 


### Example 
For IP Address: 46.88.58.188 (Berlin)

Request:
http://35.234.75.114:8000/api/get_all?ip=46.88.58.18&period=0 

Response:

```json
{
  "country_iso": "de",
  "region_iso": "be",
  "region_name": "Land Berlin",
  "city_name": "Berlin",
  "latitude": "52.4972",
  "longitude": "13.3299",
  "density_score": 15828,
  "is_holiday": false,
  "description": "light rain",
  "temperature": 25.38
}
```


