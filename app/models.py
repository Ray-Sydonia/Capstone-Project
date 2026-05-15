from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from .db import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    avatar_key = db.Column(db.String(255), nullable=True)

    clients = db.relationship('Client', backref='user', passive_deletes=True)
    
    @property
    def id(self):
        return self.userID
    
    def set_password(self, password):
        self.password= generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
class Client(db.Model):
    __tablename__ = 'client'

    clientID = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    allergies = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text,        nullable=True)


    userID = db.Column(
        db.Integer,
        db.ForeignKey('user.userID', ondelete='SET NULL')
    )

    hair_profiles = db.relationship('HairProfiles', backref='client', cascade='all, delete')
    
class HairProfiles(db.Model):
    __tablename__ = 'hairprofiles'

    profileID = db.Column(db.Integer, primary_key=True)

    clientID = db.Column(
        db.Integer,
        db.ForeignKey('client.clientID', ondelete='CASCADE'),
        nullable=False
    )

    natural_colour = db.Column(db.String(50))
    current_colour = db.Column(db.String(50))
    texture = db.Column(db.String(50))
    porosity = db.Column(db.String(50))
    chem_history = db.Column(db.Text)

    dye_sessions = db.relationship('DyeSession', backref='profile', cascade='all, delete')
    
class DyeSession(db.Model):
    __tablename__ = 'dyesession'

    session_id = db.Column(db.Integer, primary_key=True)

    profileID = db.Column(
        db.Integer,
        db.ForeignKey('hairprofiles.profileID', ondelete='CASCADE'),
        nullable=False
    )

    session_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    desired_shade = db.Column(db.String(50))
    developer_vol = db.Column(db.Integer)
    input_hair_pic_url = db.Column(db.Text)
    after_hair_pic_url = db.Column(db.Text)          
    slvl = db.Column(db.Integer)        # starting level
    tlvl = db.Column(db.Integer)        # target level
    outcome = db.Column(db.String(100))    # AI feedback outcome
    notes = db.Column(db.Text)           # feedback notes
    stars = db.Column(db.Integer, default=0)  # client satisfaction

    formulas = db.relationship('FormulaArchive', backref='session', cascade='all, delete')
    predictions = db.relationship('StrandPredictions', backref='session', cascade='all, delete')
    
class FormulaArchive(db.Model):
    __tablename__ = "formulaarchive"

    formulaID    = db.Column(db.Integer, primary_key=True)
    session_id   = db.Column(db.Integer, db.ForeignKey('dyesession.session_id', ondelete='CASCADE'))

    formula_name  = db.Column(db.String(100))
    dye_brand     = db.Column(db.String(100))
    developer_vol = db.Column(db.Integer)
    process_time  = db.Column(db.Integer)

    # New fields
    mode          = db.Column(db.String(20))   # 'natural' or 'fashion'
    current_level = db.Column(db.Integer)
    target_level  = db.Column(db.Integer)
    shade         = db.Column(db.String(50))
    texture       = db.Column(db.String(50))
    porosity      = db.Column(db.String(50))
    damage_score  = db.Column(db.Integer)
    notes         = db.Column(db.Text)         # packed detail string for fashion

    saved_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
class StrandPredictions(db.Model):
    __tablename__ = 'strandpredictions'

    predictionID = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(
        db.Integer,
        db.ForeignKey('dyesession.session_id', ondelete='CASCADE')
    )

    predicted_colour = db.Column(db.String(50))
    damage_risk = db.Column(db.String(50))
    damage_score = db.Column(db.Float)
    process_time = db.Column(db.Integer)
    success_rate = db.Column(db.Float)
    test_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    output_hair_pic_url = db.Column(db.Text)