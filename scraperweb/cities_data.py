"""
Czech Towns Geocoding Module
===========================

This module geocodes Czech towns and cities, categorizing them by administrative roles.
It retrieves the geographic coordinates (latitude and longitude) for various Czech towns
and cities and stores them in a MongoDB database.

The module processes three categories of towns:
1. Regional capitals (krajská města)
2. District towns (okresní města)
3. Towns with extended competence (obce s rozšířenou působností)

Each town is geocoded using the Nominatim geocoder from the geopy library,
and the coordinates along with administrative status are stored in MongoDB.

Requirements:
    - pandas
    - geopy
    - pymongo
    - time
"""

import pandas as pd
from geopy.geocoders import Nominatim
import pymongo
import time

# MongoDB connection setup
client = pymongo.MongoClient("localhost", 27017)
db = client["RealEstates"]

# Initialize geocoder
geolocator = Nominatim(user_agent="geopy")

# Test geocoding
location = geolocator.geocode("Praha")

# Load district towns from CSV
district_towns = pd.read_csv("scraperweb/OkresniMesta.csv")
district_towns_text = district_towns["text"]

# List of regional capitals
region_towns = ["Praha", "České Budějovice", "Plzeň", "Karlovy Vary", "Liberec", "Hradec Králové", "Pardubice",
                "Jihlava", "Brno", "Olomouc", "Ostrava", "Zlín"]

# Test geocoding for a specific town
location = geolocator.geocode("Ústí nad Labem, Czech Republic")
print(location.latitude, location.longitude)

# Sample data structure for database insertion
data_to_db = {
    "Název": "Ústí nad Labem",
    "Souřadnice": [location.latitude, location.longitude],
    "Krajské město": True,
    "Okresní město": True,
    "S rozšířenou působností": True
}

"""
Process and store regional capitals
----------------------------------

This section geocodes all regional capitals in the Czech Republic and
stores their coordinates and administrative status in the MongoDB database.

Each city is geocoded, and the following information is stored:
- Name (Název)
- Latitude (Zeměpisná šířka)
- Longitude (Zeměpisná délka)
- Regional capital status (Krajské město): True
- District town status (Okresní město): True
- Extended competence status (S rozšířenou působností): True

A delay of 1 second is added between geocoding requests to avoid
hitting rate limits on the Nominatim service.
"""
for x in region_towns:
    location = geolocator.geocode(x)
    latitude = location.latitude
    longitude = location.longitude
    print(latitude, longitude)
    data_to_db = {
        "Název": x,
        "Zeměpisná šířka": latitude,
        "Zeměpisná délka": longitude,
        "Krajské město": True,
        "Okresní město": True,
        "S rozšířenou působností": True
    }
    collection = db["Towns"]
    collection.insert_one(data_to_db)
    print(data_to_db)
    time.sleep(1)

"""
Process and store district towns
-------------------------------

This section geocodes all district towns in the Czech Republic
that are not regional capitals and stores their coordinates and 
administrative status in the MongoDB database.

Each town is geocoded, and the following information is stored:
- Name (Název)
- Latitude (Zeměpisná šířka)
- Longitude (Zeměpisná délka)
- Regional capital status (Krajské město): False
- District town status (Okresní město): True
- Extended competence status (S rozšířenou působností): True

A delay of 1 second is added between geocoding requests to avoid
hitting rate limits on the Nominatim service.
"""
for x in district_towns_text:
    location = geolocator.geocode(x)
    latitude = location.latitude
    longitude = location.longitude
    print(latitude, longitude)
    data_to_db = {
        "Název": x,
        "Zeměpisná šířka": latitude,
        "Zeměpisná délka": longitude,
        "Krajské město": False,
        "Okresní město": True,
        "S rozšířenou působností": True
    }
    collection = db["Towns"]
    collection.insert_one(data_to_db)
    print(data_to_db)
    time.sleep(1)

"""
Process and store towns with extended competence
----------------------------------------------

This section geocodes all towns with extended competence in the Czech Republic
that are neither regional capitals nor district towns, and stores their 
coordinates and administrative status in the MongoDB database.

Each town is geocoded, and the following information is stored:
- Name (Název)
- Latitude (Zeměpisná šířka)
- Longitude (Zeměpisná délka)
- Regional capital status (Krajské město): False
- District town status (Okresní město): False
- Extended competence status (S rozšířenou působností): True

A delay of 1 second is added between geocoding requests to avoid
hitting rate limits on the Nominatim service.
"""
towns_extended_competence = pd.read_csv("scraperweb/ObceSRozsirenouPusobnosti.csv")
towns_extended_competence_text = towns_extended_competence["text"]

for x in towns_extended_competence_text:
    location = geolocator.geocode(x)
    latitude = location.latitude
    longitude = location.longitude
    print(latitude, longitude)
    data_to_db = {
        "Název": x,
        "Zeměpisná šířka": latitude,
        "Zeměpisná délka": longitude,
        "Krajské město": False,
        "Okresní město": False,
        "S rozšířenou působností": True
    }
    collection = db["Towns"]
    collection.insert_one(data_to_db)
    print(data_to_db)
    time.sleep(1)