from api import api, Resource, swag_from, reqparse

from api.controllers._cards import *


class Districts(Resource):
    @swag_from('../templates/index.yml', endpoint='/cards/districts')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('order_by', type=str, help='order by given value')
        parser.add_argument('limit', type=int, help='return limited amount of items, 0 to return all items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_districts(args['sort_order'], args['order_by'], args['limit'], args['offset'])


class District(Resource):
    @swag_from('../templates/index.yml', endpoint='/cards/district/{name}')
    def get(self, name):
        return get_district(str(name))


class Characters(Resource):
    @swag_from('../templates/index.yml', endpoint='/cards/characters')
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('sort_order', type=str, help='sort order')
        parser.add_argument('order_by', type=str, help='order by given value')
        parser.add_argument('limit', type=int, help='return limited amount of items, 0 to return all items')
        parser.add_argument('offset', type=int, help='return items starting from this index position')
        args = parser.parse_args(strict=True)

        return get_characters(args['sort_order'], args['order_by'], args['limit'], args['offset'])


class Character(Resource):
    @swag_from('../templates/index.yml', endpoint='/cards/character/{name}')
    def get(self, name):
        return get_character(str(name))


api.add_resource(Districts, '/cards/districts')
api.add_resource(District, '/cards/districts/<string:name>')
api.add_resource(Characters, '/cards/characters')
api.add_resource(Character, '/cards/characters/<string:name>')
