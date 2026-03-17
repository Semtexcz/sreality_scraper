"""
Real Estate Scraper
==================

This module scrapes real estate data from sreality.cz for different regions in the Czech Republic.
It collects information about apartments for sale and stores them in a MongoDB database.

The script retrieves data such as price, location, size, and other property details.
It also adds geographic coordinates and postal codes to the data.

Requirements:
    - requests
    - beautifulsoup4
    - pymongo
    - loguru
    - geopy
    - re
    - datetime
    - time
"""

import requests as req
from bs4 import BeautifulSoup as bSoup
import re
from datetime import datetime
from loguru import logger
from geopy.geocoders import Nominatim
import time
import pymongo





# Establish connection to MongoDB
uri = "mongodb+srv://user:RealSight123@cluster.4kfctsm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster"
client = pymongo.MongoClient(uri)
# MongoDB connection
db = client["RealEstates"]

# Geocoding setup
geolocator = Nominatim(user_agent="geoapi")

counter_for_links = 0

api_url = "http://localhost:8000/receivedData"

# List of URLs for each region in the Czech Republic
links_cz = ["https://www.sreality.cz/hledani/prodej/byty/praha?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/stredocesky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/jihocesky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/plzensky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/karlovarsky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/ustecky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/liberecky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/kralovehradecky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/pardubicky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/vysocina-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/jihomoravsky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/zlinsky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/olomoucky-kraj?strana=",
            "https://www.sreality.cz/hledani/prodej/byty/moravskoslezsky-kraj?strana="]

# List of district names corresponding to the URLs
districts = ["Praha",
             "Středočeský kraj",
             "Jihočeský kraj",
             "Plzeňský kraj",
             "Karlovarský kraj",
             "Ústecký kraj",
             "Liberecký kraj",
             "Královéhradecký kraj",
             "Pardubický kraj",
             "Vysočina",
             "Jihomoravský kraj",
             "Zlínský kraj",
             "Olomoucký kraj",
             "Moravskoslezský kraj"]

# Counter for tracking properties
checking_counter_of_how_many_flats_have_been_tracked = 0


def get_range_of_estates(links_of_estates):
    """
    Determine the total number of pages available for a given region.

    This function fetches the total number of pages for a specific real estate listing
    by examining the pagination links.

    :param links_of_estates: URL of the real estate listing page
    :type links_of_estates: str
    :return: The maximum page number available for the given region plus 1
    :rtype: int
    """
    response = req.get(links_of_estates)
    received_data = bSoup(response.text, "html.parser")
    get_a_elements = received_data.find_all("a")
    processed_data = []
    holder = []
    for estate in get_a_elements:
        href = estate.get("href")
        if href and "strana" in href:
            processed_data.append(href)
    for data in processed_data:
        if "=" in data:
            holder.append(int(data.split("=")[1]))
    return max(holder) + 1


def get_list_of_estates(links_of_estates):
    """
    Extract individual property URLs from a listing page.

    This function retrieves all property detail URLs from a specific page of real estate listings.

    :param links_of_estates: URL of the real estate listing page
    :type links_of_estates: str
    :return: List of URLs for individual property details
    :rtype: list
    """
    response = req.get(links_of_estates)
    received_data = bSoup(response.text, "html.parser")
    get_a_elements = received_data.find_all("a")
    processed_data = []
    for estate in get_a_elements:
        href = estate.get("href")
        if href and "detail" in href:
            processed_data.append("https://www.sreality.cz" + href)
    return processed_data


def remove_spaces(string):
    """
    Remove all whitespace characters from a string.

    :param string: Input string to be processed
    :type string: str
    :return: String with all whitespace removed
    :rtype: str
    """
    cleaned = re.sub(r'\s+', '', string)
    return cleaned


def clean_string(string):
    """
    Remove special characters (zero-width space and non-breaking space) from a string.

    :param string: Input string to be cleaned
    :type string: str
    :return: Cleaned string
    :rtype: str
    """
    cleaned = re.sub(r'[\u200b\xa0]', '', string)
    return cleaned


