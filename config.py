import os.path
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    PER_PAGE_COUNT = 10
    UPLOAD_IMAGE_PATH = os.path.join(BASE_DIR, "static", "upload")
    CHAT_IMAGES_PATH = os.path.join(UPLOAD_IMAGE_PATH, "chat_images")
    CACHE_REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
    CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/0")
    MAIL_SERVER = "smtp.qq.com"
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_SENDER")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_PORT = 6379
    AVATARS_SAVE_PATH = os.path.join(BASE_DIR, "static", "upload", "avatars")

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        "mysql+pymysql://root:root@127.0.0.1:3306/pythonbbs?charset=utf8mb4"
    )

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = ("mysql+pymysql://root:"
                               "root@192.168.164.131:"
                               "3306/pythonbbs?charset=utf8mb4")

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        "mysql+pymysql://root:root@192.168.164.131:3306/pythonbbs?charset=utf8mb4"
    )

config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

