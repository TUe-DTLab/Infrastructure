from enum import Enum
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel


class ReferencePoint(BaseModel):
    height: float
    lat: float
    lon: float


class ReferencePointUpdate(BaseModel):
    height: Optional[float]
    lat: Optional[float]
    lon: Optional[float]


class GlobalCoordsECEF(BaseModel):
    x: float
    y: float
    z: float


class GlobalCoordsECEFUpdate(BaseModel):
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]


class GlobalCoordsWGS84(BaseModel):
    height: float
    lat: float
    lon: float


class GlobalCoordsWGS84Update(BaseModel):
    height: Optional[float]
    lat: Optional[float]
    lon: Optional[float]


GlobalCoords = Union[GlobalCoordsECEF, GlobalCoordsWGS84]
GlobalCoordsUpdate = Union[GlobalCoordsECEFUpdate, GlobalCoordsWGS84Update]


class LocalCoords(BaseModel):
    x: float
    y: float
    z: float
    referencePoint: UUID


class LocalCoordsUpdate(BaseModel):
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]
    referencePoint: Optional[UUID]


class Rotation(BaseModel):
    x: float
    y: float
    z: float


class RotationUpdate(BaseModel):
    x: Optional[float]
    y: Optional[float]
    z: Optional[float]


class GeometryType(Enum):
    glTF = "gltf"
    IFC = "ifc"
    URDF = "urdf"


class Geometry(BaseModel):
    name: str
    type: GeometryType
    globalCoords: UUID
    graphData: Optional[str]
    localCoords: UUID
    hasRotation: UUID


class GeometryUpdate(BaseModel):
    name: str
    type: GeometryType
    globalCoords: Optional[UUID]
    graphData: Optional[str]
    localCoords: Optional[UUID]
    hasRotation: Optional[UUID]
