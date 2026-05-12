import os
from dotenv import load_dotenv
from sqlalchemy.engine import URL as SA_URL

load_dotenv()

class Config(object):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Som3$ec5etK*y')

    SQLALCHEMY_DATABASE_URI = SA_URL.create(
        drivername="mysql+pymysql",
        username="root",
        password=os.environ.get("DB_PASSWORD", "K@ija1342"),
        host="localhost",
        database="colour_chem_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-2')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
