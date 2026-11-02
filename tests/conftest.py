import pytest
import os
os.environ['FLASK_ENV'] = 'testing'  # 强行设置为 testing
os.environ['DB_HOST'] = '127.0.0.1'

import redis
import pymysql


# ================= 环境准备：针对整个测试文件夹只执行一次 =================

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    print("\n\n================ [环境准备] 开始重置测试环境 ================")

    # 1. 暴力清空测试库，保证每次都是最干净的状态
    conn = pymysql.connect(host='127.0.0.1', user='root', password='root', database='pythonbbs_test')
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()
    conn.close()

    # 2. 引入 app 和 db
    from app import app
    from exts import db

    # 强制把连接指向测试库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1:3306/pythonbbs_test?charset=utf8mb4'

    with app.app_context():
        db.create_all()
        print("✅ 测试数据库表结构创建成功！")

        from commands import create_permission, create_role, create_board
        try:
            create_permission()
            create_role()
            create_board()
            print("✅ 基础数据初始化成功！")
        except Exception as e:
            print(f"初始化异常: {e}")

        # 在这里直接往数据库里塞一个 普通用户 账号
        from models.user import UserModel, RoleModel
        if not UserModel.query.filter_by(email='admin@qq.com').first():
            admin = UserModel(email='admin@qq.com', username='admin', password='123456', is_staff=True)
            user = UserModel(email='user@qq.com', username='user', password='123456', is_staff=False)
            # 找到角色，并赋给这个测试用户
            role_admin = RoleModel.query.filter_by(name='管理员').first()
            role_user = RoleModel.query.filter_by(name='普通用户').first()
            if role_admin:
                admin.role = role_admin

            if role_user:
                user.role = role_user

            db.session.add(admin)
            db.session.add(user)
            db.session.commit()

    # 清理 Redis
    r = redis.Redis(host='127.0.0.1', port=6379, db=0)
    r.flushdb()
    print("✅ Redis 缓存清理成功！")
    print("==============================================================\n")

    yield


@pytest.fixture(scope="session")
def base_url():
    """全局基础 URL"""
    return "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def api_headers():
    """通用请求头"""
    return {
        "User-Agent": "Pytest-Automation-Bot",
        "Accept": "text/html,application/json"
    }