from enum import Enum
from typing import Optional

from pydantic import BaseModel


class GeoType(Enum):
    D3Tiles = "3dtiles"
    WFS = "WFS"
    WMS = "WMS"
    WMTS = "WMTS"


class Geospatial(BaseModel):
    geoCRS: str
    geoLayerName: str
    geoName: str
    geoType: GeoType
    geoURL: str


class GeospatialUpdate(BaseModel):
    geoCRS: Optional[str]
    geoLayerName: Optional[str]
    geoName: Optional[str]
    geoType: Optional[GeoType]
    geoURL: Optional[str]
