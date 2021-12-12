import api.responses as responses

from api import api, Resource, swag_from, reqparse, request

from api.controllers.status import *

from api.utils import helpers


class Status(Resource):
    @swag_from('../templates/schema.yml', endpoint='/status')
    def get(self):
        return get_status()


api.add_resource(Status, '/status')
