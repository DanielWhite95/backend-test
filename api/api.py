from flask import Flask
from mysql.connector import connect,errorcode
import config.py

app = Flask('backend-test')

try
  db_connection = mysql.connector.connect(**db_config)
except mysql.connector.Error as err:
  db_conn_error = err
  print(f"There was an error setting connection to DB: %s" % (err,))

@app.route("/")
def search_node_children(node_id, language, search_keyword, page_num, page_size):
    if db_conn_error:
        resp_error
    if node_id == None or language == None:
        resp_error = "Missing required arguments"
    
    return "<p>Root node</p>"

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

