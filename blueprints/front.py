import bleach
from flask import Blueprint, request, render_template, jsonify, current_app, url_for, g, flash, session, redirect
from flask_paginate import Pagination
from sqlalchemy import or_, and_, func, desc
from decorators import login_required
from exts import db
from forms.post import PublicPostForm, PublicCommentForm
from models.post import BoardModel, PostModel, CommentModel
from models.user import UserModel, ChatMessageModel
from utils import restful
from utils.upload_image import save_uploaded_image
bp = Blueprint("front", __name__, url_prefix="")

@bp.route("/")
def index():
    current_app.logger.info("index页面被请求了")
    boards = BoardModel.query.all()
    page = request.args.get("page", type=int, default=1)
    board_id = request.args.get("board_id", type=int, default=0)
    start = (page - 1) * current_app.config.get("PER_PAGE_COUNT")
    end = start + current_app.config.get("PER_PAGE_COUNT")
    query_obj = PostModel.query.filter_by(is_active=True)

    if board_id != 0:
        query_obj = query_obj.filter_by(board_id=board_id)

    query_obj = query_obj.order_by(PostModel.create_time.desc())
    total = query_obj.count()
    posts = query_obj.slice(start, end)
    pagination = Pagination(bs_version=4, page=page, total=total, outer_window=0, inner_window=2, alignment="center")
    context = {
        "posts":posts,
        "boards":boards,
        "pagination":pagination,
        "current_board":board_id
    }
    return render_template("front/index.html", **context)

@bp.post("/upload/image")
@login_required
def upload_image():
    return save_uploaded_image()

@bp.route("/post/public", methods=['GET', 'POST'])
@login_required
def public_post():
    if request.method == 'GET':
        boards = BoardModel.query.all()
        return render_template("front/public_post.html", boards=boards)
    else:
        form = PublicPostForm(request.form)
        if form.validate():
            title = form.title.data
            content = form.content.data
            board_id = form.board_id.data
            post = PostModel(title=title, content=content, board_id=board_id, author=g.user)
            db.session.add(post)
            db.session.commit()
            return restful.ok()
        else:
            message = form.messages[0]
            return restful.params_error(message=message)


@bp.post("/post/<int:post_id>/comment")
@login_required
def public_comment(post_id):
    form = PublicCommentForm(request.form)
    if form.validate():
        # 拿到原始富文本
        raw_content = form.content.data

        # 定义允许的标签（只允许安全的排版和图片）
        allowed_tags = ['p', 'b', 'i', 'u', 'strong', 'em', 'br', 'img', 'a', 'span']
        allowed_attrs = {
            'img': ['src', 'alt', 'style', 'class'],
            'a': ['href', 'target']
        }

        # 清洗危险代码！
        clean_content = bleach.clean(raw_content, tags=allowed_tags, attributes=allowed_attrs)

        # 存进数据库
        comment = CommentModel(content=clean_content, post_id=post_id, author=g.user)
        db.session.add(comment)
        db.session.commit()
        return jsonify({"code": 200, "message": "评论成功"})
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(error)
        return redirect(url_for("front.post_detail", post_id=post_id))


@bp.get("/api/search")
def api_search():
    keyword = request.args.get("keyword", "").strip()
    page = request.args.get("page", 1, type=int)  # 接收页码，默认第 1 页

    if not keyword:
        return jsonify({"code": 200, "data": [], "total_pages": 0, "current_page": 1})

    query = PostModel.query.join(UserModel).filter(
        or_(
            PostModel.title.contains(keyword),
            UserModel.username.contains(keyword)
        )
    ).order_by(PostModel.create_time.desc())

    pagination = query.paginate(page=page, per_page=10, error_out=False)
    posts = pagination.items

    post_list = []
    for post in posts:
        post_list.append({
            "id": post.id,
            "title": post.title,
            "author": post.author.username,
            "create_time": post.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            "comments_count": post.comments.count()
        })

    # 返回时带上分页信息
    return jsonify({
        "code": 200,
        "data": post_list,
        "total_pages": pagination.pages,
        "current_page": pagination.page
    })


@bp.route('/chat')
@login_required
def chat():
    if 'user_id' not in session:
        return redirect(url_for('user.login'))

    return render_template('front/chat.html')

@bp.route("/chat/history/<string:target_user_id>", methods=['GET'])
@login_required
def get_chat_history(target_user_id):
    my_id = session.get("user_id")
    target_user = UserModel.query.get(target_user_id)

    if not target_user:
        return jsonify({"code": 404, "message": "用户不存在"})

    # 查询：我发给他的 OR 他发给我的
    messages = ChatMessageModel.query.filter(
        or_(
            and_(ChatMessageModel.from_user_id == my_id, ChatMessageModel.to_user_id == target_user.id),
            and_(ChatMessageModel.from_user_id == target_user.id, ChatMessageModel.to_user_id == my_id)
        )
    ).order_by(ChatMessageModel.created_at.asc()).all()

    data = []
    for msg in messages:
        sender = UserModel.query.get(msg.from_user_id)
        data.append({
            "from_user": sender.username,
            "message": msg.content,
            "is_me": msg.from_user_id == my_id
        })

    return jsonify({"code": 200, "data": data})


@bp.get('/api/recent_contacts')
@login_required
def get_recent_contacts():
    # 获取当前登录用户的 ID
    my_id = session.get('user_id')
    # 找出所有和我有过交流的人，并取每个联系人的最后一次聊天时间
    # 情况 A: 我是发送方
    sent = db.session.query(
        ChatMessageModel.to_user_id.label('contact_id'), # 我给谁发过消息（contact_id）
        func.max(ChatMessageModel.created_at).label('last_time') # 我最后一次给他们发消息的时间（last_time）
    ).filter(ChatMessageModel.from_user_id == my_id).group_by(ChatMessageModel.to_user_id)

    # 情况 B: 我是接收方
    received = db.session.query(
        ChatMessageModel.from_user_id.label('contact_id'),
        func.max(ChatMessageModel.created_at).label('last_time')
    ).filter(ChatMessageModel.to_user_id == my_id).group_by(ChatMessageModel.from_user_id)

    subq = sent.union_all(received).subquery()

    recent_data = db.session.query(
        subq.c.contact_id, # .c是.columns的缩写
        func.max(subq.c.last_time).label('final_time')
    ).group_by(subq.c.contact_id).order_by(desc('final_time')).limit(20).all()

    contact_ids = [row.contact_id for row in recent_data]
    users = UserModel.query.filter(UserModel.id.in_(contact_ids)).all()
    user_map = {user.id: user for user in users}
    result = []
    for row in recent_data:
        user = user_map.get(row.contact_id)
        if user:
            result.append({
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar,
                # 把最后聊天时间也传给前端（如果有需要的话）
                "last_time": row.final_time.strftime('%Y-%m-%d %H:%M:%S')
            })

    # 7. 返回数据
    return jsonify({
        "code": 200,
        "data": result
    })