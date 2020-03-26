from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import func
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player, Booking, Field, Participants
from wesport.player.forms import PlayerRegistrationForm, BookingForm, CurrentAddressForm, PostForm
from wesport.functions.users import save_picture, send_reset_email, send_cancellation_email, get_city, geocode, googledistance
from datetime import datetime
import ast

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
                        address=form.address.data, country=form.country.data, birthdate=form.birthdate.data, user_id=u.id)
        db.session.add(player)
        db.session.commit()
        flash('Your registration has been completed!', 'success')
        return redirect(url_for('main.login'))
    return render_template('player_register.html', title='Player Registration', form=form)


@player.route("/player_home")
@login_required
def player_home():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
    player = Player.query.filter_by(user_id=current_user.id).first()
    bookings = Booking.query.filter_by(booker_id=current_user.id)\
                .filter(Booking.date > datetime.now()) \
                .all()
    bookings_query = db.session.query(Booking).filter_by(booker_id=current_user.id).add_columns(Booking.id).all()  # query to pass the booking.ids to exclude in the public event
    participants = db.session.query(Participants, Player).add_columns(Participants.booking, Player.id, Player.name, Player.surname, Player.image_file)\
        .filter(Participants.player == Player.id)
    fields = Field.query.all()
    clubs = Club.query.all()
    bookings_id = []  # list of ids of my bookings
    for booking in bookings_query:
        bookings_id.append(booking[1])
    myevents = db.session.query(Booking).join(Participants)\
        .add_columns(Booking.id, Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.booker_id, Booking.field_id)\
        .filter(Participants.player == player.id).filter(current_user.id != Booking.booker_id) \
        .filter(Booking.date > datetime.now()) \
        .all()
    myevents_id = []  # list of ids of the event i have already joined
    for event in myevents:
        myevents_id.append(event[1])
    events = db.session.query(Booking, Participants, Field)\
        .add_columns(Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.id, Booking.field_id)\
        .filter(Booking.id == Participants.booking).filter(Booking.field_id == Field.id)\
        .filter(Booking.id.notin_(myevents_id))\
        .filter(Booking.id.notin_(bookings_id))\
        .filter(Booking.date > datetime.now())\
        .group_by(Booking.id)\
        .having(func.count(Participants.player) < Field.max_people).all()
    past_events = db.session.query(Booking, Participants, Field) \
        .add_columns(Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.id, Booking.field_id) \
        .filter(Booking.id == Participants.booking).filter(Booking.field_id == Field.id) \
        .filter(Booking.date < datetime.now()) \
        .filter(Participants.player == current_user.id)\
        .group_by(Booking.id) \
        .having(func.count(Participants.player) < Field.max_people).all()
    image_file = url_for('static', filename='profile_pics/' + player.image_file)
    return render_template('player_home.html', title='Home', player=player, bookings=bookings, participants=participants, myevents=myevents,
                           events=events, past_events=past_events, fields=fields, clubs=clubs, image_file=image_file)


@player.route("/new_booking/<location>", methods=['GET', 'POST'])
@login_required
def new_booking(location):  # i need to pass a parameter because i need to pass the latlon coordinates to query the club. if i don't have coord i pass nolocation
    clubs = Club.query.all()
    near_club = []
    markers = []
    contents = []
    if location == 'nolocation':
        latlon = location
        lat, lon = get_city()  # used to center the map in the city i'm in. it doesn't work very well
    else:
        latlon = ast.literal_eval(location)  # used to convert the string parameter location into a dictionary
        lat = latlon['lat']
        lon = latlon['lon']
        for club in clubs:
            output = googledistance(lat, lon, club.lat, club.lon)
            if output['distance_value'] < 5000:
                near_club.append({'name': club.name, 'distance': output['distance_value']})
        near_club.sort(key=lambda k: k['distance'])
        print near_club
    for club in clubs:  # sample marker to pass to the map
        markers.append([club.lat, club.lon, club.id])
        contents.append({'name': club.name, 'id': club.id})
    print markers
    print contents
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
        player_booker = Player.query.filter_by(user_id=current_user.id).first()
        form = BookingForm()
        address = CurrentAddressForm()
        club_choices = [('0', '---select option---')]+[(club.id, club.name) for club in Club.query.all()]
        field_choices = [('0', '---select option---')]+[(field.id, field.field_name) for field in Field.query.all()]
        form.club.choices = club_choices  # we can add the fact that we display only the club of the city with the function get_city
        form.field.choices = field_choices
        form.players.choices = [(player.id, '%s %s' % (player.name, player.surname)) for player in Player.query.filter(Player.id != player_booker.id).all()]
    if form.validate_on_submit():

        # check time collision
        bookingcollisions = Booking.query.filter_by(date=datetime.combine(form.date.data, datetime.min.time())).filter_by(field_id=form.field.data).all()
        print(len(bookingcollisions))
        for bookingcollision in bookingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if form.start_time.data < bookingcollision.endTime and (form.start_time.data + form.duration.data) > bookingcollision.startTime:
                flash('The time slot is already booked.', 'danger')
                print (bookingcollision.startTime,
                       bookingcollision.endTime)  # Player.query.filter_by(id=bookingcollision.booker_id).first().name, Player.query.filter_by(id=bookingcollision.booker_id).first().surname)
                return redirect(url_for('player.new_booking', location=location))

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
        participants_user = form.players.data
        print participants_user
        if len(participants_user) > (field.max_people - 1):
            db.session.delete(booking)
            db.session.commit()
            flash('You need to select max ' + str(field.max_people - 1) + ' players', 'danger')
            return render_template('book.html', title='Book', form=form, lat=lat, lon=lon, markers=markers,
                                   address=address, latlon=latlon, near_club=near_club, contents=contents)
        db.session.add(booker_participants)
        if participants_user:
            # Add participants records
            for participant in participants_user:
                participating = Participants(booking=booking_id, player=participant)
                db.session.add(participating)
        db.session.commit()

        flash('Booking processed with success!', 'success')

        return redirect(url_for("player.player_home"))

    mylocation = {'lat': 45, 'lon': 45}  # initialize the dict for location
    if address.validate_on_submit():
        mylocation['lat'], mylocation['lon'] = geocode(address.address.data + ',' + address.city.data)  # pass the latlon coordinates if submitted
        return redirect(url_for('player.new_booking', location=mylocation))
    return render_template('book.html', title='Book', form=form, lat=lat, lon=lon, markers=markers, address=address, latlon=latlon, near_club=near_club, contents=contents)


