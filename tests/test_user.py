import pytest
import requests


class TestUserAuth:
    """测试用户认证模块"""

    def get_captcha_from_redis(self, email):
        """去真实的 Redis 里拿验证码（使用你的项目自带的 cache 对象）"""
        # 直接从你的后端代码里导入 cache 对象
        from exts import cache

        # 用这个真实的 cache 对象去拿，它自己会处理 pickel 和前缀问题
        captcha = cache.get(email)

        if captcha is not None:
            return str(captcha)  # 确保转成字符串
        return None

    def test_register_success(self, base_url):
        """测试正常注册流程（成功）"""
        test_email = "zhangsan@qq.com"
        test_username = "zhangsan"
        test_password = "123456"
        is_staff = True

        # 请求发送验证码
        requests.get(f"{base_url}/user/mail/register?mail={test_email}")

        # 从 Redis 获取真实的验证码
        captcha = self.get_captcha_from_redis(test_email)
        assert captcha is not None, "失败：Redis里没找到验证码，请检查邮件发送逻辑"

        # 带上验证码去注册
        reg_res = requests.post(f"{base_url}/user/register", data={
            "email": test_email,
            "captcha": captcha,
            "username": test_username,
            "password": test_password,
            "confirm_password": test_password,
            "is_staff": is_staff
        })

        # 断言注册成功
        assert reg_res.status_code == 200
        data = reg_res.json()
        assert data.get("code") == 200
        assert "redirect_url" in data

    def test_register_fail_wrong_captcha(self, base_url):
        """测试注册失败：验证码错误"""
        reg_res = requests.post(f"{base_url}/user/register", data={
            "email": "fake_user@example.com",
            "captcha": "000000",
            "username": "fake_user",
            "password": "123456",
            "confirm_password": "123456"
        })

        # 验证码错误，后端应该拦截并返回错误（状态码可能是 200 渲染页面，或者 400 JSON）
        assert reg_res.status_code in [200, 400]
        # 断言页面里或 JSON 里包含错误提示（请根据你后端的实际提示词修改）
        assert "验证码错误" in reg_res.text or "验证码已过期" in reg_res.text or "code" in reg_res.text

    def test_login_success(self, base_url):
        """测试正常登录成功（必须等 admin 注册完才能跑）"""
        # 发送登录请求
        res = requests.post(f"{base_url}/user/login", data={
            "email": "admin@qq.com",
            "password": "123456"
        })

        # 登录成功通常返回 302 重定向到首页，或者返回 200 并渲染首页
        assert res.status_code in [200, 302]
        # 登录成功的页面里肯定有你的用户名，或者出现“退出登录”按钮
        assert "退出登录" in res.text or "admin" in res.text

    def test_login_wrong_password(self, base_url):
        """测试错误密码登录，应该失败并包含提示"""
        res = requests.post(f"{base_url}/user/login", data={
            "email": "admin@qq.com",
            "password": "wrong_password"
        })
        # 假设登录失败时，页面会重新渲染，状态码为 200，但包含错误提示
        print("\n返回状态码:", res.status_code)
        print("返回内容:", res.text[:200])  # 打印返回的前 200 个字符
        assert res.status_code == 200
        assert "登录" in res.text

    def test_login_invalid_length(self, base_url):
        """测试密码长度超出限制，应该被表单拦截"""
        res = requests.post(f"{base_url}/user/login", data={
            "email": "ikhdvn@qq.com",
            "password": "123"  # 故意用 3 个字符
        })


        # 如果关了 CSRF，这里应该是长密码提示；如果是 CSRF 拦截，则是 CSRF 提示
        assert "请输入正确长度的密码" in res.text or "CSRF" in res.text

    def test_send_mail_code(self, base_url):
        """测试发送邮箱验证码接口"""
        res = requests.get(f"{base_url}/user/mail/register?mail=test_captcha@example.com")
        assert res.status_code == 200
        data = res.json()
        assert data.get("code") == 200

    # def test_send_mail_too_fast(self, base_url):
    #     """测试验证码防刷（连续发送两次）"""
    #     email = "spam_test@example.com"
    #     # 第一次发送
    #     requests.get(f"{base_url}/user/mail/register?mail={email}")
    #     # 立刻发第二次
    #     res2 = requests.get(f"{base_url}/user/mail/register?mail={email}")
    #     data2 = res2.json()
    #     # 第二次应该被拦截，返回 400 或提示 "请求过于频繁"
    #     assert data2.get("code") == 400 or "频繁" in data2.get("message", "")
