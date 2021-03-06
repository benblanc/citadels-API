import uuid, json, os, time

from datetime import datetime


def create_uuid():
    return str(uuid.uuid4())


def create_timestamp():
    return datetime.now()


def read_json(file_path):
    with open(file_path) as file:
        return json.load(file)


def create_environment_variables(file_path):
    settings = read_json(file_path)

    for key, value in settings.items():
        os.environ[key.upper()] = value


def load_app_config(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["DEBUG"] = False

    if os.environ['SQLALCHEMY_TRACK_MODIFICATIONS'] == 'true':
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    if os.environ['SQLALCHEMY_ECHO'] == 'true':
        app.config["SQLALCHEMY_ECHO"] = True

    if os.environ['DEBUG'] == 'true':
        app.config["DEBUG"] = True

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ['SQLALCHEMY_DATABASE_URI']
    app.config["SQLALCHEMY_POOL_RECYCLE"] = int(os.environ['SQLALCHEMY_POOL_RECYCLE'])  # expects integer
    app.config["SECRET_KEY"] = os.environ['SECRET_KEY']

    return app


def get_filtered_items(items, check_property, required_value, equals=True):
    response = []

    if items:  # check if list has items
        if isinstance(items[0], dict):  # check if item is a dictionary / json
            if equals:  # check if operator is equals
                response = list(filter(lambda item: item[check_property] == required_value, items))  # filter through items
            else:  # operator is not equals
                response = list(filter(lambda item: item[check_property] != required_value, items))  # filter through items

        else:  # item is from a class
            if equals:  # check if operator is equals
                response = list(filter(lambda item: item.__getattribute__(check_property) == required_value, items))  # filter through items
            else:  # operator is not equals
                response = list(filter(lambda item: item.__getattribute__(check_property) != required_value, items))  # filter through items

    return response


def get_filtered_item(items, check_property, required_value, equals=True):
    response = None

    filtered_items = get_filtered_items(items, check_property, required_value, equals)

    if filtered_items:  # check if there are items after filtering
        response = filtered_items[0]  # get the first filtered item

    return response
