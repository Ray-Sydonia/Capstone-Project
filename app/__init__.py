from flask import Flask
from .db import db
from .config import Config
from flask_login import LoginManager

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Rainbow%402004@localhost/colour_chem_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # required for flask-login

    db.init_app(app)
    login_manager.init_app(app)  # ← this was missing

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User
        return User.query.get(int(user_id))

    with app.app_context():
        from . import models
        from .views import main
        app.register_blueprint(main)
        db.create_all()

    return app