import os
import binascii
from PIL import Image
from flask import url_for
from flask_mail import Message
from wesport import app, mail
import unicodedata
import requests
import json


def save_picture(form_picture):
    random_hex = binascii.b2a_hex(os.urandom(8))
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # form_picture.save(picture_path)

    size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(size)
    i.save(picture_path)
    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender=app.config.get("MAIL_USERNAME"),
                  recipients=[user.email])
    msg.body = '''To reset your password, visit the following link: 
%s    

If you did not make this request, then simply ignore this email and non changes will be made

''' % url_for('main.reset_token', token=token, _external=True)
    mail.send(msg)


def send_cancellation_email(name, surname, field, date, start_time, receiver):  # to be checked the email
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore')
    surname = unicodedata.normalize('NFKD', surname).encode('ascii', 'ignore')
    field = unicodedata.normalize('NFKD', field).encode('ascii', 'ignore')
    start_time = str(start_time)
    receiver = unicodedata.normalize('NFKD', receiver).encode('ascii', 'ignore')
    msg = Message('Booking cancellation',
                  sender=app.config.get("MAIL_USERNAME"),
                  recipients=[receiver])
    msg.body = '''The user %s %s has just canceled a booking. the booking was made for %s the %s at %s

''' % (name, surname, field, date, start_time)
    print msg.body
    mail.send(msg)


def send_cancellation_email_club(club, field, date, start_time, receiver):  # to be checked the email
    club = unicodedata.normalize('NFKD', club).encode('ascii', 'ignore')
    field = unicodedata.normalize('NFKD', field).encode('ascii', 'ignore')
    start_time = str(start_time)
    receiver = unicodedata.normalize('NFKD', receiver).encode('ascii', 'ignore')
    msg = Message('Booking cancellation',
                  sender=app.config.get("MAIL_USERNAME"),
                  recipients=[receiver])
    msg.body = '''The user %s has just canceled a booking. the booking was made for %s the %s at %s

''' % (club, field, date, start_time)
    print msg.body
    mail.send(msg)


def get_city():
    try:
        access_key = '68ecc8eed3700d80beef22d1d4a527e8'
        send_url = 'http://api.ipstack.com/check?access_key='
        r = requests.get(send_url + access_key)
        j = json.loads(r.text)
        lat = j['latitude']
        lon = j['longitude']
    except:
        lat = 45.0734031
        lon = 7.5355232
    return lat, lon


a, b = get_city()


def geocode(address):  # needed for both saving the coordinates of the address and also to search the locations near me
    access_key = 'AIzaSyBCNB6dLAqToK9fbYsZKIHxreBLPGcn9so'
    send_url = 'https://maps.googleapis.com/maps/api/geocode/json?address='
    r = requests.get(send_url + address + '&key=' + access_key)
    j = json.loads(r.text)
    lat = j['results'][0]['geometry']['location']['lat']
    lng = j['results'][0]['geometry']['location']['lng']
    return lat, lng


addr = 'via washington 11, milano'

lat, lng = geocode(addr)