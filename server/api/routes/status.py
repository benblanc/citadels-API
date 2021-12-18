from api import api, Resource, swag_from

from api.controllers.status import *


class Status(Resource):
    @swag_from('../templates/index.yml', endpoint='/status')
    def get(self):
        return get_status()


api.add_resource(Status, '/status')
