from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, IntegerField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from wesport.models import User, Club, Player, Field, Booking


class PlayerRegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    name = StringField('Name',
                       validators=[DataRequired()])
    surname = StringField('Surname',
                          validators=[DataRequired()])
    gender = StringField('Gender',
                         validators=[DataRequired()])
    phone_number = StringField('Phone',
                               validators=[DataRequired()])
    address = StringField('Address',
                          validators=[DataRequired()])
    birthdate = DateField('Birthdate', format='%d-%m-%Y',
                          validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username is taken. Please choose another one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose another one')

    def validate_phone(self, phone_number):
        player = Player.query.filter_by(phone_number=phone_number.data).first()
        if player:
            raise ValidationError('That Phone is taken. Please choose another one')


class BookingForm(FlaskForm):
    day = DateField('Day',
                    validators=[DataRequired()])
    start_hour = TimeField('Start',
                           validators=[DataRequired()])
    field = StringField('Field',
                        validators=[DataRequired()])

    def validate_booking(self, day, start_hour, field):
        field = Field.query.filter_by(field_name=field).first
        booking = Booking.query.filter_by(field_id=field.id, day=day, start=start_hour).first()
        if booking:
            raise ValidationError('This Time has already been booked for this field. Please choose another one')