def get_coordinates(address):
    """
    Get geographic coordinates (latitude, longitude) for a given address.

    :param address: Address to be geocoded
    :type address: str
    :return: Tuple containing latitude and longitude, or None if geocoding fails
    :rtype: tuple or None
    """
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None


def get_final_data_for_estate_to_database(link_of_estate):
    """
    Extract detailed information about a property from its detail page.

    This function scrapes all relevant information from a property's detail page
    and returns it as a dictionary.

    :param link_of_estate: URL of the property detail page
    :type link_of_estate: str
    :return: Dictionary containing all property details
    :rtype: dict
    """
    response = req.get(link_of_estate)
    received_data = bSoup(response.text, "html.parser")
    dictionary_data = {}
    name_of_estate = received_data.find("h1").text
    dictionary_data["Název"] = clean_string(name_of_estate)

    dt_elements = received_data.find_all('dt')
    dd_elements = received_data.find_all('dd')

    for dt, dd in zip(dt_elements, dd_elements):
        term = dt.get_text(strip=True)
        description = dd.get_text(strip=True)
        sub_items = [div.get_text(strip=True) for div in dd.find_all('div')]

        if sub_items:
            description = ', '.join(sub_items)

        dictionary_data[term] = clean_string(description)

    return dictionary_data


def get_district_by_postcode(psc):
    """
    Look up the district name based on a postal code.

    This function queries the MongoDB database to find the district corresponding
    to a given postal code.

    :param psc: Postal code to look up
    :type psc: str
    :return: Name of the district or error message
    :rtype: str
    """
    collection = db["Okresy"]
    result = collection.find_one({"psc": psc})

    if result:
        return result.get("okres", "Okres nenalezen")
    else:
        return "PSČ nenalezeno v databázi."


