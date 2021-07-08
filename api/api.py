from flask import Flask
from mysql.connector import connect,errorcode,Error
import config

app = Flask('backend-test')

try:
  db_connection = connect(**config.db_config)
except Error as err:
  db_conn_error = err
  print(f"There was an error setting connection to DB: %s" % (err,))

@app.route("/", methods=["GET"])
def search_node_children(node_id, language, search_keyword, page_num, page_size):

# retrieve a single node from the db and build the class
def query_node(nodeid):
  if nodeid == None or nodeid < 0 :
    return None
  sql_query = "SELECT * FROM node_tree_names WHERE idNode = %s"
  # query usando db_connection
  node = Node() # buid node with query result
  
class Node():
    def __init__(id, level, left_child, right_child):
        _id = id
        _level = level
        _left_child = left_child
        _right_child = right_child
        _names = dict()

    def set_name(name, language):
        if not (language == 'english' or language == 'italian'):
            return
        _names[language] = name

    def get_json(language='english'):
        return {
            "node_id": _id,
            "name": _names[language]
          }
