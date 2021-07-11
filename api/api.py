from flask import Flask,current_app, g,request
from mysql.connector import connect,errorcode,Error
from flask import 
from flask.cli import with_appcontext
import config




def get_db():
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

# Initiate Flask application
app = Flask('backend-test')
app.config.from_mapping(
        SECRET_KEY='dev',
        )
app.teardown_appcontext(close_db)

# The only endpoint of the program
# should accept only GET request with these parameters:
# - `node_id` (integer, required): the unique ID of the selected node.
# - `language` (enum, required): language identifier. Possible values: "english", "italian".
# - `search_keyword` (string, optional): a search term used to filter results. If provided, restricts
# the results to "all children nodes under `node_id` whose nodeName in the given language
# contains search_keyword (case insensitive)".
# - `page_num` (integer, optional): the 0-based identifier of the page to retrieve. If not
# provided, defaults to “0”.
# - `page_size` (integer, optional): the size of the page to retrieve, ranging from 0 to 1000. If
# not provided, defaults to “100”.
@app.route('/', methods=['GET'])
def find_children_for_node():
    # validate input parameters
    try:
        node_id = int(request.args.get('node_id', '')) 
    except:
        return build_error_message("'node_id' parameter is required")


    if node_id < 0 :
        return build_error_message("Invalid node_id. Node ID must be  a number bigger than 0")

    language = request.args.get('language', '')
    if not (language == 'english' or language == 'italian'):
        return build_error_message("Only 'english' and 'italian' language are supported")

    search_keyword = request.args.get('search_keyword', '')
    # help function to filter out results
    filter_f = lambda x: (x['name'].find(search_keyword) != -1)
    page_num = int(request.args.get('page_num', '0'))
    page_size = int(request.args.get('page_size', '100'))

    # obtain DB Cursor for executing query  
    db = get_db()
    cursor = db.cursor()

    sql_query = ("SELECT Child.idNode, node_tree_names.nodeName " \
          "FROM node_tree as Child, node_tree as Parent " 
          "INNER JOIN node_tree_names " 
          "WHERE node_tree_names.idNode = Child.idNode " 
          "AND Child.iLeft > Parent.iLeft "
          "AND Child.iRight < Parent.iRight " 
          "AND Parent.idNode = %s " 
          "AND node_tree_names.language = %s")
    cursor.execute(sql_query, (node_id, language))

    # Build result
    children_nodes = []
    for (id, name) in cursor: 
        children_nodes.append({ "node_id": id, "name": name, "children_coutn": 0 })

    cursor.close()

    for node in children_nodes: 
        node['children_count'] = count_children(node['node_id'])

    # filter result based on search_keyword
    if search_keyword != '':
        children_results = filter(filter_f, children_results)

    # select correct page for result
    children_results = children_results[page_num * page_size:max((page_num+1) * page_size:len(children_results)] 


    return {
            "nodes": children_nodes,
            "error": ""
            }


  # query usando db_connection    
  # node = Node(id,level,left_child, right_child) # buid node with query result

# Function that uses an optimized query for counting how many children has a node
def count_children(nodeId):
    # Obtain DB Cursor for query
    cursor = get_db().cursor()

    sql_query = ("SELECT COUNT(Child.idNode) " 
          "FROM node_tree as Child, node_tree as Parent " 
          "WHERE Child.iLeft > Parent.iLeft " 
          "AND Child.iRight < Parent.iRight " 
          "AND Parent.idNode = %s ")

    cursor.execute(sql_query, (nodeId,))

    children_count = 0 
    # to fix and avoid for loop
    for (count,) in cursor: 
        children_count = count 

    cursor.close() 

    return children_count

def build_error_message(msg):
    return {
            "nodes": [],
            "error": msg
            }

# class Node():
#     def __init__(id, level, left_child, right_child):
#         _id = id
#         _level = level
#         _left_child = left_child
#         _right_child = right_child
#         _names = dict()
# 
#     def set_name(name, language):
#         if not (language == 'english' or language == 'italian'):
#             return
#         _names[language] = name
# 
#     def get_json(language='english'):
#         return {
#                 "node_id": _id,
#                 "name": _names[language]
#                 }
