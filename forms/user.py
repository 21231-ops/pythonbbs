from wtforms import StringField, ValidationError, FileField
from wtforms.fields.simple import BooleanField, SubmitField, PasswordField
from wtforms.validators import Email, Length, Optional, DataRequired, EqualTo
from exts import cache
from models.user import UserModel
from .baseform import BaseForm

class RegisterForm(BaseForm):
    email = StringField(validators=[Email(message="请输入正确格式的邮箱！")])
    captcha = StringField(validators=[Length(min=6, max=6, message="请输入正确格式的验证码！")])
    username = StringField(validators=[Length(min=2, max=10, message="请输入正确格式的用户名！")])
    password = StringField(validators=[Length(min=6, max=20, message="请输入正确长度的密码！")])
    confirm_password = StringField(validators=[Length(min=6, max=20, message="两次密码不一致！")])

    def validate_email(self, field):
        email = field.data
        user = UserModel.query.filter_by(email=email).first()
        if user:
            raise ValidationError(message="邮箱已经存在！")

    def validate_captcha(self, field):
        captcha = field.data
        email = self.email.data
        cache_captcha = cache.get(email)
        if not cache_captcha or captcha != cache_captcha:
            raise ValidationError(message="验证码错误！")

class LoginForm(BaseForm):
    email = StringField(validators=[Email(message="请输入正确格式的邮箱！")])
    password = StringField(validators=[Length(min=6, max=20, message="请输入正确长度的密码！")])
    remember = BooleanField()

class EditProfileForm(BaseForm):
    username = StringField(validators=[Length(min=2, max=20, message="请输入正确格式的用户名！")])
    avatar = FileField()
    signature = StringField('个性签名', validators=[Optional(), Length(max=100)])
    province = StringField('所在地', validators=[Optional(), Length(max=50)])
    gender = StringField('性别', validators=[Optional(), Length(max=10)])
    birthday = StringField('生日', validators=[Optional()])

    def validate_signature(self, field):
            signature = field.data
            if signature and len(signature) > 100:
                raise ValidationError(message="签名不能超过100个字符！")

class PasswordResetForm(BaseForm):
    code = StringField('验证码', validators=[DataRequired(), Length(6,6)])
    new_password = PasswordField('新密码', validators=[DataRequired()])
    confirm_new_password = PasswordField('确认新密码', validators=[
        DataRequired(),
        EqualTo('new_password', message='两次输入的新密码不一致')
    ])
    submit = SubmitField('重置密码')
