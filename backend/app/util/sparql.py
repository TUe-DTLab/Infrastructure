from uuid import UUID

from SPARQLWrapper import BASIC, JSON, SPARQLWrapper

from app import models
from app.config import config


def graphdb_query(user: models.User, repo_id: str, query: str, response_type=JSON, write=False):
    """
    Returns the result of a query on a GraphDB repo
    """
    url = f"{config['GRAPHDB_URL']}/repositories/{str(repo_id)}"
    sparql = SPARQLWrapper(url + ("/statements" if write else ""))
    sparql.setHTTPAuth(BASIC)
    sparql.setCredentials(user=user.graphdb_username, passwd=user.graphdb_password)

    sparql.setQuery(query)
    sparql.setReturnFormat(response_type)

    if write:
        sparql.setMethod("POST")
    return sparql.query().convert()


def insert_edge(user: models.User, repo_id: str, obj: UUID, pred: str, sub: str, quotes=True):
    query = f"""
        PREFIX dtlab: <http://owl.dtlab.eaisi.tue.nl/0.2.0/digitaltwin#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        INSERT DATA
        {{
            dtlab:{obj} {pred} {'"' + sub + '"' if quotes else sub} .
        }}
    """

    results = graphdb_query(user=user, repo_id=repo_id, query=query, response_type=JSON, write=True)
    return results


def update_edge(user: models.User, repo_id: str, obj: UUID, pred: str, sub: str, quotes=True):
    query = f"""
        PREFIX dtlab: <http://owl.dtlab.eaisi.tue.nl/0.2.0/digitaltwin#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        DELETE {{
            dtlab:{obj} {pred} ?o .
        }}
        INSERT DATA {{
            dtlab:{obj} {pred} {'"' + sub + '"' if quotes else sub} .
        }}
        WHERE {{
            dtlab:{obj} {pred} ?o .
        }}
    """

    results = graphdb_query(user=user, repo_id=repo_id, query=query, response_type=JSON, write=True)
    return results


def delete_edge(user: models.User, repo_id: str, obj: UUID, pred: str, sub: str, quotes=True):
    query = f"""
        PREFIX dtlab: <http://owl.dtlab.eaisi.tue.nl/0.2.0/digitaltwin#>

        DELETE {{
            dtlab:{obj} {pred} {'"' + sub + '"' if quotes else sub} .
        }}
        WHERE {{
            dtlab:{obj} {pred} {'"' + sub + '"' if quotes else sub} .
        }}
    """

    results = graphdb_query(user=user, repo_id=repo_id, query=query, response_type=JSON, write=True)
    return results


def delete_node(user: models.User, repo_id: str, obj: UUID):
    # TODO: check if this works, there seem to be issues
    query = f"""
        PREFIX dtlab: <http://owl.dtlab.eaisi.tue.nl/0.2.0/digitaltwin#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

        DELETE {{
            dtlab:{obj} ?p1 ?o1 .
            ?s2 ?p2 dtlab:{obj} .
        }}
        WHERE {{
            dtlab:{obj} ?p1 ?o1 .
            ?s2 ?p2 dtlab:{obj} .
        }}
    """

    results = graphdb_query(user=user, repo_id=repo_id, query=query, response_type=JSON, write=False)
    return results


# # TODO: check all names using this function
# def sparql_sanitize(string: str):
#     bad_chars = ["?", "{", "}", "*", '"', "'", "#"]
#     return_string = "".join(i for i in string if i not in bad_chars)
#     return return_string
