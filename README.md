# Backend-Test
This program solves the test for organizational charts.
The program is develeoped using Python 3.7.3 and Flask 2.0 but should be compatible with Python 3.x
The only dependencies are Flask 2.0 and mysql-connector-plugin. All requirements can be installed with the command
```pip install -r api/requirements```

A simple MYSQL db test can be created using the SQL scripts *db/tables.sql* and *db/data.sql*. 
*db/tables.sql* **must** be executed before *db/data.sql*

To start the application, run the following command from the api sub-directory:
```FLASK_APP=api flask run --host=0.0.0.0```

# Configuration
Configuration parameters for DB connection can be set in the *api/config.py* file. These are the parameters
passed to the *connect()* of mysql-connector-plugin, so please follow their specification about the supported options


# Docker 
A *Dockerfile* is provided with API server to build a test container and quickly use the API.
In additon, a Docker Compose specification (*docker-compose.yml*) is provided for deploying a simple test environment 
with a DB and an API server.
In order to use docker-compose you have to modify *config.py* and set host to 'db', to have a proper connection between DB and API containers

To build and start  the test environment, run the following commands:
1. ```docker-compose build```
2. ```docker-compose up```

