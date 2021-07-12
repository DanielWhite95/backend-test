from flask import Flask,current_app, g,request
from werkzeug.exceptions import HTTPException
from mysql.connector import connect,errorcode,Error
from enum import Enum
import json
import config

class Language(Enum):
    """Supported languages by API"""
    italian="italian"
    english="english"

class Node():
    def __init__(self, id, name, language, level=0):
        self._id = id
        self._name = name
        self._language = language
        self._level = level
        self._children_count = 0

    def count_children(self):
        """Count how many children there are for this node and update children_count field"""
        try:
            cursor = get_db().cursor()

            sql_query = ("SELECT COUNT(Child.idNode) " 
                  "FROM node_tree as Child, node_tree as Parent " 
                  "WHERE Child.iLeft > Parent.iLeft " 
                  "AND Child.iRight < Parent.iRight " 
                  "AND Parent.idNode = %s ")

            cursor.execute(sql_query, (self._id,))

            children_count = 0 
            # to fix and avoid for loop
            for (count,) in cursor: 
                children_count = count 

            cursor.close() 
        except  Exception as err: 
            print(err)
            raise DBException(description="There was an error with the database")

        self._children_count = children_count

    def get_name(self):
        return self._name

    def to_json(self):
        return json.dumps({
            "node_id": self._id,
            "language": self._language.value,
            "name": self._name,
            "children_count": self._children_count
            })


def get_db():
    """Returns connection to MySQL DB if present, otherwise initialize it and make it shared among requests"""
    if 'db' not in g:
        try:
            g.db = connect(**config.db_config)
            return g.db
        except Error as err:
            g.db_err = err
            print(f"There was an error setting connection to DB: ${err}")
            pass
    else: 
        return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

class InvalidParameter(HTTPException):
    """Exception for invalid parameters in request."""
    code = 400

class DBException(HTTPException):
    """Exception for problems with DB connection."""
    code = 500

# Initiate Flask application
app = Flask('backend-test')
app.teardown_appcontext(close_db)

@app.route('/', methods=['GET'])
def find_children_for_node():
    """The only endpoint of the program should accept only GET request with these parameters:
        - `node_id` (integer, required): the unique ID of the selected node.
        - `language` (enum, required): language identifier. Possible values: "english", "italian".
        - `search_keyword` (string, optional): a search term used to filter results. If provided, restricts
        the results to "all children nodes under `node_id` whose nodeName in the given language
        contains search_keyword (case insensitive)".
        - `page_num` (integer, optional): the 0-based identifier of the page to retrieve. If not
        provided, defaults to “0”.
        - `page_size` (integer, optional): the size of the page to retrieve, ranging from 0 to 1000. If
        not provided, defaults to “100”."""
    # validate input parameters
    try:
        node_id = int(request.args.get('node_id', '')) 
    except:
        raise InvalidParameter(description="node_id parameter is required")


    if node_id < 0 :
        raise InvalidParameter(description="Invalid node_id. Node ID must be  a number bigger than 0")

    try:
        language = Language[request.args.get('language', '')]
    except:
        raise InvalidParameter(description="Only 'english' and 'italian' languages are supported")
    print(language.value)
    search_keyword = request.args.get('search_keyword', '')

    # No particular requirements for page_num and page_size
    try:
        page_num = int(request.args.get('page_num', '0'))
        page_size = int(request.args.get('page_size', '100'))
    except: 
        raise InvalidParameter(description="page_num and page_size parameters should be numbers")

    # obtain DB Cursor for executing query  
    try: 
        cursor = get_db().cursor()

        sql_query = ("SELECT Child.idNode, node_tree_names.nodeName " \
              "FROM node_tree as Child, node_tree as Parent " 
              "INNER JOIN node_tree_names " 
              "WHERE node_tree_names.idNode = Child.idNode " 
              "AND Child.iLeft > Parent.iLeft "
              "AND Child.iRight < Parent.iRight " 
              "AND Parent.idNode = %s " 
              "AND node_tree_names.language = %s")
        cursor.execute(sql_query, (node_id, language.value))

        # Build result
        children_nodes = []
        for (id, name) in cursor: 
            children_nodes.append(Node(id=id, name=name, language=language))

        cursor.close()
    except Exception as err:
        print(err)
        raise DBException(description="There was an error with the database!")

    for node in children_nodes: 
        node.count_children()

    # filter result based on search_keyword
    children_nodes = [ child for child in children_nodes if child.get_name().find(search_keyword) != -1 ]

    # select correct page for result
    # avoid case where page_num is bigger than actual size
    start_index = min(page_num * page_size, len(children_nodes))
    end_index = min((page_num+1) * page_size,len(children_nodes))


    children_nodes = children_nodes[start_index:end_index] 

    return {
            "nodes": [ json_node.to_json() for json_node in children_nodes],
            "error": ""
            }


  # query usando db_connection    
  # node = Node(id,level,left_child, right_child) # buid node with query result

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "nodes": [],
        "error": e.description
    })
    response.status = e.code
    response.content_type = "application/json"
    return response

