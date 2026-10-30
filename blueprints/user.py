import os.path

from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash, session, g, jsonify

from exts import cache, db
from models.post import PostModel
from utils import restful
from forms.user import RegisterForm, LoginForm, EditProfileForm, PasswordResetForm
from models.user import UserModel, RoleModel
from werkzeug.datastructures import CombinedMultiDict

import random
import hashlib
import time

bp = Blueprint("user", __name__, url_prefix="/user")

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("front/register.html")
    else:
        form = RegisterForm(request.form)
        captcha_input = request.form.get("captcha")
        if form.validate():
            email = form.email.data
            username = form.username.data
            password = form.password.data

            if UserModel.query.filter_by(email=email).first():
                return jsonify({"code": 400, "message": "该邮箱已被注册"})

            cached_code = cache.get(email)
            if not cached_code or str(cached_code) != str(captcha_input).strip():
                return jsonify({"code": 400, "message": "验证码错误或已过期"})

            user = UserModel(email=email, username=username, password=password)
            default_role = RoleModel.query.filter_by(name="普通用户").first()
            if default_role:
                user.role = default_role
            db.session.add(user)
            db.session.commit()
            cache.delete(email)

            # 前端是 Ajax，必须返回 JSON，而不是 redirect
            return jsonify({"code": 200, "message": "注册成功", "redirect_url": "/user/login"})

        else:
            # 把表单错误拼成一条消息返回给前端
            error_msg = list(form.errors.values())[0][0]
            return jsonify({"code": 400, "message": error_msg})

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("front/login.html")
    else:
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = UserModel.query.filter_by(email=email).first()
            if user and user.check_password(password):
                if not user.is_active:
                    flash("该用户已被禁用！")
                    return redirect(url_for("user.login"))
                session['user_id'] = user.id
                session['username'] = user.username
                if remember:
                    session.permanent = True
                return redirect("/")
            else:
                flash("邮箱或密码错误！")
                return redirect(url_for("user.login"))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error)
            return render_template("front/login.html", form=form)

@bp.get('/logout')
def logout():
    session.clear()
    return redirect("/")

@bp.route("/mail/register")
def mail_register():
    try:
        email = request.args.get("mail")
        existing_user = UserModel.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"code": 400, "message": "该邮箱已注册，请直接登录！"})
        digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        captcha = "".join(random.sample(digits, 6))
        subject = "【灵犀论坛】注册验证码"
        body = f"【灵犀论坛】您的验证码是：{captcha},请勿告诉别人！"
        current_app.celery.send_task("send_mail", (email, subject, body))
        cache.set(email, captcha, timeout=600)
        return restful.ok()
    except Exception as e:
        return restful.server_error()

@bp.route('/mail/password-reset', methods=['GET', 'POST'])
def mail_password_reset():
    form = PasswordResetForm()

    if request.method == 'GET' and not request.args.get('mail'):
        return render_template('front/password_reset.html', form=form)

    else:
        try:
            email = request.args.get("mail")
            digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
            captcha = "".join(random.sample(digits, 6))
            subject = "【灵犀论坛】重置密码"
            body = f"【灵犀论坛】您的验证码是：{captcha},请勿告诉别人！"
            current_app.celery.send_task("send_mail", (email, subject, body))
            cache.set(email, captcha, timeout=600)
            return restful.ok(data={"redirect_url":url_for('user.password_reset_verify')})
        except Exception as e:
            return restful.server_error()


@bp.post('/password_reset_verify')
def password_reset_verify():
    email = request.form.get('email')
    code = request.form.get('code')
    new_password = request.form.get('new_password')

    if not all([email, code, new_password]):
        return jsonify({"code": 400, "message": "参数不能为空"})

    # 1. 查找用户
    user = UserModel.query.filter_by(email=email).first()
    if not user:
        return jsonify({"code": 400, "message": "用户不存在"})

    # 从缓存中取出刚才发的验证码
    cached_code = cache.get(email)

    # 校验逻辑
    if not cached_code:
        return jsonify({"code": 400, "message": "验证码已过期，请重新获取"})

    if str(cached_code) != str(code).strip():
        return jsonify({"code": 400, "message": "验证码错误，请重新输入"})

    # 验证成功，修改密码
    user.password = new_password  # 你模型里应该有 password 的 setter 自动加密
    db.session.commit()

    # 用过了就把缓存里的验证码删掉，防止重复使用
    cache.delete(email)
    session.clear()

    return jsonify({"code": 200, "message": "重置成功", "redirect_url": "/user/login"})

@bp.get("/profile/<string:user_id>")
def profile(user_id):
    if not user_id or user_id == 'None':
        flash("用户不存在")
        return redirect(url_for('front.index'))

    user = UserModel.query.get(user_id)
    posts = user.posts.order_by(PostModel.create_time.desc()).all()
    is_mine = False
    if hasattr(g, "user") and g.user.id == user_id:
        is_mine = True
    context = {
        "user":user,
        "is_mine":is_mine,
        "posts":posts
    }
    return render_template("front/profile.html", **context)

@bp.route("/profile/edit", methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    user = UserModel.query.get(user_id)

    if request.method == 'GET':

        return render_template("front/edit_profile.html", user=user)

    else:
        form = EditProfileForm(CombinedMultiDict([request.form, request.files]))
        if form.validate():
            username = form.username.data
            avatar = request.files.get('avatar')
            signature = request.form.get('signature')
            province = request.form.get('province')
            gender = request.form.get('gender')
            birthday = request.form.get('birthday')
            tags_list = request.form.getlist('tags[]')
            tags = ",".join(tags_list) if tags_list else ""

            user.username = username
            user.signature = signature
            user.province = province
            user.gender = gender
            user.tags = tags

            if birthday and birthday.strip():
                from datetime import datetime
                try:
                    user.birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
                except ValueError:
                    flash("生日格式不正确")
                    return redirect(url_for("user.profile", user_id=user.id))
            else:
                user.birthday = None


            if avatar and avatar.filename != '':
                ext = avatar.filename.rsplit('.', 1)[-1].lower()
                allowed_exts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
                if ext not in allowed_exts:
                    flash("不支持该图片格式！")
                    return redirect(request.url)

                file_content = avatar.read()
                file_hash = hashlib.md5(file_content).hexdigest()
                filename = f"{file_hash}.{ext}"

                save_dir = current_app.config.get("AVATARS_SAVE_PATH")
                user_folder = os.path.join(save_dir, str(user.id))
                os.makedirs(user_folder, exist_ok=True)
                avatar_path = os.path.join(user_folder, filename)

                with open(avatar_path, "wb") as f:
                    f.write(file_content)

                user.avatar = url_for("static",
                                      filename=f"upload/avatars/{user.id}/{filename}") + f"?t={int(time.time())}"

            try:
                db.session.commit()
                flash("修改资料成功！")
            except Exception as e:
                db.session.rollback()
                flash("修改失败，请检查数据格式")

            return redirect(url_for("user.profile", user_id=user.id))

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    flash(error)
            return redirect(url_for("user.profile", user_id=user.id))
