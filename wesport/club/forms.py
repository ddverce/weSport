from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from wesport.models import User, Club, Player


class ClubRegistrationForm(FlaskForm):
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
    phone_number = StringField('Phone',
                               validators=[DataRequired()])
    city = StringField('City',
                               validators=[DataRequired()])
    address = StringField('Address',
                          validators=[DataRequired()])
    piva = StringField('Partita Iva',
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

    def validate_name(self, name):
        club = Club.query.filter_by(name=name.data).first()
        if club:
            raise ValidationError('That Name is taken. Please choose another one')

    def validate_phone(self, phone_number):
        club = Club.query.filter_by(phone_number=phone_number.data).first()
        if club:
            raise ValidationError('That Phone is taken. Please choose another one')

    def validate_piva(self, piva):
        club = Club.query.filter_by(piva=piva.data).first()
        if club:
            raise ValidationError('That piva is taken. Please choose another one')


class AddFieldForm(FlaskForm):
    field_name = StringField('Field Name',
                             validators=[DataRequired(), Length(min=2, max=20)])
    sport = SelectField('Sport', choices=[('Football', 'Football'), ('Basketball', 'Basketball'), ('Volleyball', 'Volleyball'), ('Paddle', 'Paddle')])
    max_people = IntegerField('Max Number of Player',
                              validators=[DataRequired()])
    submit = SubmitField('AddField')
