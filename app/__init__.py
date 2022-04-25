from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

app = Flask(__name__)

# getting a secret key
SECRET_KEY = os.urandom(32)
app.config["SECRET_KEY"] = SECRET_KEY

# Connection to the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
db = SQLAlchemy(app)

# connection to the login manager
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


bcrypt = Bcrypt(app)

from app import routes
