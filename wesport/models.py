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
        return "User(%s, %s, %s)" % (self.username, self.email, self.urole)


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    city = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    lat = db.Column(db.Float(10), nullable=False)
    lon = db.Column(db.Float(10), nullable=False)
    piva = db.Column(db.String(20), unique=True, nullable=False)
    subscription_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default_club.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    field = db.relationship('Field', backref='club_field', lazy=True)
    rating = db.relationship('ClubRate', backref='club_rate', lazy=True)

    def __repr__(self):
        return "Club(%s, %s)" % (self.name, self.address)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    surname = db.Column(db.String(60), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.String(60), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    subscription_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking = db.relationship('Booking', backref='booker', lazy=True)
    post = db.relationship('Post', backref='player_post', lazy=True)
    rating = db.relationship('PlayerRate', backref='player_rate', lazy=True)

    def __repr__(self):
        return "Player(%s, %s, %s)" % (self.name, self.surname, self.subscription_date)


class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    field_name = db.Column(db.String(20), unique=False, nullable=False)
    sport = db.Column(db.String(20), unique=False, nullable=False)
    max_people = db.Column(db.Integer, unique=False, nullable=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    booking = db.relationship('Booking', backref='field', lazy=True)

    def __repr__(self):
        club = Club.query.filter_by(id=self.club_id).first()
        return "Field(%s, %s, %s)" % (club.name, self.field_name, self.sport)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False, unique=False)
    date = db.Column(db.DateTime, nullable=False)
    startTime = db.Column(db.Integer, nullable=False)
    endTime = db.Column(db.Integer, nullable=False)  # should be calculated with startTime and duration
    duration = db.Column(db.Integer, nullable=False)
    booker_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('field.id'), nullable=False)
    post = db.relationship('Post', backref='booking', lazy=True)

    # How Bookings are printed when the object is called
    def __repr__(self):
        return "Booking(%s, %s, %s)" % (self.booker_id, self.startTime, self.endTime)


class Participants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking = db.Column(db.Integer, db.ForeignKey('booking.id'))
    player = db.Column(db.Integer, db.ForeignKey('player.id'))
    event = db.relationship('Booking', backref='booking', lazy=True)
    player_link = db.relationship('Player', backref='player', lazy=True)

    def __repr__(self):
        return "Participants(%s, %s)" % (self.booking, self.player)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    event = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)

    def __repr__(self):
        content = "Post(%s , %s)" % (self.title, self.date_posted)
        return content.encode("urf-8")


class ClubRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Integer, nullable=False)
    club = db.Column(db.Integer, db.ForeignKey('club.id'))
    player = db.Column(db.Integer, db.ForeignKey('player.id'))


class PlayerRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Integer, nullable=False)
    club = db.Column(db.Integer, db.ForeignKey('club.id'))
    player = db.Column(db.Integer, db.ForeignKey('player.id'))
