# zeit&ort

### Feature enrichment API for Data Science and Analytics.

###### Providing temporal and geographical information to ease and speed up data gathering process. 

---

 Final Project for Pipeline - Data Engineering Academy
 by Tomek Florek

---



Based on a given IP Address the API returns the location, population density score, current and near weather and current and near public holidays for users location. 

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

