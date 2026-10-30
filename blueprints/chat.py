from flask import session, request
from exts import socketio
from flask_socketio import emit
from models.user import UserModel


@socketio.on('connect')
def connect():
    UserModel.add_user(session.get("username"), request.sid)
    emit("users", {"users":UserModel.query.all()}, broadcast=True)
