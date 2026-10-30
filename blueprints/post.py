from flask import Blueprint, render_template, request, make_response
from exts import  db
from models.post import PostModel

bp = Blueprint("posts", __name__, url_prefix="/post")

@bp.route("/detail/<int:post_id>")
def post_detail(post_id):
    post = PostModel.query.get(post_id)
    viewed_cookie = request.cookies.get(f'viewed_post_{post_id}')

    if not viewed_cookie:
        post.read_count += 1
        db.session.commit()

    resp = make_response(render_template("front/post_detail.html", post=post))

    if not viewed_cookie:
        resp.set_cookie(f'viewed_post_{post_id}', 'true', max_age=31536000)

    return resp


