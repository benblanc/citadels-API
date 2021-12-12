import json, logging, traceback, time

from api import api, Resource, swag_from, reqparse, request

from api.controllers.cards import *


class Cards(Resource):
    @swag_from('../templates/schema.yml', endpoint='/cards')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('limit', type=int, help='return limited amount of ')
        parser.add_argument('offset', type=int, help='return  starting from this index position')
        args = parser.parse_args(strict=True)

        return get_cards(args['sort_order'], args['limit'], args['offset'])


class Districts(Resource):
    @swag_from('../templates/schema.yml', endpoint='/cards/districts')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('limit', type=int, help='return limited amount of ')
        parser.add_argument('offset', type=int, help='return  starting from this index position')
        args = parser.parse_args(strict=True)

        return get_districts(args['sort_order'], args['limit'], args['offset'])


class Characters(Resource):
    @swag_from('../templates/schema.yml', endpoint='/cards/characters')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('limit', type=int, help='return limited amount of ')
        parser.add_argument('offset', type=int, help='return  starting from this index position')
        args = parser.parse_args(strict=True)

        return get_characters(args['sort_order'], args['limit'], args['offset'])


api.add_resource(Cards, '/cards')
api.add_resource(Districts, '/cards/districts')
api.add_resource(Characters, '/cards/characters')
# api.add_resource(Card, '/card/<string:name>')
