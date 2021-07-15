import pytest
import json
import api



@pytest.fixture
def client():

    app = api.create_app()
    with app.test_client() as client:
        yield client

def test_empty_request(client):
    """A blank request without parameters should fails."""
    rv = client.get('/')
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Missing mandatory params" in json_rv['error']

def test_missing_params(client):
    """Missing mandatory parameters should make the request fail and return '400 BAD REQUEST'."""
    rv = client.get(f"/")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Missing mandatory params" in json_rv['error']

    node_id = 5
    rv = client.get(f"/?node_id={node_id}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Missing mandatory params" in json_rv['error']


    language = "italian"
    rv = client.get(f"/?language={language}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Missing mandatory params" in json_rv['error']

def test_invalid_paramters(client):
    """Invalid parameter should make the request fail and return '400 BAD REQUEST'."""
    # Invalid ID
    node_id = "dafe"
    language = "italian"
    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid node id" in json_rv['error']

    node_id = -1
    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid node id" in json_rv['error']


    # Invalid language but valid id
    node_id = 1
    language = "spanish"
    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid language requested" in json_rv['error']

    # Invalid page_num but valid id and language
    node_id = 1
    language = "english"
    page_num = -1
    rv = client.get(f"/?node_id={node_id}&language={language}&page_num={page_num}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid page number requested" in json_rv['error']

    page_num = "4e"
    rv = client.get(f"/?node_id={node_id}&language={language}&page_num={page_num}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid page number requested" in json_rv['error']

    # Invalid page_size but valid id and language
    node_id = 1
    language = "english"
    page_size = -1
    rv = client.get(f"/?node_id={node_id}&language={language}&page_size={page_size}")
    json_rv = rv.get_json()
    print(json_rv['error'])
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid page size requested" in json_rv['error']

    page_size = 10001
    rv = client.get(f"/?node_id={node_id}&language={language}&page_size={page_size}")
    json_rv = rv.get_json()
    assert json_rv['nodes'] == []
    assert '400' in rv.status
    assert "Invalid page size requested" in json_rv['error']

def test_correct_request(client):
    node_id = 1
    language = "italian"
    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert '200' in rv.status 
    assert len(json_rv['nodes']) == 0 # In test schema, only nodes 5 and 7 have children
    assert json_rv['error'] == ""

    node_id = 7
    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert '200' in rv.status 
    assert len(json_rv['nodes']) == 3 # In test schema, only nodes 5 and 7 have children
    assert json_rv['error'] == ""

    node_id = 5
    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert '200' in rv.status 
    assert len(json_rv['nodes']) == 8 # In test schema, only nodes 5 and 7 have children
    assert json_rv['error'] == ""


def test_not_exists(client):
    node_id = 56 # In test schema there are only ids from 1 to 13
    language = "italian"

    rv = client.get(f"/?node_id={node_id}&language={language}")
    json_rv = rv.get_json()
    assert '404' in rv.status 
    assert json_rv['nodes'] == []
    assert json_rv['error'] == "Invalid node id"


def test_search_keyword(client):
    """Search Keyword should restrict the nodes in the response"""
    node_id = 5 # In test schema there are only ids from 1 to 13
    language = "english"
    valid_keyword = "DEV"

    rv = client.get(f"/?node_id={node_id}&language={language}&search_keyword={valid_keyword}")
    json_rv = rv.get_json()
    assert '200' in rv.status
    assert len(json_rv['nodes']) == 1

    invalid_keyword = "afgfgd"
    rv = client.get(f"/?node_id={node_id}&language={language}&search_keyword={invalid_keyword}")
    json_rv = rv.get_json()
    assert '200' in rv.status
    assert len(json_rv['nodes']) == 0
