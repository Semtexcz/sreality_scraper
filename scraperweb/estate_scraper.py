from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any

import pymongo
import requests as req
from bs4 import BeautifulSoup as bSoup
from geopy.geocoders import Nominatim
from loguru import logger

from scraperweb.config import get_settings


LINKS_CZ = [
    "https://www.sreality.cz/hledani/prodej/byty/praha?strana=",
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
    "https://www.sreality.cz/hledani/prodej/byty/moravskoslezsky-kraj?strana=",
]

DISTRICTS = [
    "Praha",
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
    "Moravskoslezský kraj",
]


def build_runtime() -> tuple[pymongo.database.Database, Nominatim, str]:
    settings = get_settings()
    client = pymongo.MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    geolocator = Nominatim(user_agent=settings.geopy_user_agent)
    return db, geolocator, settings.scraper_api_url


def get_range_of_estates(links_of_estates: str) -> int:
    response = req.get(links_of_estates, timeout=30)
    received_data = bSoup(response.text, "html.parser")
    page_numbers: list[int] = []
    for estate in received_data.find_all("a"):
        href = estate.get("href")
        if href and "strana" in href and "=" in href:
            try:
                page_numbers.append(int(href.split("=")[1]))
            except ValueError:
                continue
    return (max(page_numbers) if page_numbers else 1) + 1


def get_list_of_estates(links_of_estates: str) -> list[str]:
    response = req.get(links_of_estates, timeout=30)
    received_data = bSoup(response.text, "html.parser")
    estates: list[str] = []
    for estate in received_data.find_all("a"):
        href = estate.get("href")
        if href and "detail" in href:
            estates.append(f"https://www.sreality.cz{href}")
    return estates


def remove_spaces(value: str) -> str:
    return re.sub(r"\s+", "", value)


def clean_string(value: str) -> str:
    return re.sub(r"[\u200b\xa0]", "", value)


def get_coordinates(geolocator: Nominatim, address: str) -> tuple[float, float] | None:
    location = geolocator.geocode(address)
    if not location:
        return None
    return location.latitude, location.longitude


def get_final_data_for_estate_to_database(link_of_estate: str) -> dict[str, Any]:
    response = req.get(link_of_estate, timeout=30)
    received_data = bSoup(response.text, "html.parser")
    dictionary_data: dict[str, Any] = {}
    title = received_data.find("h1")
    dictionary_data["Název"] = clean_string(title.text) if title else ""

    dt_elements = received_data.find_all("dt")
    dd_elements = received_data.find_all("dd")

    for dt, dd in zip(dt_elements, dd_elements):
        term = dt.get_text(strip=True)
        description = dd.get_text(strip=True)
        sub_items = [div.get_text(strip=True) for div in dd.find_all("div")]
        if sub_items:
            description = ", ".join(sub_items)
        dictionary_data[term] = clean_string(description)

    return dictionary_data


def get_district_by_postcode(db: pymongo.database.Database, psc: str) -> str:
    collection = db["Okresy"]
    result = collection.find_one({"psc": psc})
    if result:
        return result.get("okres", "Okres nenalezen")
    return "PSČ nenalezeno v databázi."


def enrich_property_location(
    db: pymongo.database.Database,
    geolocator: Nominatim,
    property_data: dict[str, Any],
    district_name: str,
) -> None:
    address_of_property = property_data.get("Název", "")
    parts = address_of_property.split("²")

    if len(property_data["Název"].split(" ")) > 2:
        property_data["Počet místností"] = property_data["Název"].split(" ")[2]
    else:
        property_data["Počet místností"] = ""

    address_of_property = parts[1] if len(parts) > 1 else ""

    if "," in address_of_property:
        split_address = [part.strip() for part in address_of_property.split(",", maxsplit=1)]
        property_data["Adresa"] = {
            "Ulice": split_address[0],
            "Město": split_address[1],
            "Kraj": district_name,
        }
        address = f"{split_address[0]},{split_address[1]}"
    else:
        property_data["Adresa"] = {"Město": address_of_property.strip()}
        address = property_data["Adresa"]["Město"]

    time.sleep(1.3)
    coordinates = get_coordinates(geolocator, address)
    time.sleep(1.3)

    logger.debug(coordinates)
    if coordinates is None:
        property_data["Zeměpisná šířka"] = None
        property_data["Zeměpisná délka"] = None
        property_data["PSČ"] = None
        property_data["Okres"] = None
        return

    district = geolocator.reverse((coordinates[0], coordinates[1]), language="cs")
    address_data = district.raw.get("address", {}) if district else {}
    postcode = address_data.get("postcode", "PSČ nenalezeno").replace(" ", "")
    property_data["Zeměpisná šířka"] = coordinates[0]
    property_data["Zeměpisná délka"] = coordinates[1]
    property_data["PSČ"] = postcode
    property_data["Okres"] = get_district_by_postcode(db, postcode)


def process_estate(
    db: pymongo.database.Database,
    geolocator: Nominatim,
    api_url: str,
    district_index: int,
    estate_url: str,
) -> dict[str, Any]:
    property_data = get_final_data_for_estate_to_database(estate_url)

    if "Celková cena:" not in property_data:
        property_data["Celková cena:"] = "Cenanavyžádání"
    else:
        property_data["Celková cena:"] = remove_spaces(property_data["Celková cena:"]).replace("Kč", "")

    property_data["Čas"] = str(datetime.now())
    property_data["ID nemovitosti"] = estate_url.split("/")[-1]

    enrich_property_location(db, geolocator, property_data, DISTRICTS[district_index])

    building_state = property_data.get("Stavba:", "")
    property_data["Typ stavby"] = building_state.split(",")[0] if building_state else ""

    parts = property_data.get("Název", "").split(" ")
    if len(parts) > 3:
        property_data["Velikost bytu"] = parts[3].split("²")[0].replace("m", "")
    else:
        property_data["Velikost bytu"] = ""

    payload = {
        "collection_name": DISTRICTS[district_index],
        "data_of_properties": property_data,
    }
    logger.debug(f"Payload:{payload}")
    req.post(api_url, json=payload, timeout=30)
    logger.debug(property_data)
    return property_data


def run_scraper() -> int:
    db, geolocator, api_url = build_runtime()
    tracked_estates = 0

    for district_index, district_link in enumerate(LINKS_CZ):
        listing_range = get_range_of_estates(f"{district_link}1")
        for page_number in range(1, listing_range + 1):
            current_link = f"{district_link}{page_number}"
            estates = get_list_of_estates(current_link)
            for estate_url in estates:
                process_estate(db, geolocator, api_url, district_index, estate_url)
                tracked_estates += 1
                logger.debug(tracked_estates)

    logger.info(f"Processed {tracked_estates} estates.")
    return tracked_estates


def main() -> None:
    run_scraper()
