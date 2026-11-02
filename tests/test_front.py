import requests

class TestFrontPages:
    """测试论坛前台的基础页面"""

    def test_index_page(self, base_url, api_headers):
        """测试首页能否正常打开"""
        res = requests.get(f"{base_url}/", headers=api_headers)
        assert res.status_code == 200
        assert "灵犀论坛" in res.text

    def test_login_page(self, base_url):
        """测试登录页能否打开"""
        res = requests.get(f"{base_url}/user/login")
        assert res.status_code == 200
        assert "立即登录" in res.text

    def test_register_page(self, base_url):
        """测试注册页能否打开"""
        res = requests.get(f"{base_url}/user/register")
        assert res.status_code == 200
        assert "立即注册" in res.text

    def test_404_page(self, base_url):
        """测试访问一个不存在的页面，应该返回 404"""
        res = requests.get(f"{base_url}/this_page_does_not_exist_123")
        assert res.status_code == 404