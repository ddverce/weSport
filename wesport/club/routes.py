from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player, Field, Booking, Participants
from wesport.club.forms import ClubRegistrationForm, AddFieldForm
from wesport.functions.users import save_picture, send_reset_email, send_cancellation_email_club, geocode
from datetime import datetime

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
        lat, lon = geocode(form.address.data + ',' + form.city.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, urole="Club")
        db.session.add(user)
        db.session.commit()
        u = User.query.filter_by(email=form.email.data).first()
        club = Club(name=form.name.data, phone_number=form.phone_number.data, address=form.address.data, lat=lat, lon=lon, piva=form.piva.data, city=form.city.data, user_id=u.id)
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
    bookings = Booking.query.join(Field, Booking.field_id==Field.id).join(User, Booking.booker_id == User.id).join(Player, User.id == Player.user_id)\
        .add_columns(Booking.id, Booking.title, Booking.date, Booking.startTime, Booking.endTime, Field.club_id, Field.field_name, Player.name)\
        .filter(Field.club_id == club.id)\
        .filter(Booking.date > datetime.now()).all()
    image_file = url_for('static', filename='profile_pics/' + club.image_file)
    return render_template('club_home.html', fields=fields, bookings=bookings, image_file=image_file, club=club)


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


@club.route("/myfield/<int:field_id>")
@login_required
def myfield(field_id):
    field = Field.query.get_or_404(field_id)
    print field
    return render_template('field.html', title=field.field_name, field=field)


@club.route("/myfield/<int:field_id>/cancel_field", methods=['POST'])
@login_required
def cancel_field(field_id):
    field = Field.query.get_or_404(field_id)
    booking = Booking.query.filter_by(field_id=field_id).first()
    if booking:
        flash('Fields with current Bookings cannot be canceled', 'danger')
        return redirect(url_for('club.club_home'))
    db.session.delete(field)
    db.session.commit()
    flash('Your field has been deleted!', 'success')
    return redirect(url_for('club.club_home'))


@club.route("/booking/<int:booking_id>")
@login_required
def booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    print booking
    return render_template('booking.html', title=booking.title, booking=booking)


@club.route('/booking/<int:booking_id>/cancel_booking', methods=['POST'])
@login_required
def cancel_booking(booking_id):  # to be tested
    booking = Booking.query.get_or_404(booking_id)
    # verify no date constraints

    if booking.date <= datetime.now():
        flash('Past booking cannot be canceled', 'info')
        return redirect(url_for('club.club_home'))

    # eliminate participants of the eliminated booking

    participants_user = Participants.query.filter_by(booking=booking.id).all()
    for part in participants_user:
        print part
        db.session.delete(part)
    '''
    # eliminate cost log

    costlog = CostLog.query.filter_by(title=meeting.title).first()
    db.session.delete(costlog)
    '''
    # send email to booker to notify that the event has been deleted
    player = Player.query.filter_by(user_id=booking.booker_id).first()
    user = User.query.filter_by(id=booking.booker_id).first()
    field = Field.query.filter_by(id=booking.field_id).first()
    club = Club.query.filter_by(user_id=current_user.id).first()
    print (player.name, player.surname, field.field_name, booking.date, booking.startTime, user.email)
    send_cancellation_email_club(club.name, field.field_name, booking.date.strftime("%d/%m/%y"), booking.startTime, user.email)
    db.session.delete(booking)
    db.session.commit()
    flash('Your booking has been deleted!', 'success')
    return redirect(url_for('club.club_home'))


@club.route('/clubs/<sport>')  # route needed fot java script select field only of the appropriate club
def clubs(sport):
    fields = Field.query.filter_by(sport=sport).all()

    club_list = []

    for field in fields:
        clubObj = {}
        clubObj['id'] = field.club_id
        clubObj['name'] = Club.query.filter_by(id=field.club_id).first().name
        club_list.append(clubObj)

    return jsonify({'clubs': club_list})


@club.route('/field/<club_id>/<sport>')  # route needed fot java script select field only of the appropriate club. problem with special characters
def field(club_id, sport):
    fields = Field.query.filter_by(club_id=club_id, sport=sport).all()

    field_list = []

    for field in fields:
        fieldObj = {}
        fieldObj['id'] = field.id
        fieldObj['name'] = field.field_name
        field_list.append(fieldObj)
        print field.field_name

    return jsonify({'fields': field_list})


@club.route("/club_profile/<int:club_id>", methods=['GET', 'POST'])
def club_profile(club_id):
    club = Club.query.filter_by(id=club_id).first()
    user = User.query.filter_by(id=club.user_id).first()
    image_file = url_for('static', filename='profile_pics/' + club.image_file)
    return render_template('club.html', title=club.name, club=club, user=user, image_file=image_file)

