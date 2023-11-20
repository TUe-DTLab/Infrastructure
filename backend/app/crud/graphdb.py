import base64
import time
from string import Template
from typing import Union
from uuid import UUID

import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import config


def get_federation_members(db: Session, user: models.User, project_id: UUID):
    credentials = "%s:%s" % (user.graphdb_username, user.graphdb_password)
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    current_json = requests.get(f"{config['GRAPHDB_URL']}/rest/repositories/{str(project_id)}", headers=headers).json()
    return current_json["params"]["member"]


def restart_repository(db: Session, user: models.User, project_id: UUID):
    credentials = "%s:%s" % (user.graphdb_username, user.graphdb_password)
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    return requests.post(f"{config['GRAPHDB_URL']}/rest/repositories/{str(project_id)}/restart", headers=headers)


def add_federation_member(
    db: Session,
    project_id: UUID,
    user: models.User,
    member: Union[schemas.ResolvableRepository, schemas.SPARQLEndpointWrite],
):
    credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    current_json = requests.get(f"{config['GRAPHDB_URL']}/rest/repositories/{str(project_id)}", headers=headers).json()

    # check if it is not already part of the federation
    for item in current_json["params"]["member"]["value"]:
        if member.store == "ResolvableRepository":
            if item.get("repositoryName", None) == member.repositoryName:
                raise HTTPException(
                    status_code=400, detail="A resolvable repository with that name is already in the federation."
                )
        elif member.store == "SPARQLEndpoint":
            if item.get("endpoint", None) == member.endpoint:
                raise HTTPException(
                    status_code=400, detail="A SPARQL endpoint with that url is already in the federation."
                )

    # add to config
    current_json["params"]["member"]["value"].append(member.dict())

    # update config
    new_json = requests.put(
        f"{config['GRAPHDB_URL']}/rest/repositories/{str(project_id)}",
        json=current_json,
        headers=headers,
    )

    return new_json


def remove_federation_member(db: Session, user: models.User, project_id: UUID, member: str):
    credentials = "%s:%s" % (user.graphdb_username, user.graphdb_password)
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    # get current config
    current_json = requests.get(f"{config['GRAPHDB_URL']}/rest/repositories/{str(project_id)}", headers=headers).json()

    # try to remove member
    try:
        current_json["params"]["member"]["value"].remove(member)
    except ValueError:
        raise HTTPException(status_code=404, detail="The supplied federation member does not exist in the federation.")

    # update config
    new_json = requests.put(
        f"{config['GRAPHDB_URL']}/rest/repositories/{str(project_id)}",
        json=current_json,
        headers=headers,
    )

    return new_json