@player.route("/event/<int:event_id>", methods=['GET', 'POST'])
def event(event_id):
    time_now = datetime.now()
    posts = db.session.query(Post, Player)\
        .add_columns(Post.id, Post.event, Post.date_posted, Post.content, Player.name, Player.surname, Player.image_file)\
        .filter(Post.player_id == Player.id).filter(Post.event == event_id)
    form = PostForm()
    if form.validate_on_submit():
        post = Post(player_id=Player.query.filter_by(user_id=current_user.id).first().id, event=event_id, content=form.content.data)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('player.event', event_id=event_id))
    print posts
    booking = Booking.query.get_or_404(event_id)
    player_user = Player.query.filter_by(user_id=current_user.id).first()
    participants = Participants.query.filter_by(booking=booking.id).all()
    players = db.session.query(Participants, Player)\
        .add_columns(Participants.booking, Player.id, Player.name, Player.surname, Player.image_file) \
        .filter(Participants.player == Player.id).filter(Participants.booking == event_id)
    field = Field.query.filter_by(id=booking.field_id).first()
    club = Club.query.filter_by(id=field.club_id).first()
    player_status = 0
    booker = User.query.filter_by(id=booking.booker_id).first()
    for part in participants:
        if player_user.id == part.player:
            player_status = 1
    if player_status == 1:
        return render_template('event.html', title=booking.title, booking=booking, booker=booker.id, player_status=player_status, posts=posts,
                           players=players, club=club, field=field, form=form, time_now=time_now)
    else:
        return render_template('event_out.html', title=booking.title, booking=booking, booker=booker.id,
                               player_status=player_status, players=players, club=club, field=field, form=form, time_now=time_now)


@player.route("/event/<int:event_id>/join", methods=['POST'])
@login_required
def join(event_id):
    booking = Booking.query.get_or_404(event_id)
    player_user = Player.query.filter_by(user_id=current_user.id).first()
    participants = Participants.query.filter_by(booking=booking.id).all()
    for part in participants:
        if player_user.id == part.player:
            flash('You are already part of this event', 'info')
            return redirect(url_for('player.player_home'))
    player_join = Participants(booking=booking.id, player=player_user.id)
    db.session.add(player_join)
    db.session.commit()
    flash('You join this event. Have Fun!', 'success')
    return redirect(url_for('player.player_home'))


@player.route("/event/<int:event_id>/leave", methods=['POST'])
@login_required
def leave(event_id):
    booking = Booking.query.get_or_404(event_id)
    player_user = Player.query.filter_by(user_id=current_user.id).first()
    participant = Participants.query.filter_by(booking=booking.id, player=player_user.id).first()
    db.session.delete(participant)
    db.session.commit()
    flash('You left the event!', 'success')
    return redirect(url_for('player.player_home'))


@player.route('/event/<int:event_id>/cancel', methods=['POST'])
@login_required
def cancel(event_id):
    booking = Booking.query.get_or_404(event_id)
    if booking.booker_id != User.query.filter_by(id=current_user.id).first().id:
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
    player = Player.query.filter_by(user_id=booking.booker_id).first()
    field = Field.query.filter_by(id=booking.field_id).first()
    club = Club.query.filter_by(id=field.club_id).first()
    club_user = User.query.filter_by(id=club.user_id).first()
    print (player.name, player.surname, field.field_name, booking.date, booking.startTime, club_user.email)
    send_cancellation_email(player.name, player.surname, field.field_name, booking.date.strftime("%d/%m/%y"), booking.startTime, club_user.email)
    posts = Post.query.filter_by(event=event_id)
    for post in posts:
        db.session.delete(post)
    db.session.delete(booking)
    db.session.commit()
    flash('Your booking has been deleted!', 'success')
    return redirect(url_for('player.player_home'))


