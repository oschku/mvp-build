# -*- coding: utf-8 -*-

"""Flask app configuration."""
from os import environ, path
from dotenv import load_dotenv
import os as os
import redis
from datetime import timedelta

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


osname = os.name




class Config:
    """Set Flask configuration from environment variables."""


    def get_env_variable(name):
        try:
            return os.environ[name]
        except KeyError:
            message = "Expected environment variable '{}' not set.".format(name)
            raise Exception(message)

    # POSTGRES 
    POSTGRES_URL = get_env_variable("POSTGRES_URL")
    POSTGRES_USER = get_env_variable("POSTGRES_USER")
    POSTGRES_PW = get_env_variable("POSTGRES_PW")
    POSTGRES_DB = get_env_variable("POSTGRES_DB")

    # Flask app
    FLASK_APP = get_env_variable('FLASK_APP')
    FLASK_ENV = get_env_variable('FLASK_ENV')
    SECRET_KEY = get_env_variable('SECRET_KEY')

    # Flask-SQLAlchemy
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Assets
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
    #LESS_BIN = environ.get('LESS_BIN')
    #ASSETS_DEBUG = environ.get('ASSETS_DEBUG')
    #LESS_RUN_IN_DEBUG = environ.get('LESS_RUN_IN_DEBUG')

    # Static Assets
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    #COMPRESSOR_DEBUG = environ.get('COMPRESSOR_DEBUG')

    # Pagination
    POSTS_PER_PAGE = 8

    # Flask-session
    SESSION_REDIS = redis.from_url(get_env_variable('SESSION_REDIS'))
    SESSION_TYPE = get_env_variable('SESSION_TYPE')

    # Work-directory
    # WORK_DIR = get_env_variable('WORK_DIR')
    if osname == 'nt':
        WORK_DIR = 'local'
    else:
        WORK_DIR = 'docker'