"""
Czech Postal Code Database Import Script
=======================================

This script imports postal code (PSČ) data for Czech municipalities from a CSV file
into a MongoDB database. Each row in the CSV contains information about a municipality,
including its name, district, postal code, and geographical coordinates.

The data is stored in the "Okresy" collection within the "RealEstates" database,
which can later be used for geocoding and district lookup operations.

Requirements:
    - pandas
    - pymongo
    - csv
    - time
"""

import pymongo
import csv

# Initialize MongoDB connection
client = pymongo.MongoClient("localhost", 27017)
db = client["RealEstates"]
collection = db["Okresy"]

# Path to the CSV file containing postal code data
csv_file = "souradnice.csv"

"""
Process and import CSV data
--------------------------

This section reads the CSV file containing Czech postal code data
and imports each row into the MongoDB database.

The CSV file is expected to have the following columns:
- Obec: Name of the municipality
- Okres: District name
- PSČ: Postal code
- Latitude: Geographic latitude coordinate
- Longitude: Geographic longitude coordinate

Each row is converted into a document in the following format:
- obec: Name of the municipality (string)
- okres: District name (string)
- psc: Postal code (string)
- latitude: Geographic latitude coordinate (float)
- longitude: Geographic longitude coordinate (float)

The documents are inserted one by one into the "Okresy" collection.
"""
with open(csv_file, mode="r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Create document with data from the current row
        data = {
            "obec": row["Obec"],
            "okres": row["Okres"],
            "psc": row["PSČ"],
            "latitude": float(row["Latitude"]),
            "longitude": float(row["Longitude"])
        }

        # Insert document into MongoDB collection
        collection.insert_one(data)