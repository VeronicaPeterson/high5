from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os.path

#Initializes a Flask app and creates the SVN_Parser with the xml list and log. Used to populate index.html with the project_list
#Builds the DATABASE path to be used in querying the database
app = Flask(__name__)
app.config.from_object('config')
app_db = SQLAlchemy(app)
login_manager = LoginManager()

login_manager.init_app(app)
login_manager.login_view = 'login'

from app import views, models