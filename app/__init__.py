from flask import Flask
import os


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    SECRET_KEY = os.urandom(32)
    app.config['SECRET_KEY'] = SECRET_KEY

    # registering the blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
