from flask import Flask
import os
import logging

from app.utilities.utils import configure_logging


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates', instance_relative_config=True)
    app.config.update(
        SECRET_KEY=os.urandom(32),
        TEMPLATES_AUTO_RELOAD=True,  # 👈 Force template reload
        SEND_FILE_MAX_AGE_DEFAULT=0,  # 👈 Disable static file caching
        DEBUG=True  # 👈 Enable debug mode
    )


    configure_logging()
    logging.info("Application started")

    # registering the blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)
    logging.info("Blueprints registered")

    return app
