from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player, Booking, Field, Participants
from wesport.player.forms import PlayerRegistrationForm, BookingForm
from wesport.functions.users import save_picture, send_reset_email, send_cancellation_email
from datetime import datetime

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
        player = Player(name=form.name.data, surname=form.surname.data, gender=form.gender.data, phone_number=form.phone_number.data,
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
    bookings = Booking.query.filter_by(booker_id=current_user.id)
    events = db.session.query(Booking).join(Participants)\
        .add_columns(Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.id)\
        .filter(Participants.player==player.id).all()
    return render_template('player_home.html', player=player, bookings=bookings, events=events)


@player.route("/new_booking", methods=['GET', 'POST'])
@login_required
def new_booking():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
        player_booker = Player.query.filter_by(user_id=current_user.id).first()
        form = BookingForm()
        form.club.choices = [(club.id, club.name) for club in Club.query.all()]  # we can add the fact that we display only the club of the city with the function get_city
        form.field.choices = [(field.id, field.field_name) for field in Field.query.all()]
        form.players.choices = [(player.id, '%s %s' % (player.name, player.surname)) for player in Player.query.filter(Player.id != player_booker.id).all()]
    if form.validate_on_submit():

        # check time collision
        bookingcollisions = Booking.query.filter_by(date=datetime.combine(form.date.data, datetime.min.time())).filter_by(field_id=form.field.data).all()
        print(len(bookingcollisions))
        for bookingcollision in bookingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if form.start_time.data < bookingcollision.endTime and (form.start_time.data + form.duration.data) > bookingcollision.startTime:
                flash('The time from is already booked.', 'danger')
                print (bookingcollision.startTime,
                       bookingcollision.endTime)  # Player.query.filter_by(id=bookingcollision.booker_id).first().name, Player.query.filter_by(id=bookingcollision.booker_id).first().surname)
                return redirect(url_for('player.new_booking'))

        # make booking
        booker = current_user

        field = Field.query.filter_by(id=form.field.data).first()
        # cost = room.cost
        end_time = form.start_time.data + form.duration.data

        booking = Booking(title=form.title.data, date=form.date.data, field_id=field.id, booker_id=booker.id, startTime=form.start_time.data, endTime=end_time, duration=form.duration.data)
        db.session.add(booking)
        db.session.commit()

        booking_id = Booking.query.filter_by(booker_id=booker.id).order_by(Booking.id.desc()).first().id
        booker_participants = Participants(booking=booking_id, player=player_booker.id)
        db.session.add(booker_participants)
        participants_user = form.players.data
        print participants_user

        if participants_user:
            # Add participants records
            for participant in participants_user:
                participating = Participants(booking=booking_id, player=participant)
                db.session.add(participating)

        db.session.commit()

        flash('Booking processed with success!', 'success')

        return redirect(url_for("player.player_home"))
    return render_template('book.html', title='Book', form=form)


@player.route("/event/<int:event_id>")
def event(event_id):
    booking = Booking.query.get_or_404(event_id)
    booker = Player.query.filter_by(id=booking.booker_id).first()
    return render_template('event.html', title=booking.title, booking=booking, booker=booker.user_id)


@player.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel(event_id):
    booking = Booking.query.get_or_404(event_id)
    if booking.booker_id != Player.query.filter_by(user_id=current_user.id).first().id:
        abort(403)

    # verify no date constraints

    if booking.date <= datetime.now():
        flash('Past booking cannot be canceled', 'info')
        return redirect(url_for('player.player_home'))

    # eliminate participants of the eliminated booking

    participants_user = Participants.query.filter_by(booking=booking.id).all()
    for part in participants_user:
        db.session.delete(part)
    '''
    # eliminate cost log
    
    costlog = CostLog.query.filter_by(title=meeting.title).first()
    db.session.delete(costlog)
    '''
    # send email to club to notify that the event has been deleted
    player = Player.query.filter_by(user_id=current_user.id).first()
    field = Field.query.filter_by(id=booking.field_id).first()
    club = Club.query.filter_by(id=field.club_id).first()
    club_user = User.query.filter_by(id=club.user_id).first()
    print (player.name, player.surname, field.field_name, booking.date, booking.startTime, club_user.email)
    send_cancellation_email(player.name, player.surname, field.field_name, booking.date.strftime("%d/%m/%y"), booking.startTime, club_user.email)
    db.session.delete(booking)
    db.session.commit()
    flash('Your booking has been deleted!', 'success')
    return redirect(url_for('player.player_home'))

