from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, IntegerField, TimeField, SelectField, SelectMultipleField, widgets, TextAreaField
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
    country = StringField('Country of Origin',
                          validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')])
    phone_number = StringField('Phone',
                               validators=[DataRequired()])
    address = StringField('Address',
                          validators=[DataRequired()])
    birthdate = DateField('Birthdate', format='%Y-%m-%d',
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
    title = StringField('Name Your event',
                        validators=[DataRequired()])
    date = DateField('Select your Day', format='%Y-%m-%d',
                     validators=[DataRequired()])
    sport = SelectField('Sport', choices=[('0', '---select option---'), ('Football', 'Football'), ('Basketball', 'Basketball'), ('Volleyball', 'Volleyball'), ('Paddle', 'Paddle')])
    club = SelectField('Club', coerce=int, choices=[])
    field = SelectField('Field', coerce=int, choices=[])
    start_time = SelectField('Start time', coerce=int, choices=[(i, i) for i in range(9, 19)])
    duration = SelectField('Select duration', coerce=int, choices=[(i, i) for i in range(1, 6)])
    players = SelectMultipleField('Choose players for your event', coerce=int, choices=[], option_widget=widgets.CheckboxInput(),
                                  widget=widgets.ListWidget(prefix_label=False))
    submit = SubmitField('Book')


class CurrentAddressForm(FlaskForm):
    city = StringField('Your city',
                        validators=[DataRequired()])
    address = StringField('Your current address',
                          validators=[DataRequired()])
    submit = SubmitField('Find nearest clubs')


class PostForm(FlaskForm):
    content = TextAreaField('', validators=[DataRequired()])
    submit = SubmitField('Send')