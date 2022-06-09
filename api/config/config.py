from datetime import timedelta
import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=90)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')


class DevConfig(Config):
    DEBUG = config('DEBUG', cast=bool)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + \
        os.path.join(BASE_DIR, 'db.sqlite3')
    FLASK_DEBUG = True


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    pass


config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}