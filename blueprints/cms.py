from datetime import datetime

from flask import Blueprint, render_template, redirect, g, request, flash, url_for
from socket_events import online_users
from decorators import permission_required
from exts import db
from forms.cms import AddStaffForm, EditStaffForm
from models.post import PostModel, CommentModel, BoardModel
from models.user import PermissionEnum, UserModel, RoleModel
from utils import restful
from utils.batch_update_status import batch_update_status

bp = Blueprint("cms", __name__, url_prefix="/cms")

@bp.get("")
def index():
        post_count = PostModel.query.count()
        user_count = UserModel.query.count()
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_post = PostModel.query.filter(PostModel.create_time >= today_start).count()
        recent_posts = PostModel.query.order_by(PostModel.create_time.desc()).limit(5).all()
        online_count = len(online_users)
        return render_template(
            "cms/index.html",
            post_count=post_count,
            user_count=user_count,
            today_post=today_post,
            recent_posts=recent_posts,
            online_count=online_count
        )

@bp.before_request
def cms_before_request():
    if not hasattr(g, "user") or g.user.is_staff == False:
        return redirect("/")

@bp.context_processor
def context_processor():
    return {"PermissionEnum":PermissionEnum}

@bp.route("/staff/add", methods=['GET', 'POST'])
@permission_required(PermissionEnum.CMS_USER)
def add_staff():
    if request.method == "GET":
        roles = RoleModel.query.all()
        return render_template("cms/add_staff.html", roles=roles)
    else:
        form = AddStaffForm(request.form)
        if form.validate():
            email = form.email.data
            role_id = form.role.data
            user = UserModel.query.filter_by(email=email).first()
            if not user:
                flash("没有此用户！")
                return redirect(url_for("cms.add_staff"))
            user.is_staff = True
            user.role = RoleModel.query.get(role_id)
            db.session.commit()
            return redirect(url_for("cms.staff_list"))

        else:
            for message in form.messages:
                flash(message)
            return redirect(url_for("cms.add_staff"))

@bp.route("/staff/edit/<string:user_id>", methods=['GET', 'POST'])
@permission_required(PermissionEnum.FRONT_USER)
def edit_staff(user_id):
    user = UserModel.query.get(user_id)
    if request.method == 'GET':
        roles = RoleModel.query.all()
        return render_template("cms/edit_staff.html", user=user, roles=roles)
    else:
        form = EditStaffForm(request.form)
        if form.validate():
            is_staff = form.is_staff.data
            role_id = form.role.data
            user.is_staff = is_staff
            if not user.role or user.role.id != role_id:
                user.role = RoleModel.query.get(role_id)
            db.session.commit()
            return redirect(url_for("cms.edit_staff", user_id=user_id))
        else:
            for message in form.messages:
                flash(message)
            return redirect(url_for("cms.edit_staff", user_id=user_id))


@bp.post("/board/edit/<int:board_id>")
@permission_required(PermissionEnum.BOARD)
def edit_board(board_id):
    board = BoardModel.query.get(board_id)
    new_name = request.form.get("name")
    if not new_name or len(new_name) > 20:
        return restful.params_error(message="名称不合法！")

    board.name = new_name
    db.session.commit()
    return restful.ok()


@bp.get("/staff/list")
@permission_required(PermissionEnum.CMS_USER)
def staff_list():
    users = UserModel.query.filter_by(is_staff=True).all()
    return render_template("cms/staffs.html", users=users)

@bp.route("/users")
@permission_required(PermissionEnum.CMS_USER)
def user_list():
    users = UserModel.query.filter_by(is_staff=False).all()
    return render_template("cms/users.html", users=users)

@bp.get("/posts")
@permission_required(PermissionEnum.POST)
def post_list():
    posts = PostModel.query.all()
    return render_template("cms/posts.html", posts=posts)

@bp.get("/comments")
@permission_required(PermissionEnum.COMMENT)
def comment_list():
    comments = CommentModel.query.all()
    return render_template("cms/comments.html", comments=comments)

@bp.get("/boards")
@permission_required(PermissionEnum.BOARD)
def board_list():
    boards = BoardModel.query.all()
    return render_template("cms/boards.html", boards=boards)

@bp.post("/users/active/<string:user_id>")
@permission_required(PermissionEnum.FRONT_USER)
def active_user(user_id):
    is_active = request.form.get("is_active", type=int)
    if is_active is None:
        return restful.params_error(message="请传入is_active参数！")
    user = UserModel.query.get(user_id)
    user.is_active = bool(is_active)
    db.session.commit()
    return restful.ok()

@bp.post("/posts/active/<int:post_id>")
@permission_required(PermissionEnum.POST)
def active_post(post_id):
    is_active = request.form.get("is_active", type=int)
    if is_active is None:
        return restful.params_error(message="请传入is_active参数！")
    post = PostModel.query.get(post_id)
    post.is_active = bool(is_active)
    db.session.commit()
    return restful.ok()

@bp.post("/comments/active/<string:comment_id>")
@permission_required(PermissionEnum.COMMENT)
def active_comment(comment_id):
    is_active = request.form.get("is_active", type=int)
    if is_active is None:
        return restful.params_error(message="请传入is_active参数！")
    comment = CommentModel.query.get(comment_id)
    comment.is_active = bool(is_active)
    db.session.commit()
    return restful.ok()

@bp.post("/boards/active/<string:board_id>")
@permission_required(PermissionEnum.BOARD)
def active_board(board_id):
    is_active = request.form.get("is_active", type=int)
    if is_active is None:
        return restful.params_error(message="请传入is_active参数！")
    board = BoardModel.query.get(board_id)
    board.is_active = bool(is_active)
    db.session.commit()
    return restful.ok()

@bp.post("/comments/batch_update")
@permission_required(PermissionEnum.COMMENT)
def batch_update_comments():
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    is_active = request.form.get("is_active", type=int)
    success, msg = batch_update_status(CommentModel, ids, is_active)
    return restful.ok() if success else restful.params_error(message=msg)

@bp.post("/posts/batch_update")
@permission_required(PermissionEnum.POST)
def batch_update_posts():
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    is_active = request.form.get("is_active", type=int)
    success, msg = batch_update_status(PostModel, ids, is_active)
    return restful.ok() if success else restful.params_error(message=msg)

@bp.post("/boards/batch_update")
@permission_required(PermissionEnum.BOARD)
def batch_update_boards():
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    is_active = request.form.get("is_active", type=int)
    success, msg = batch_update_status(BoardModel, ids, is_active)
    return restful.ok() if success else restful.params_error(message=msg)

@bp.post("/users/batch_update")
@permission_required(PermissionEnum.FRONT_USER)
def batch_update_users():
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    is_active = request.form.get("is_active", type=int)
    success, msg = batch_update_status(UserModel, ids, is_active)
    return restful.ok() if success else restful.params_error(message=msg)

@bp.post("/staffs/batch_update")
@permission_required(PermissionEnum.CMS_USER)
def batch_update_staffs():
    ids = request.form.getlist('ids[]') or request.form.getlist('ids')
    is_active = request.form.get("is_active", type=int)

    if not is_active:
        ids = [str(i) for i in ids if str(i) != str(g.user.id)]

    success, msg = batch_update_status(UserModel, ids, is_active)
    return restful.ok() if success else restful.params_error(message=msg)