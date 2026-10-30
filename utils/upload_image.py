# utils/upload.py
import os
import uuid

from flask import request, jsonify, url_for, current_app, session

def save_uploaded_image(request_file_name='image'):
    f = request.files.get(request_file_name)

    if not f or not f.filename:
        return jsonify({"error": 400, "message": "未选择文件"}), 400

    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg', 'webp']:
        return jsonify({"error": 400, "data": []}), 400

    user_id = session.get('user_id')

    base_dir = current_app.config.get("CHAT_IMAGES_PATH")
    # 拼接上用户 ID 作为子文件夹 (static/upload/chat_images/用户ID)
    save_dir = os.path.join(base_dir, str(user_id))
    # 如果文件夹不存在，自动创建
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{extension}"

    save_path = os.path.join(save_dir, filename)
    f.save(save_path)

    url = url_for('media.media_file', filename=f"chat_images/{user_id}/{filename}")

    return jsonify({
        "errno": 0,
        "data": [{"url": url, "alt": "", "href": ""}]
    })