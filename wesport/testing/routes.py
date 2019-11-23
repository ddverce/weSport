from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player
from wesport.testing.forms import (RegistrationForm, PlayerRegistrationForm, ClubRegistrationForm, LoginForm, CLubForm, UpdateAccountForm, UpdateClubForm, UpdatePlayerForm)
from wesport.functions.users import save_picture, send_reset_email

test = Blueprint('test', __name__)

'''
# deprecated
@test.route("/test_register", methods=['GET', 'POST'])
def test_register():
    if current_user.is_authenticated:
        if current_user.urole.data == "Club":
            return redirect(url_for('test.club_home'))
        else:
            return redirect(url_for('test.player_home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, urole=form.urole.data)
        db.session.add(user)
        db.session.commit()
        flash('Almost done! Fill in this module to complete the registration.', 'success')
        if form.urole.data == "Club":
            return redirect(url_for('test.club_register'))
        else:
            return redirect(url_for('test.player_register'))
    return render_template('testregister.html', title='Registration', form=form)


@test.route("/club_register", methods=['GET', 'POST'])
def club_register():
    if current_user.is_authenticated:
        if current_user.urole.data == "Player":
            return redirect(url_for('test.player_home'))
        else:
            return redirect(url_for('test.player_home'))
    form = ClubRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, urole="Club")
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(email=form.email.data).first()
        club = Club(name=form.name.data, phone_number=form.phone_number.data, address=form.address.data, piva=form.piva.data, city=form.city.data, user_id=u.id)
        db.session.add(club)
        db.session.commit()
        flash('Your registration has been completed!', 'success')
        return redirect(url_for('test.club_home'))
    return render_template('club_register.html', title='Club Registration', form=form)


@test.route("/player_register", methods=['GET', 'POST'])
def player_register():
    if current_user.is_authenticated:
        if current_user.urole.data == "Club":
            return redirect(url_for('club.home'))
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
        return redirect(url_for('test.player_home'))
    return render_template('player_register.html', title='Player Registration', form=form)


@test.route("/test_login", methods=['GET', 'POST'])
def test_login():
    if current_user.is_authenticated:
        if current_user.urole.data == "Club":
            return redirect(url_for('test.club_home'))
        else:
            return redirect(url_for('test.player_home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if current_user.is_authenticated:
                if user.urole == "Club":
                    return redirect(next_page) if next_page else redirect(url_for('test.club_home'))
                else:
                    return redirect(next_page) if next_page else redirect(url_for('test.player_home'))
        else:
            flash('Login unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@test.route("/test_logout")
def test_logout():
    logout_user()
    return redirect(url_for('main.home'))
'''


@test.route("/test_club_account", methods=['GET'])
@login_required
def test_club_account():
    if current_user.urole == 'Player':
        return redirect(url_for('test.player_home'))
    form = CLubForm()
    club = Club.query.filter_by(user_id=current_user.id).first()
    form.name.data = club.name
    form.phone_number.data = club.phone_number
    form.address.data = club.address
    return render_template('testclubaccount.html', title='Club %s', form=form) % club.name


@test.route("/test_update_account", methods=['GET', 'POST'])
@login_required
def test_update_account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

'''
@test.route("/club_home")
def club_home():
    return render_template('layout.html')


@test.route("/player_home")
def player_home():
    return render_template('layout.html')
'''