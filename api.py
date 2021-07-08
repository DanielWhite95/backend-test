from flask import Flask

app = Flask(__name__)

@app.route("/")
def root_node():
    return "<p>Root node</p>"

class Node():
    
