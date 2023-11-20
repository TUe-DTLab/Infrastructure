from typing import List

from pydantic import BaseModel


class Head(BaseModel):
    vars: List[str]


class Results(BaseModel):
    bindings: list


class GraphDB(BaseModel):
    head: Head
    results: Results


class SPARQLEndpoint(BaseModel):
    store: str = "SPARQLEndpoint"
    supportsAskQueries: str
    writable: str = "false"
    endpoint: str


class SPARQLEndpointWrite(SPARQLEndpoint):
    username: str
    password: str


class ResolvableRepository(BaseModel):
    repoType: str = "graphdb"
    repositoryName: str
    respectRights: str = "true"
    store: str = "ResolvableRepository"
    writable: str = "true"
