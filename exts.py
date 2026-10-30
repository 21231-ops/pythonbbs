from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_caching import Cache
from flask_wtf import CSRFProtect
from flask_avatars import Avatars
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
mail = Mail()
cache = Cache()
csrf = CSRFProtect()
avatars = Avatars()
migrate = Migrate()
socketio = SocketIO()