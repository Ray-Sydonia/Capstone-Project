from flask import Flask
from .db import db
from .config import Config
from flask_login import LoginManager
from flask_cors import CORS

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Rainbow%402004@localhost/colour_chem_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # required for flask-login

    db.init_app(app)
    login_manager.init_app(app)

    # CORS — add every URL you open the frontend from.
    # During development this is usually Live Server (port 5500) or just opening
    # the HTML file directly (file://). Add your Render/Railway URL here too once deployed.
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "null",                          # covers opening HTML files directly (file://)
        "https://your-app.onrender.com", # replace with your real Render URL when deployed
    ])

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