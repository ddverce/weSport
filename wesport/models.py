from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from wesport import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    urole = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)
    clubs = db.relationship('Club', backref='club_user', lazy=True)
    player = db.relationship('Player', backref='player-user', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'u': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['u']
            return User.query.get(user_id)
        except:
            return None

    def __repr__(self):
        return "User(%s, %s, %s, %s)" % (self.username, self.email, self.urole, self.image_file)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        content = "Post(%s , %s)" % (self.title, self.date_posted)
        return content.encode("urf-8")


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    city = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    piva = db.Column(db.String(20), unique=True, nullable=False)
    subscription_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    field = db.relationship('Field', backref='club', lazy=True)

    def __repr__(self):
        return "User(%s, %s)" % (self.name, self.address)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    surname = db.Column(db.String(60), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(60), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    subscription_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "User(%s, %s, %s)" % (self.name, self.surname, self.subscription_date)


class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(20), unique=False, nullable=False)
    sport = db.Column(db.String(20), unique=False, nullable=False)
    max_people = db.Column(db.Integer, unique=False, nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)

    def __repr__(self):
        return "Field(%s, %s, %s)" % (self.club_id, self.field_name, self.sport)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False, unique=False)
    day = db.Column(db.DateTime, nullable=False)
    startTime = db.Column(db.Integer, nullable=False)
    endTime = db.Column(db.Integer, nullable=False)  # should be calculated with startTime and duration
    duration = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    player_list = db.relationship('Players', backref='Booking', lazy=True)

    # How Bookings are printed when the object is called
    def __repr__(self):
        return "Booking(%s, %s, %s)" % (self.owner, self.start_at, self.finish_at)


class Participants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking = db.Column(db.Integer, db.ForeignKey('booking.id'), primary_key=True)
    player = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
