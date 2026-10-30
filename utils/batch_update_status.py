# utils/cms_utils.py
from exts import db

def batch_update_status(model, ids, is_active, extra_filters=None):
    """
    通用批量修改状态函数
    :param model: 数据库模型类 (如 CommentModel, PostModel)
    :param ids: 前端传来的 ID 列表
    :param is_active: 目标状态 (0 或 1)
    """

    if not ids:
        return False, "没有选中任何数据"

    try:
        query = model.query.filter(model.id.in_(ids))

        if extra_filters:
            for f in extra_filters:
                query = query.filter(f)

        query.update({"is_active": bool(is_active)}, synchronize_session=False)
        db.session.commit()
        return True, "操作成功"
    except Exception as e:
        db.session.rollback()
        return False, "数据库操作失败"