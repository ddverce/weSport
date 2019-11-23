from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player, Field
from wesport.club.forms import ClubRegistrationForm, AddFieldForm
from wesport.functions.users import save_picture, send_reset_email

club = Blueprint('club', __name__)


@club.route("/club_register", methods=['GET', 'POST'])
def club_register():
    if current_user.is_authenticated:
        if current_user.urole == "Player":
            return redirect(url_for('player.player_home'))
        else:
            return redirect(url_for('club.club_home'))
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
        return redirect(url_for('main.login'))
    return render_template('club_register.html', title='Club Registration', form=form)


@club.route("/club_home")
def club_home():
    if current_user.is_authenticated:
        if current_user.urole == 'Player':
            return redirect(url_for('player.player_home'))
    club = Club.query.filter_by(user_id=current_user.id).first()
    fields = Field.query.filter_by(club_id=club.id)
    return render_template('club_home.html', fields=fields)


@club.route("/add_field", methods=['GET', 'POST'])
@login_required
def add_field():
    if current_user.is_authenticated:
        if current_user.urole == "Player":
            return redirect(url_for('player.player_home'))
    form = AddFieldForm()
    if form.validate_on_submit():
        club = Club.query.filter_by(user_id=current_user.id).first()
        field = Field(field_name=form.field_name.data, sport=form.sport.data, max_people=form.max_people.data, club_id=club.id)
        db.session.add(field)
        db.session.commit()
        flash('Your field has been added!', 'success')
        return redirect(url_for('club.club_home'))
    return render_template('add_field.html', title='Add Field', form=form)
