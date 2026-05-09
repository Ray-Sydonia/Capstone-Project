import os
from dotenv import load_dotenv
from flask import current_app

load_dotenv()

class Config(object):
    DEBUG = False

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Som3$ec5etK*y')

    # Database (MySQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost/colour_chem_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads (local fallback if needed)
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')

    # ☁️ AWS S3 Config
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
    AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-1')

    # 📦 File Limits (important)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload
    
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_S3_REGION']
    )
    