@player.route("/my_bookings")
@login_required
def my_bookings():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
    player = Player.query.filter_by(user_id=current_user.id).first()
    bookings = Booking.query.filter_by(booker_id=current_user.id)\
                .filter(Booking.date > datetime.now()) \
                .all()
    participants = db.session.query(Participants, Player)\
        .add_columns(Participants.booking, Player.id, Player.name, Player.surname, Player.image_file) \
        .filter(Participants.player == Player.id)
    fields = Field.query.all()
    clubs = Club.query.all()
    image_file = url_for('static', filename='profile_pics/' + player.image_file)
    return render_template('my_bookings.html', title='My Bookings', player=player, bookings=bookings, participants=participants,
                           fields=fields, clubs=clubs, image_file=image_file)


@player.route("/my_events")
@login_required
def my_events():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
    player = Player.query.filter_by(user_id=current_user.id).first()
    bookings_query = db.session.query(Booking).filter_by(booker_id=current_user.id).add_columns(Booking.id).all()  # query to pass the booking.ids to exclude in the public event
    participants = db.session.query(Participants, Player)\
        .add_columns(Participants.booking, Player.id, Player.name, Player.surname, Player.image_file) \
        .filter(Participants.player == Player.id)
    fields = Field.query.all()
    clubs = Club.query.all()
    bookings_id = []  # list of ids of my bookings
    for booking in bookings_query:
        bookings_id.append(booking[1])
    myevents = db.session.query(Booking).join(Participants) \
        .add_columns(Booking.id, Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.booker_id,
                     Booking.field_id) \
        .filter(Participants.player == player.id).filter(current_user.id != Booking.booker_id) \
        .filter(Booking.date > datetime.now()) \
        .all()
    image_file = url_for('static', filename='profile_pics/' + player.image_file)
    return render_template('my_events.html', title='My Events', player=player, participants=participants,
                           fields=fields, clubs=clubs, image_file=image_file, myevents=myevents)


@player.route("/events")
@login_required
def events():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
    player = Player.query.filter_by(user_id=current_user.id).first()
    bookings_query = db.session.query(Booking).filter_by(booker_id=current_user.id).add_columns(Booking.id).all()  # query to pass the booking.ids to exclude in the public event
    participants = db.session.query(Participants, Player).add_columns(Participants.booking, Player.id, Player.name, Player.surname, Player.image_file)\
        .filter(Participants.player == Player.id)
    fields = Field.query.all()
    clubs = Club.query.all()
    bookings_id = []  # list of ids of my bookings
    for booking in bookings_query:
        bookings_id.append(booking[1])
    myevents = db.session.query(Booking).join(Participants)\
        .add_columns(Booking.id, Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.booker_id, Booking.field_id)\
        .filter(Participants.player == player.id).filter(current_user.id != Booking.booker_id) \
        .filter(Booking.date > datetime.now()) \
        .all()
    myevents_id = []  # list of ids of the event i have already joined
    for event in myevents:
        myevents_id.append(event[1])
    events = db.session.query(Booking, Participants, Field)\
        .add_columns(Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.id, Booking.field_id)\
        .filter(Booking.id == Participants.booking).filter(Booking.field_id == Field.id)\
        .filter(Booking.id.notin_(myevents_id))\
        .filter(Booking.id.notin_(bookings_id))\
        .filter(Booking.date > datetime.now())\
        .group_by(Booking.id)\
        .having(func.count(Participants.player) < Field.max_people).all()
    image_file = url_for('static', filename='profile_pics/' + player.image_file)
    return render_template('events.html', title='Join Events', player=player, participants=participants, myevents=myevents,
                           events=events, fields=fields, clubs=clubs, image_file=image_file)


@player.route("/past_events")
@login_required
def past_events():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
    player = Player.query.filter_by(user_id=current_user.id).first()
    participants = db.session.query(Participants, Player).add_columns(Participants.booking, Player.id, Player.name, Player.surname, Player.image_file)\
        .filter(Participants.player == Player.id)
    fields = Field.query.all()
    clubs = Club.query.all()
    past_events = db.session.query(Booking, Participants, Field) \
        .add_columns(Participants.player, Booking.title, Booking.date, Booking.startTime, Booking.id, Booking.field_id) \
        .filter(Booking.id == Participants.booking).filter(Booking.field_id == Field.id) \
        .filter(Booking.date < datetime.now()) \
        .filter(Participants.player == current_user.id)\
        .group_by(Booking.id) \
        .having(func.count(Participants.player) < Field.max_people).all()
    image_file = url_for('static', filename='profile_pics/' + player.image_file)
    return render_template('past_events.html', title='Past Events', player=player, participants=participants,
                           past_events=past_events, fields=fields, clubs=clubs, image_file=image_file)


@player.route("/players/<int:player_id>", methods=['GET', 'POST'])
def players(player_id):
    player = Player.query.filter_by(id=player_id).first()
    user = User.query.filter_by(id=player.user_id).first()
    image_file = url_for('static', filename='profile_pics/' + player.image_file)
    return render_template('player.html', title=player.name, player=player, user=user, image_file=image_file)