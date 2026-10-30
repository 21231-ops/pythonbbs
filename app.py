from dotenv import load_dotenv
load_dotenv()
import logging
import commands
import config
import filters
import hooks
import os

from logging.handlers import RotatingFileHandler
from flask import Flask
from exts import db, mail, cache, csrf, avatars, socketio, migrate
from blueprints.cms import bp as cms_bp
from blueprints.front import bp as front_bp
from blueprints.user import bp as user_bp
from blueprints.post import bp as posts_bp
from blueprints.media import bp as media_bp
from bbs_celery import make_celery

app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config.config_map[env])
app.before_request(hooks.bbs_before_request)
app.template_filter("email_hash")(filters.email_hash)
celery = make_celery(app)

file_handler = RotatingFileHandler('pythonbbs.log', maxBytes=16384, backupCount=20)
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s: %(lineno)d]')
file_handler.setFormatter(file_formatter)
if app.logger.handlers:
    app.logger.removeHandler(app.logger.handlers[0])

app.logger.addHandler(file_handler)

# 注册错误钩子函数
app.errorhandler(401)(hooks.bbs_401_error)
app.errorhandler(403)(hooks.bbs_403_error)
app.errorhandler(404)(hooks.bbs_404_error)
app.errorhandler(500)(hooks.bbs_500_error)

db.init_app(app)
mail.init_app(app)
cache.init_app(app)
csrf.init_app(app)
avatars.init_app(app)
migrate.init_app(app, db)
socketio.init_app(app)
import socket_events

# 注册蓝图
app.register_blueprint(cms_bp)
app.register_blueprint(front_bp)
app.register_blueprint(user_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(media_bp)

# 注册自定义命令
app.cli.command("create-permission")(commands.create_permission)
app.cli.command("create-role")(commands.create_role)
app.cli.command("create-test-user")(commands.create_test_user)
app.cli.command("create-admin")(commands.create_admin)
app.cli.command("create-board")(commands.create_board)
app.cli.command("create-test-post")(commands.create_test_post)


if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=8000, allow_unsafe_werkzeug=True)
