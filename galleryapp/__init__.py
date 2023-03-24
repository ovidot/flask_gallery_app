from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__,instance_relative_config=True)
#load the config
app.config.from_pyfile('config.py',silent=False)

csrf = CSRFProtect(app)

db=SQLAlchemy(app)

#load the routes
from galleryapp import adminroute,userroute