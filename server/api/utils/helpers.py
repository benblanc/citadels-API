import uuid, json, os, time


def create_uuid():
    return str(uuid.uuid4())


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
