from functools import wraps
from flask import redirect, url_for, g, abort, flash, request, jsonify


def login_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        # 判断是否登录
        if not hasattr(g, "user"):
            # 判断是不是 AJAX / Fetch 请求
            # 如果请求头里有 X-Requested-With，或者路径是 /api/ 或 /chat/history 等
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith(
                    '/api/') or request.path.startswith('/chat/history/'):
                return jsonify({"code": 401, "message": "请先登录"}), 401

            # 普通页面请求，才跳转到登录页
            return redirect(url_for("user.login"))

        # 判断账号是否被禁用
        elif not g.user.is_active:
            flash("该用户已被禁用！")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return jsonify({"code": 403, "message": "该账号已被禁用"}), 403
            return redirect(url_for("user.login"))

        # 正常
        return func(*args, **kwargs)

    return inner

def permission_required(permission):
    def outer(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if hasattr(g, "user") and g.user.has_permission(permission):
                return func(*args, **kwargs)
            else:
                return abort(403)
        return inner
    return outer
