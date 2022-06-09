from flask import Flask
from flask_restx import Api
from .orders.views import order_namespace
from .auth.views import auth_namespace
from .config.config import config_dict
from .utils import db
from .models.users import User
from .models.orders import Order
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from werkzeug.exceptions import NotFound, MethodNotAllowed

# adding a comment


def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    authorizations = {
        "Bearer Auth": {
            'type': "apiKey",
            'in': 'header',
            'name': "Authorization",
            'description': "Add a JWT with ** Bearer &lt;JWT&gt; to authorize"
        }
    }

    db.init_app(app)
    jwt = JWTManager(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    migrate.init_app(app)
    jwt.init_app(app)
    api = Api(app,
              title="Pizza Delivery API",
              description="A REST API for a Pizza Delievry service",
              authorizations=authorizations,
              security="Bearer Auth"
              )
    api.add_namespace(order_namespace)
    api.add_namespace(auth_namespace, path='/auth')

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not Found"}, 404

    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "method not allowed"}, 405

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db,
                'User': User,
                'Order': Order}

    return app
