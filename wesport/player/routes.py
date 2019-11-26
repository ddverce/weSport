from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from wesport import db, bcrypt
from wesport.models import User, Post, Club, Player, Booking, Field
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


@player.route("/new_booking", methods=['GET', 'POST'])
@login_required
def new_booking():
    if current_user.is_authenticated:
        if current_user.urole == 'Club':
            return redirect(url_for('club.club_home'))
        form = BookingForm()
        form.club.choices = [(club.id, club.name) for club in Club.query.all()]  # we can add the fact that we display only the club of the city with the function get_city
        form.field.choices = [(field.id, field.field_name) for field in Field.query.all()]
    if form.validate_on_submit():
        '''
        # check time collision
        meetingcollisions = Meeting.query.filter_by(date=datetime.combine(form.date.data, datetime.min.time())).filter_by(roomId=form.rooms.data).all()
        print(len(meetingcollisions))
        for meetingcollision in meetingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if (form.startTime.data < meetingcollision.endTime and (form.startTime.data + form.duration.data) > meetingcollision.startTime):
                flash(f'The time from {meetingcollision.startTime} to {meetingcollision.endTime} is already booked by {User.query.filter_by(id=meetingcollision.bookerId).first().fullname}.')
                return redirect(url_for('book'))
        '''
        # make booking
        booker = current_user

        field = Field.query.filter_by(id=form.field.data).first()
        # cost = room.cost
        end_time = form.start_time.data + form.duration.data

        # participants_user = form.participants_user.data
        # participants_partner = form.participants_partner.data

        booking = Booking(title=form.title.data, date=form.date.data, field_id=field.id, booker_id=booker.id, startTime=form.start_time.data, endTime=end_time, duration=form.duration.data)
        db.session.add(booking)
        db.session.commit()
        flash('Booking processed with success!', 'success')

        return redirect(url_for("player.player_home"))
    return render_template('book.html', title='Book', form=form)