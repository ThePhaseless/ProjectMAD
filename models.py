import re
from contextlib import suppress
from datetime import date, datetime
from math import atan2, cos, radians, sin, sqrt
from typing import Any

from pydantic import BaseModel, Field


class DetailedInformation(BaseModel):
    label: str
    icon: str | None = None
    value: str
    url: str | None = None


class Company(BaseModel):
    address: list[str]
    faxes: list[Any]
    name: str
    phones: list[str]
    type: str


class Person(BaseModel):
    faxes: list[Any]
    name: str
    phones: list[int]
    photo: str | None = None
    type: str


class Contact(BaseModel):
    company: Company
    contact_comment: list[Any] = Field(alias="contactComment")
    person: Person


class EnvironmentalDatum(BaseModel):
    data_type: str = Field(alias="dataType")
    description: str
    value: str


class Facility(BaseModel):
    icon: str
    label: str


class GeographicPoint(BaseModel):
    latitude: float
    longitude: float


class Map(BaseModel):
    center: GeographicPoint


class Location(BaseModel):
    map: Map


class OfferDetailedInformation(BaseModel):
    label: str
    value: str


class Price(BaseModel):
    amount: str
    currency: str


class Types(BaseModel):
    primary_type: str = Field(alias="primaryType")
    primary_type_root: str = Field(alias="primaryTypeRoot")
    main_type: str = Field(alias="mainType")
    main_type_root: str = Field(alias="mainTypeRoot")


class PropertyData(BaseModel):
    area: str
    building_detailed_information: list[DetailedInformation] = Field(
        alias="buildingDetailedInformation"
    )
    detailed_information: list[DetailedInformation] = Field(alias="detailedInformation")
    environmental_data: list[EnvironmentalDatum] = Field(alias="environmentalData")
    equipments: list[Any]
    facilities: list[Facility]
    floor_formatted: str = Field(alias="floorFormatted")
    location: Location
    market_type: str = Field(alias="marketType")
    offer_detailed_information: list[OfferDetailedInformation] = Field(
        alias="offerDetailedInformation"
    )
    presentation_type: str = Field(alias="presentationType")
    price: Price
    price_m2: Price = Field(alias="priceM2")
    transaction: str
    types: Types
    url: str


metro_locations_raw = [
    "52 16 08,5 N 20 59 04,8 E",
    "52 07 52 N 21 03 58 E",
    "52 08 27 N 21 03 23 E",
    "52 08 57 N 21 02 47 E",
    "52 09 22 N 21 02 05 E",
    "52 09 43 N 21 01 40 E",
    "52 10 22 N 21 01 35 E",
    "52 10 53 N 21 01 23 E",
    "52 11 23 N 21 01 00 E",
    "52 11 55 N 21 00 44 E",
    "52 12 31 N 21 00 28 E",
    "52 13 05 N 21 00 55 E",
    "52 13 31 N 21 00 51 E",
    "52 13 49,88 N 21 00 38,73 E",
    "52 14 07 N 21 00 30 E",
    "52 14 41 N 21 00 02 E",
    "52 15 00 N 20 59 56 E",
    "52 15 28 N 20 59 40 E",
    "52 16 08,5 N 20 59 04,8 E",
    "52 16 18 N 20 58 18 E",
    "52 16 35 N 20 57 41 E",
    "52 16 55 N 20 56 58 E",
    "52 17 11 N 20 56 22 E",
    "52 17 28 N 20 55 44 E",
    "52 14 19,43 N 20 54 37,12 E",
    "52 14 25,55 N 20 55 48,47 E",
    "52 14 20,8 N 20 56 39,1 E",
    "52 14 15,7 N 20 57 35,6 E",
    "52 13 53,9026 N 20 58 01,3393 E",
    "52 13 48 N 20 58 59 E",
    "52 13 59 N 20 59 54 E",
    "52 14 12 N 21 00 59 E",
    "52 14 24 N 21 01 53 E",
    "52 14 47 N 21 02 35 E",
    "52 15 15 N 21 02 07 E",
    "52 15 47,5 N 21 02 42,4 E",
    "52 16 08,9 N 21 03 03,9 E",
    "52 16 31,537 N 21 03 20,736 E",
    "52 17 01,72 N 21 03 43,63 E",
    "52 17 31,20 N 21 02 55,10 E",
    "52 17 36,53 N 21 01 46,31 E",
]


def dms_to_decimal(
    degrees: float, minutes: float, seconds: float, direction: str
) -> float:
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ("S", "W"):
        decimal *= -1
    return decimal


def parse_coordinates(coord_str: str) -> GeographicPoint:
    pattern = re.compile(
        r"(\d+,?\d*) (\d+,?\d*) (\d+,?\d*) ([NS]) (\d+,?\d*) (\d+,?\d*) (\d+,?\d*) ([EW])"
    )
    match = pattern.match(coord_str)

    if not match:
        raise ValueError("Invalid coordinate format")

    lat_deg, lat_min, lat_sec, lat_dir, lon_deg, lon_min, lon_sec, lon_dir = (
        match.groups()
    )

    latitude = dms_to_decimal(
        float(lat_deg.replace(",", ".")),
        float(lat_min.replace(",", ".")),
        float(lat_sec.replace(",", ".")),
        lat_dir,
    )
    longitude = dms_to_decimal(
        float(lon_deg.replace(",", ".")),
        float(lon_min.replace(",", ".")),
        float(lon_sec.replace(",", ".")),
        lon_dir,
    )

    return GeographicPoint(latitude=latitude, longitude=longitude)


def haversine_distance(center1: GeographicPoint, center2: GeographicPoint) -> float:
    R = 6371000  # Radius of Earth in meters

    lat1, lon1 = radians(center1.latitude), radians(center1.longitude)
    lat2, lon2 = radians(center2.latitude), radians(center2.longitude)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


metro_locations = [parse_coordinates(loc) for loc in metro_locations_raw]


class ReturnData(BaseModel):
    area: float = 0
    location: GeographicPoint
    distance_to_metro: float = 0
    build_year: int | None = None
    has_parking: bool = False
    floor: int | None = None
    is_new: bool = False
    price: float = 0
    price_m2: float = Field(alias="priceM2", default=0)
    date_added: date | None = None

    @classmethod
    def from_property_data(cls, property_data: PropertyData):
        new = cls(
            **{
                **property_data.model_dump(),
                "area": float(property_data.area.replace(",", ".").replace("\xa0", "")),
                "price": float(property_data.price.amount),
                "location": property_data.location.map.center,
            }
        )
        with suppress(StopIteration):
            new.build_year = next(
                int(info.value)
                for info in property_data.building_detailed_information
                if info.label == "Rok budowy"
            )

        new.has_parking = any(
            info.icon == "parking_places" for info in property_data.facilities
        )
        floor_str = property_data.floor_formatted.split("/")[0]
        new.floor = 0 if floor_str == "parter" else int(floor_str.split()[-1])
        new.distance_to_metro = min(
            haversine_distance(property_data.location.map.center, metro)
            for metro in metro_locations
        )
        with suppress(StopIteration):
            new.date_added = datetime.strptime(  # noqa: DTZ007
                next(
                    info.value
                    for info in property_data.detailed_information
                    if info.label == "Data dodania"
                ),
                "%d.%m.%Y",
            ).date()

        new.is_new = property_data.market_type != "Rynek wt\u00f3rny"
        new.price = float(property_data.price.amount)
        new.price_m2 = float(property_data.price_m2.amount)
        return new
