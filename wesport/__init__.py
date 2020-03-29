import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '39c2ba20fb1768239419357751008838'  # app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/site.db'  # app configuration
db = SQLAlchemy(app)  # initialize db
bcrypt = Bcrypt(app)  # initialize bycript
login_manager = LoginManager(app)  # initialize the login manager
login_manager.login_view = 'main.login'  # set the route to redirect when you try to access to pages where login is required and you are not
login_manager.login_message_category = 'info'  # set the colour of the message of login
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'wesportpolito@gmail.com'
app.config['MAIL_PASSWORD'] = 'Wesport!'
mail = Mail(app)

from wesport.main.routes import main
from wesport.testing.routes import test
from wesport.player.routes import player
from wesport.club.routes import club


app.register_blueprint(main)
app.register_blueprint(test)
app.register_blueprint(player)
app.register_blueprint(club)