# Main execution block
while counter_for_links <= len(links_cz) - 1:
    """
    Main execution loop that processes each region in the Czech Republic.

    For each region, it:
    1. Determines the number of pages available
    2. Processes each page of listings
    3. Extracts detailed information for each property
    4. Adds geographic and postal code information
    5. Sends the data to an API endpoint
    """
    link_for_determination_of_length = links_cz[counter_for_links]
    link_for_determination_of_length += "1"
    range_of_database_for_region = get_range_of_estates(link_for_determination_of_length)
    counter_for_estates_in_region = 1

    while counter_for_estates_in_region <= range_of_database_for_region:
        current_link = links_cz[counter_for_links]
        current_link += str(counter_for_estates_in_region)
        list_of_estates = get_list_of_estates(current_link)

        counter_for_concrete_estates_in_region = 0
        if counter_for_concrete_estates_in_region == range_of_database_for_region:
            counter_for_links += 1

        while counter_for_concrete_estates_in_region <= len(list_of_estates) - 1:
            # Process each individual property
            final_data_of_property_to_database = get_final_data_for_estate_to_database(
                list_of_estates[counter_for_concrete_estates_in_region])

            # Handle price information
            if "Celková cena:" not in final_data_of_property_to_database:
                final_data_of_property_to_database["Celková cena:"] = "Cenanavyžádání"
            else:
                final_data_of_property_to_database["Celková cena:"] = remove_spaces(
                    final_data_of_property_to_database["Celková cena:"]).replace("Kč", "")

            # Add timestamp and property ID
            final_data_of_property_to_database["Čas"] = str(datetime.now())
            final_data_of_property_to_database["ID nemovitosti"] = \
            list_of_estates[counter_for_concrete_estates_in_region].split("/")[-1]

            # Extract address information
            address_of_property = final_data_of_property_to_database.get("Název", "")
            parts = address_of_property.split("²")

            # Extract number of rooms
            if len(final_data_of_property_to_database["Název"].split(" ")) > 2:
                number_of_rooms = final_data_of_property_to_database["Název"].split(" ")[2]
                final_data_of_property_to_database["Počet místností"] = number_of_rooms
            else:
                number_of_rooms = ""

            # Process address
            if len(parts) > 1:
                address_of_property = parts[1]
            else:
                address_of_property = ""

            # Handle address with street and city
            if "," in address_of_property:
                dictionary_of_address_of_property = {"Ulice": address_of_property.split(",")[0],
                                                     "Město": address_of_property.split(",")[1],
                                                     "Kraj": districts[counter_for_links]}
                final_data_of_property_to_database["Adresa"] = dictionary_of_address_of_property
                address = f"{dictionary_of_address_of_property['Ulice']},{dictionary_of_address_of_property['Město']}"
                time.sleep(1.3)
                coordinates = get_coordinates(address)
                time.sleep(1.3)

                logger.debug(coordinates)
                if coordinates is not None:
                    district = geolocator.reverse((coordinates[0], coordinates[1]), language="cs")
                    address = district.raw.get('address', {})
                    district_final = address.get('postcode', "PSČ nenalezeno").replace(" ", "")
                    final_data_of_property_to_database["Zeměpisná šířka"] = coordinates[0]
                    final_data_of_property_to_database["Zeměpisná délka"] = coordinates[1]
                    final_data_of_property_to_database["PSČ"] = district_final
                    final_data_of_property_to_database["Okres"] = get_district_by_postcode(district_final)
                else:
                    final_data_of_property_to_database["Zeměpisná šířka"] = None
                    final_data_of_property_to_database["Zeměpisná délka"] = None
                    final_data_of_property_to_database["PSČ"] = None
                    final_data_of_property_to_database["Okres"] = None

            # Handle address with only city
            else:
                dictionary_of_address_of_property = {"Město": address_of_property}
                final_data_of_property_to_database["Adresa"] = dictionary_of_address_of_property
                address = f"{dictionary_of_address_of_property['Město']}"
                time.sleep(1.3)
                coordinates = get_coordinates(address)
                time.sleep(1.3)

                logger.debug(coordinates)
                if coordinates is not None:
                    district = geolocator.reverse((coordinates[0], coordinates[1]), language="cs")
                    address = district.raw.get('address', {})
                    district_final = address.get('postcode', "PSČ nenalezeno").replace(" ", "")
                    final_data_of_property_to_database["Zeměpisná šířka"] = coordinates[0]
                    final_data_of_property_to_database["Zeměpisná délka"] = coordinates[1]
                    final_data_of_property_to_database["PSČ"] = district_final
                    final_data_of_property_to_database["Okres"] = get_district_by_postcode(district_final)
                else:
                    final_data_of_property_to_database["Zeměpisná šířka"] = None
                    final_data_of_property_to_database["Zeměpisná délka"] = None
                    final_data_of_property_to_database["PSČ"] = None
                    final_data_of_property_to_database["Okres"] = None

            # Extract building type
            type_of_materials = final_data_of_property_to_database["Stavba:"].split(",")[0]
            final_data_of_property_to_database["Typ stavby"] = type_of_materials

            # Extract flat size
            name = final_data_of_property_to_database.get("Název", "")
            parts = name.split(" ")
            # Extract apartment size in square meters
            if len(parts) > 3:
                flat_size = parts[3].split("²")[0].replace("m", "")
                final_data_of_property_to_database["Velikost bytu"] = flat_size
            else:
                final_data_of_property_to_database["Velikost bytu"] = ""

            # Prepare payload for API request
            payload = {
                "collection_name": districts[counter_for_links],
                "data_of_properties": final_data_of_property_to_database
            }
            logger.debug(f"Payload:{payload}")

            # Send data to API
            req.post(api_url, json=payload)

            # Log debug information
            logger.debug(districts[counter_for_links])
            logger.debug(type(districts[counter_for_links]))

            logger.debug(final_data_of_property_to_database)
            logger.debug(type(final_data_of_property_to_database))

            # Update counters
            counter_for_concrete_estates_in_region += 1
            checking_counter_of_how_many_flats_have_been_tracked += 1
            logger.debug(checking_counter_of_how_many_flats_have_been_tracked)

            # Move to next page when all properties on current page are processed
            if counter_for_concrete_estates_in_region == len(list_of_estates) - 1:
                counter_for_estates_in_region += 1


