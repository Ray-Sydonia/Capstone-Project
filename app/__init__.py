from flask import Flask
from .db import db
from .config import Config
from flask_login import LoginManager
from flask_cors import CORS

login_manager = LoginManager()
login_manager.login_view = 'main.login_page'
login_manager.login_message = ''

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
<<<<<<< HEAD
=======

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
>>>>>>> 213398c245056d4f040e9a84abe10eac797833e7

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