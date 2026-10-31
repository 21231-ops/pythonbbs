from flask import current_app
from flask_mail import Message
from exts import mail
from celery import Celery

# 定义任务函数
def send_mail(recipient, subject, body):
    message = Message(subject=subject, recipients=[recipient], body=body, sender="灵犀论坛 <ikhdvn@qq.com>")
    mail.send(message)

#  创建Celery对象
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    app.celery = celery

    # 添加任务
    celery.task(name="send_mail")(send_mail)

    return celery