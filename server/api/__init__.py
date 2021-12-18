import os

from flask import Flask, request
from flasgger import Swagger, swag_from
from flask_restful import Api, Resource, reqparse
from flask_expects_json import expects_json

from api.utils import helpers

app = Flask(__name__)

api = Api(app)
swagger = Swagger(app, template_file="./templates/index.yml")
