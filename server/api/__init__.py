import os

from flask import Flask, request
from flasgger import Swagger, swag_from
from flask_restful import Api, Resource, reqparse
# from flask_sqlalchemy import SQLAlchemy

from api.utils import helpers
# from flask_cors import CORS

# from flask_sslify import SSLify

app = Flask(__name__)
# CORS(app)
# SSLify(app)

# config_path = "./api/config/%s.json" % os.environ['PYTHON_ENV']  # set path to config

# if not os.path.isfile(config_path):  # check if file does not exist
#     print("PYTHON_ENV is invalid. Review the value and try again.")
#     exit(1)  # exit script with "issue" code

# helpers.create_env_variables(config_path)  # load settings from config file

# app = helpers.load_app_config(app)  # load application config

api = Api(app)
swagger = Swagger(app, template_file="./templates/schema.yml")
# db = SQLAlchemy(app)
