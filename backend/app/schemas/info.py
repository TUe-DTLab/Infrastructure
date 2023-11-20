from pydantic import BaseModel


class Info(BaseModel):
    version: str
    ontology_version: str
    ontology_base_url: str
