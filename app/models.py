from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from .db import db

class User(db.Model):
    __tablename__ = 'User'

    userID = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    clients = db.relationship('Client', backref='user', passive_deletes=True)
    
    def set_password(self, password):
        self.password= generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Client(db.Model):
    __tablename__ = 'Client'

    clientID = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    userID = db.Column(
        db.Integer,
        db.ForeignKey('User.userID', ondelete='SET NULL')
    )

    hair_profiles = db.relationship('HairProfiles', backref='client', cascade='all, delete')
    
class HairProfiles(db.Model):
    __tablename__ = 'HairProfiles'

    profileID = db.Column(db.Integer, primary_key=True)

    clientID = db.Column(
        db.Integer,
        db.ForeignKey('Client.clientID', ondelete='CASCADE'),
        nullable=False
    )

    natural_colour = db.Column(db.String(50))
    current_colour = db.Column(db.String(50))
    texture = db.Column(db.String(50))
    porosity = db.Column(db.String(50))
    chem_history = db.Column(db.Text)

    dye_sessions = db.relationship('DyeSession', backref='profile', cascade='all, delete')
    
class DyeSession(db.Model):
    __tablename__ = 'DyeSession'

    session_id = db.Column(db.Integer, primary_key=True)

    profileID = db.Column(
        db.Integer,
        db.ForeignKey('HairProfiles.profileID', ondelete='CASCADE'),
        nullable=False
    )

    session_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    desired_shade = db.Column(db.String(50))
    developer_vol = db.Column(db.Integer)
    input_hair_pic_url = db.Column(db.Text)

    formulas = db.relationship('FormulaArchive', backref='session', cascade='all, delete')
    predictions = db.relationship('StrandPredictions', backref='session', cascade='all, delete')
    
class FormulaArchive(db.Model):
    __tablename__ = 'FormulaArchive'

    formulaID = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey('DyeSession.session_id', ondelete='CASCADE')
    )

    formula_name = db.Column(db.String(100))
    dye_brand = db.Column(db.String(100))
    developer_vol = db.Column(db.Integer)
    process_time = db.Column(db.Integer)

    saved_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())