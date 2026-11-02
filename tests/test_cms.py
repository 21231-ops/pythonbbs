import pytest
import requests


class TestCMS:
    """测试后台管理系统 (CMS)"""

    def test_non_admin_access_cms(self, base_url):
        """1. 测试普通用户（无权限）访问 CMS 后台（安全测试）"""
        session = requests.Session()
        # 普通用户登录
        session.post(f"{base_url}/user/login", data={
            "email": "user@qq.com",
            "password": "123456"
        })
        # 访问 CMS 首页（注意：没有斜杠）
        res = session.get(f"{base_url}/cms")

        # 你的 cms.py 里 before_request 拦截后重定向了，所以这里断言重定向
        print("\n请求返回状态码:", res.status_code)
        print("请求返回内容:", res.text[:500])
        assert res.status_code == 200
        assert "灵犀论坛" in res.text


    def test_admin_access_cms(self, base_url):
        """2. 测试管理员正常访问 CMS 后台（业务测试）"""
        session = requests.Session()
        # 管理员登录
        session.post(f"{base_url}/user/login", data={
            "email": "admin@qq.com",
            "password": "123456"
        })
        res = session.get(f"{base_url}/cms")
        assert res.status_code == 200
        # 精准断言你模板里的标题
        assert "灵犀CMS管理系统" in res.text

    def test_admin_active_post(self, base_url):
        """3. 测试管理员在 CMS 中封禁/解封帖子（业务测试）"""
        session = requests.Session()
        session.post(f"{base_url}/user/login", data={"email": "admin@qq.com", "password": "123456"})

        # 真实接口是 /cms/posts/active/<post_id>
        post_id = 1
        res = session.post(f"{base_url}/cms/posts/active/{post_id}", data={"is_active": 1})

        # 你的接口返回的是 restful.ok()，所以是 200
        assert res.status_code == 200
        assert res.json().get("code") == 200

    def test_admin_batch_update_posts(self, base_url):
        """4. 测试管理员批量审核帖子（业务测试）"""
        session = requests.Session()
        session.post(f"{base_url}/user/login", data={"email": "admin@qq.com", "password": "123456"})

        # 真实接口是 /cms/posts/batch_update
        res = session.post(f"{base_url}/cms/posts/batch_update", data={
            "ids": [1, 2],
            "is_active": 0
        })
        assert res.status_code == 200
        assert res.json().get("code") == 200