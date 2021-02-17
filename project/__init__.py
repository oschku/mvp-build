# -*- coding: utf-8 -*-

"""Initialize app."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_session import Session
import sys
import config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
sess = Session()



def create_app():
    """Construct the core app object."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config.Config)

    # Initialize Plugins
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    sess.init_app(app)
    
    

    with app.app_context():
        from . import routes
        from . import auth
        from . import ui_input
        from .assets import compile_static_assets

        # Register Blueprints
        app.register_blueprint(routes.main_bp)
        app.register_blueprint(auth.auth_bp)
        app.register_blueprint(ui_input.valuation_bp)

        # Create Database Models
        db.create_all()

        # Compile static assets
        # if app.config['FLASK_ENV'] == 'development':
        #     compile_static_assets(app)

        return app


