from flask import Blueprint, current_app, send_from_directory

bp = Blueprint("media", __name__, url_prefix="/media")

@bp.get("/<path:filename>")
def media_file(filename):
    upload_dir = current_app.config.get("UPLOAD_IMAGE_PATH")
    return send_from_directory(upload_dir, filename)

