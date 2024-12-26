from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db
from sqlalchemy import or_
from datetime import datetime
from app.blueprints.auth import auth


bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

from app import socketio
from flask_socketio import emit, join_room
from flask_login import current_user
from app.models import Message, db

@socketio.on('send_message')
def handle_send_message(data):
    # Save the message to the database
    new_message = Message(
        sender_id=current_user.id,
        requirement_id=data['requirement_id'],
        content=data['content']
    )
    db.session.add(new_message)
    db.session.commit()

    # Emit the message to the room
    room = f"requirement_{data['requirement_id']}"
    emit('receive_message', {
        'sender_id': current_user.id,
        'content': data['content'],
        'timestamp': new_message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, room=room)

@socketio.on('join_room')
def handle_join_room(data):
    room = f"requirement_{data['requirement_id']}"
    join_room(room)
    print(f"User {data['user_id']} joined room {room}")


@auth.route('/chats')
@login_required
def chat_list():
    # Find all unique users the current user has chatted with
    user_chats = (
        Message.query.filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id
            )
        )
        .distinct(Message.sender_id, Message.receiver_id)
        .all()
    )

    # Build a unique list of chat participants
    participants = {}
    for message in user_chats:
        if message.sender_id != current_user.id:
            participants[message.sender_id] = message.sender
        if message.receiver_id != current_user.id:
            participants[message.receiver_id] = message.receiver

    return render_template('chat_list.html', participants=participants)

@auth.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def unified_chat(user_id):
    # Retrieve the user being chatted with
    chat_user = User.query.get_or_404(user_id)

    # Get all messages between the current user and the chat_user
    messages = (
        Message.query.filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == user_id
            )
        )
        .order_by(Message.timestamp)
        .all()
    )

    return render_template('unified_chat.html', chat_user=chat_user, messages=messages)
