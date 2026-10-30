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

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/pythonbbs?charset=utf8mb4"
    MAIL_SERVER = "smtp.qq.com"
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_SENDER")
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "192.168.164.131"
    CACHE_REDIS_PORT = 6379
    CELERY_BROKER_URL = "redis://192.168.164.131:6379/0"
    CELERY_RESULT_BACKEND = "redis://192.168.164.131:6379/0"
    AVATARS_SAVE_PATH = os.path.join(BaseConfig.UPLOAD_IMAGE_PATH, "avatars")

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = ("mysql+pymysql://root:"
                               "root@192.168.164.131:"
                               "3306/pythonbbs?charset=utf8mb4")

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = ("mysql+pymysql://root:"
                               "root@192.168.164.131:"
                               "3306/pythonbbs?charset=utf8mb4")

config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

