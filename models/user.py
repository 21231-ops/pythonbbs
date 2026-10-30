from enum import Enum
from datetime import datetime
from shortuuid import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from exts import db


class PermissionEnum(Enum):
    BOARD = "板块"
    POST = "帖子"
    COMMENT = "评论"
    FRONT_USER = "前台用户"
    CMS_USER = "后台用户"

class PermissionModel(db.Model):
    __tablename__ = "permission"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Enum(PermissionEnum), nullable=False, unique=True)

role_permission_table = db.Table(
    "role_permission_table",
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
    db.Column("permission_id", db.Integer, db.ForeignKey("permission.id"))
)

class RoleModel(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    desc = db.Column(db.String(200), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.now)

    permissions = db.relationship("PermissionModel", secondary=role_permission_table, backref="roles")

class UserModel(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(100), primary_key=True, default=uuid)
    username = db.Column(db.String(10), nullable=False, unique=True)
    _password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    avatar = db.Column(db.String(100))
    signature = db.Column(db.String(20))
    province = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    birthday = db.Column(db.Date)
    tags = db.Column(db.String(200))
    join_time = db.Column(db.DateTime, default=datetime.now)
    is_staff = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # 外键
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    role = db.relationship("RoleModel", backref="users")
    posts = db.relationship('PostModel', backref='author', lazy='dynamic')

    def __init__(self, *args, **kwargs):
        if "password" in kwargs:
            self.password = kwargs.get('password')
            kwargs.pop("password")
        super(UserModel, self).__init__(*args, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw_password):
        self._password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        result = check_password_hash(self._password.strip(), raw_password.strip())
        return result

    def has_permission(self, permission):
        return permission in [permission.name for permission in self.role.permissions]

class ChatMessageModel(db.Model):
    __tablename__ = "chat_message"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_user_id = db.Column(db.String(36), db.ForeignKey("user.id"))
    to_user_id = db.Column(db.String(36), db.ForeignKey("user.id"))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    from_user = db.relationship("UserModel", foreign_keys=[from_user_id])
    to_user = db.relationship("UserModel", foreign_keys=[to_user_id])