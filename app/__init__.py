# app/__init__.py
from flask import Flask
from .db import db
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:K@ija1342@localhost/colour_chem_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        from . import models
        from . import views       
        db.create_all()

    return app