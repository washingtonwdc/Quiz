from flask import Flask
from flask_pymongo import PyMongo
from flask_login import LoginManager
from app.config import Config
import os

mongo = PyMongo()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config.from_object(Config)
    
    mongo.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    from app.routes.main import main as main_blueprint
    from app.routes.auth import auth as auth_blueprint
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    return app
