from flask import Flask, current_app, g,request
from werkzeug.exceptions import HTTPException
from mysql.connector import connect, errorcode, Error
from enum import Enum
import json
import config

class Language(Enum):
    """Enum for supported languages by API."""
    italian="italian"
    english="english"

class Node():
    """Class that represents Node in result data and provide some helper functions.""" 
    def __init__(self, id, name, language, level=0):
        self._id = id
        self._name = name
        self._language = language
        self._level = level
        self._children_count = 0

    def count_children(self):
        """Count how many children there are for this node and update children_count field"""

        sql_query = ("SELECT COUNT(Child.idNode) " 
              "FROM node_tree as Child, node_tree as Parent " 
              "WHERE Child.iLeft > Parent.iLeft " 
              "AND Child.iRight < Parent.iRight " 
              "AND Parent.idNode = %s ")

        # Get count from the DB
        self._children_count = execute_query_on_db(sql_query, (self._id,), fetch_one=True)[0] # Only column in ROW is count

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
        db = connect(**config.db_config)
        # Set connection for the current request context
        if db:
            g.db = db
        return db
    else: 
        return g.db

def close_db(e=None):
    """Destroy DB connection for current request."""
    db = g.pop('db', None)

    if db is not None:
        db.close()

class NotFoundException(HTTPException):
    """Exception for node_id not present in database."""
    code = 404

class InvalidParameterException(HTTPException):
    """Exception for invalid parameters in request."""
    code = 400

class DBException(HTTPException):
    """Exception for problems with DB connection."""
    code = 500



def node_exists(node_id):
    """Check if there is node with id=node_id in the DB."""

    sql_query = ("SELECT Tree.idNode " \
          "FROM node_tree as Tree " 
          "WHERE Tree.idNode = %s")
    result_id = execute_query_on_db(sql_query, (node_id,), fetch_one=True)
    # Id is greater than 0
    return result_id != None

def check_required_params(request):
    """Check if required parameters are present, otherwise raise an exception"""
    if not request.args.get('node_id', None):
        raise InvalidParameterException(description="Missing mandatory params")
    if not request.args.get('language', None):
        raise InvalidParameterException(description="Missing mandatory params")

def validate_node_id(request):

    # Assume that check_required_params has been already called
    try:
        node_id = int(request.args.get('node_id', '')) 
    except:
        raise InvalidParameterException(description="Invalid node id")

    if node_id < 0 :
        raise InvalidParameterException(description="Invalid node id")

    return node_id

def validate_language(request):

    # Assume that check_required_params has been already called
    try:
        language = Language[request.args.get('language', '')]
    except:
        raise InvalidParameterException(description="Invalid language requested")
    return language

def validate_page_num(request):
    try:
        page_num = int(request.args.get('page_num', '0'))
    except: 
        raise InvalidParameterException(description="Invalid page number requested")

    if page_num < 0 :
        raise InvalidParameterException(description="Invalid page number requested")

    return page_num

def validate_page_size(request):
    try:
        page_size = int(request.args.get('page_size', '100'))
    except: 
        raise InvalidParameterException(description="Invalid page size requested")

    if page_size < 0 or page_size > 1000:
        raise InvalidParameterException(description="Invalid page size requested")
    return page_size

def execute_query_on_db(sql_query, args, fetch_one=False):
    cursor = get_db().cursor()
    try: 
        cursor.execute(sql_query, args)

        # Store query results before closing current cursor
        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()

        cursor.close()
    except Exception as err:
        raise DBException(description="There was an error with the database!")
    return result


# Define a Flask application factory
def create_app(test_config=None):
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
        # check mandatory parameters
        check_required_params(request)

        # validate input parameters
        # in case of invalid parameters, exception is handled by exception handler
        node_id = validate_node_id(request)
        language = validate_language(request)
        search_keyword = request.args.get('search_keyword', None)
        page_num = validate_page_num(request)
        page_size = validate_page_size(request)

        # No particular requirements for page_num and page_size
        
        if not node_exists(node_id) :
            raise NotFoundException(description=f"Invalid node id")
                

        # Execute query DB and build the result
        children_nodes = []
        sql_query = ("SELECT Child.idNode, node_tree_names.nodeName " \
              "FROM node_tree as Child, node_tree as Parent " 
              "INNER JOIN node_tree_names " 
              "WHERE node_tree_names.idNode = Child.idNode " 
              "AND Child.iLeft > Parent.iLeft "
              "AND Child.iRight < Parent.iRight " 
              "AND Child.level = Parent.level + 1 "
              "AND Parent.idNode = %s " 
              "AND node_tree_names.language = %s")
        query_result = execute_query_on_db(sql_query, (node_id, language.value))

        for (id, name) in query_result: 
            children_nodes.append(Node(id=id, name=name, language=language))

        # Count children for nodes in the result (requires new DB cursor)
        for node in children_nodes: 
            node.count_children()

        # filter result based on search_keyword
        if search_keyword: 
            children_nodes = [ child for child in children_nodes if search_keyword.lower() in child.get_name().lower() ]

        # select correct page for result
        # avoid case where page_num is bigger than actual size
        start_index = min(page_num * page_size, len(children_nodes))
        end_index = min((page_num+1) * page_size,len(children_nodes))
        children_nodes = children_nodes[start_index:end_index] 

        return {
                "nodes": [ json_node.to_json() for json_node in children_nodes],
                "error": ""
                }

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

    return app
