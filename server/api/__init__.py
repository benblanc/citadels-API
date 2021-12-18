import os

from flask import Flask, request
from flasgger import Swagger, swag_from
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_expects_json import expects_json

from api.utils import helpers

app = Flask(__name__)

config_path = "./api/config/%s.json" % os.environ['PYTHON_ENV']  # set path to config

if not os.path.isfile(config_path):  # check if file does not exist
    print("PYTHON_ENV is invalid. Review the value and try again.")
    exit(1)  # exit script with "issue" code

helpers.create_environment_variables(config_path)  # load settings from config file

app = helpers.load_app_config(app)  # load application config

api = Api(app)
swagger = Swagger(app, template_file="./templates/index.yml")
db = SQLAlchemy(app)
