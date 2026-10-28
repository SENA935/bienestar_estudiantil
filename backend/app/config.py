import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    uri = os.environ.get('DATABASE_URL', 'mysql+pymysql://root:@localhost:3306/bienestar_estudiantil')
    if uri and uri.startswith('mysql://'):
        uri = uri.replace('mysql://', 'mysql+pymysql://', 1)
    if uri and uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql+psycopg2://', 1)
    if uri and uri.startswith('postgresql://') and '+psycopg' not in uri:
        uri = uri.replace('postgresql://', 'postgresql+psycopg2://', 1)
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JSON_AS_ASCII = False
