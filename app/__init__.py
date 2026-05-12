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