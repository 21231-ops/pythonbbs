from flask import session, request
from flask_socketio import emit
from exts import socketio, db
from models.user import UserModel, ChatMessageModel

online_users = {}

@socketio.on('connect')
def handle_connect():
    user_id = session.get("user_id")
    username = session.get("username")
    if username:
        online_users[user_id] = request.sid
        socketio.emit('update_online_count', {'count': len(online_users)})
    else:
        pass

@socketio.on('disconnect')
def handle_disconnect():
    # 清理断线用户
    user_to_remove = None
    for user_id, sid in online_users.items():
        if sid == request.sid:
            user_to_remove = user_id
            break
    if user_to_remove:
        del online_users[user_to_remove]
        socketio.emit('update_online_count', {'count': len(online_users)})


@socketio.on("personal")
def handle_personal_message(data):
    to_user_id = data.get("to_user_id")
    message_text = data.get("message")
    from_user_name = session.get("username")
    from_user_id = session.get("user_id")

    if not from_user_id:
        return

    # 1. 去数据库找接收者（王五）
    to_user_obj = UserModel.query.get(to_user_id)
    if not to_user_obj:
        return

    # 核心修复：无论对方在不在线，先把消息存进数据库！
    try:
        new_msg = ChatMessageModel(
            from_user_id=from_user_id,
            to_user_id=to_user_obj.id,
            content=message_text
        )
        db.session.add(new_msg)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return # 存库失败就不往下转发了

    to_sid = online_users.get(to_user_id)
    if to_sid:
        # 对方在线，实时推送
        emit("personal_msg", {
            "from_user": from_user_name,
            "message": message_text,
            "from_user_id":from_user_id,
            "is_me": False
        }, room=to_sid)
        
        # 发给自己
        emit("personal_msg", {
            "from_user": from_user_name,
            "message": message_text,
            "from_user_id": from_user_id,
            "is_me": True
        }, room=request.sid)
