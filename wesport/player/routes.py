from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player, Booking
from wesport.player.forms import PlayerRegistrationForm, BookingForm
from wesport.functions.users import save_picture, send_reset_email

player = Blueprint('player', __name__)


@player.route("/player_register", methods=['GET', 'POST'])
def player_register():
    if current_user.is_authenticated:
        if current_user.urole == "Club":
            return redirect(url_for('club.club_home'))
        else:
            return redirect(url_for('player.player_home'))
    form = PlayerRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, urole="Player")
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(email=form.email.data).first()
        player = Player(name=form.name.data, surname=form.surname.data, gender=form.gender.data,  phone_number=form.phone_number.data,
                        address=form.address.data, birthdate=form.birthdate.data, user_id=u.id)
        db.session.add(player)
        db.session.commit()
        flash('Your registration has been completed!', 'success')
        return redirect(url_for('main.login'))
    return render_template('player_register.html', title='Player Registration', form=form)


@player.route("/player_home")
def player_home():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
    player = Player.query.filter_by(user_id=current_user.id).first()
    return render_template('player_home.html', player=player)

'''
@player.route("/new_booking")
@login_required
def new_booking():
    if current_user.is_autenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
        form = BookingForm()
        booking = Booking.query.all()
        if form.validate_on_submit():
'''
