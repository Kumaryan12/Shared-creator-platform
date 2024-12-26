from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.forms import RequirementForm, RegistrationForm
from app.models import User, Requirement, Message
from flask_socketio import emit, join_room
from app import socketio

auth = Blueprint('auth', __name__)

# Register Route
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
     form = RegistrationForm()
     if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Add the new user to the database
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Flash success message and redirect to login
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

     return render_template('register.html', form=form)

# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

# Logout Route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.home'))

# Dashboard Route
@auth.route('/dashboard')
@login_required
def dashboard():
    posted_requirements = Requirement.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', posted_requirements=posted_requirements)

# Route to post a new requirement
@auth.route('/post_requirement', methods=['GET', 'POST'])
@login_required
def post_requirement():
    form = RequirementForm()
    if form.validate_on_submit():
        new_requirement = Requirement(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            contact_info=form.contact_info.data,
            user_id=current_user.id
        )
        db.session.add(new_requirement)
        db.session.commit()
        flash('Requirement posted successfully!', 'success')
        return redirect(url_for('auth.view_requirements'))
    return render_template('post_requirement.html', form=form)

# Route to view all requirements
@auth.route('/view_requirements')
def view_requirements():
    all_requirements = Requirement.query.order_by(Requirement.timestamp.desc()).all()
    return render_template('view_requirements.html', requirements=all_requirements)

# Chat Route
@auth.route('/chat/<int:requirement_id>', methods=['GET'])
@login_required
def chat(requirement_id):
    requirement = Requirement.query.get_or_404(requirement_id)
    messages = Message.query.filter_by(requirement_id=requirement.id).order_by(Message.timestamp).all()
    return render_template('chat.html', requirement=requirement, messages=messages)

@socketio.on('send_message')
def handle_send_message(data):
    new_message = Message(
        sender_id=data['sender_id'],
        receiver_id=data['receiver_id'],
        requirement_id=data['requirement_id'],
        content=data['content']
    )
    db.session.add(new_message)
    db.session.commit()
    room = f"requirement_{data['requirement_id']}"
    emit('receive_message', {
        'content': data['content'],
        'sender_id': data['sender_id'],
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=room)

@socketio.on('join_room')
def handle_join_room(data):
    room = f"requirement_{data['requirement_id']}"
    join_room(room)
    print(f"User {data['user_id']} joined room {room}")
