import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '39c2ba20fb1768239419357751008838'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'wesportpolito@gmail.com'
app.config['MAIL_PASSWORD'] = 'Wesport!'
mail = Mail(app)

from wesport.user.routes import users
from wesport.post.routes import posts
from wesport.main.routes import main
from wesport.testing.routes import test
from wesport.player.routes import player
from wesport.club.routes import club

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(test)
app.register_blueprint(player)
app.register_blueprint(club)