def create_repository(db: Session, name: str, user: models.User, federation: bool = False):
    credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}

    graph_user = requests.get(
        f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", headers=headers
    ).json()
    graph_user["grantedAuthorities"].append("READ_REPO_" + name)
    graph_user["grantedAuthorities"].append("WRITE_REPO_" + name)
    del graph_user["password"]

    # create respository
    if federation:
        # create subrepo
        template = Template(open("repo-config.ttl", "r").read())
        template = template.substitute(
            {
                "repo_id": name + "-subrepo",
                "repo_label": name + "-subrepo",
                "graphdb_url": config["GRAPHDB_URL"],
            }
        )
        requests.post(
            f"{config['GRAPHDB_URL']}/rest/repositories",
            files={"config": ("repo-config.ttl", str.encode(template))},
            headers=headers,
        )

        # Upload ontology
        requests.post(
            f"{config['GRAPHDB_URL']}/rest/repositories/{name + '-subrepo'}/import/upload/url",
            json={
                "name": f"{config['ONTOLOGY_BASE_URL']}/{config['ONTOLOGY_VERSION_MAJOR']}.{config['ONTOLOGY_VERSION_MINOR']}.{config['ONTOLOGY_VERSION_PATCH']}/ontology.ttl",  # noqa: E501
                "status": "NONE",
                "message": "",
                "context": "",
                "replaceGraphs": [],
                "baseURI": None,
                "forceSerial": False,
                "type": "url",
                "format": "",
                "data": f"{config['ONTOLOGY_BASE_URL']}/{config['ONTOLOGY_VERSION_MAJOR']}.{config['ONTOLOGY_VERSION_MINOR']}.{config['ONTOLOGY_VERSION_PATCH']}/ontology.ttl",  # noqa: E501
                "timestamp": int(time.time()),
                "parserSettings": {
                    "preserveBNodeIds": False,
                    "failOnUnknownDataTypes": False,
                    "verifyDataTypeValues": False,
                    "normalizeDataTypeValues": False,
                    "failOnUnknownLanguageTags": False,
                    "verifyLanguageTags": False,
                    "normalizeLanguageTags": False,
                    "stopOnError": True,
                },
                "requestIdHeadersToForward": None,
            },
            headers=headers,
        )

        # create federated repo
        templateFedX = Template(open("fedx-config.ttl", "r").read())
        templateFedX = templateFedX.substitute(
            {
                "repo_id": name,
                "repo_label": name,
                "repo_members": f"""[fedx:repoType "graphdb"; fedx:repositoryName "{name}-subrepo";
                fedx:respectRights "true"; fedx:store "ResolvableRepository"; fedx:writable "true"]""",
            }
        )
        requests.post(
            f"{config['GRAPHDB_URL']}/rest/repositories",
            files={"config": ("repo-config.ttl", str.encode(templateFedX))},
            headers=headers,
        )

        graph_user["grantedAuthorities"].append("READ_REPO_" + name + "-subrepo")
        graph_user["grantedAuthorities"].append("WRITE_REPO_" + name + "-subrepo")
    else:
        template = Template(open("repo-config.ttl", "r").read())
        template = template.substitute(
            {
                "repo_id": name,
                "repo_label": name,
                "graphdb_url": config["GRAPHDB_URL"],
            }
        )
        requests.post(
            f"{config['GRAPHDB_URL']}/rest/repositories",
            files={"config": ("repo-config.ttl", str.encode(template))},
            headers=headers,
        )

        # Upload ontology
        requests.post(
            f"{config['GRAPHDB_URL']}/rest/repositories/{name}/import/upload/url",
            json={
                "name": f"{config['ONTOLOGY_BASE_URL']}/{config['ONTOLOGY_VERSION_MAJOR']}.{config['ONTOLOGY_VERSION_MINOR']}.{config['ONTOLOGY_VERSION_PATCH']}/ontology.ttl",  # noqa: E501
                "status": "NONE",
                "message": "",
                "context": "",
                "replaceGraphs": [],
                "baseURI": None,
                "forceSerial": False,
                "type": "url",
                "format": "",
                "data": f"{config['ONTOLOGY_BASE_URL']}/{config['ONTOLOGY_VERSION_MAJOR']}.{config['ONTOLOGY_VERSION_MINOR']}.{config['ONTOLOGY_VERSION_PATCH']}/ontology.ttl",  # noqa: E501
                "timestamp": int(time.time()),
                "parserSettings": {
                    "preserveBNodeIds": False,
                    "failOnUnknownDataTypes": False,
                    "verifyDataTypeValues": False,
                    "normalizeDataTypeValues": False,
                    "failOnUnknownLanguageTags": False,
                    "verifyLanguageTags": False,
                    "normalizeLanguageTags": False,
                    "stopOnError": True,
                },
                "requestIdHeadersToForward": None,
            },
            headers=headers,
        )

    # give user permissions
    requests.put(
        f"{config['GRAPHDB_URL']}/rest/security/users/{user.graphdb_username}", json=graph_user, headers=headers
    )


def delete_repository(db: Session, name: str):
    """
    Delete repository and repository user on graphdb and in database
    """

    credentials = "%s:%s" % (config["GRAPHDB_USER"], config["GRAPHDB_PASSWD"])
    headers = {"Authorization": "Basic %s" % base64.b64encode(credentials.encode("utf-8")).decode("utf-8")}
    result = requests.delete(
        f"{config['GRAPHDB_URL']}/rest/repositories/{name}",
        headers=headers,
    )
    return result
