import pytest
import requests


class TestPostAndComment:
    """测试帖子与评论模块"""

    def test_unauthorized_post(self, base_url):
        """未登录状态下尝试发帖（安全测试）"""
        res = requests.post(f"{base_url}/post/public", data={
            "title": "黑客攻击贴",
            "board_id": 1,
            "content": "<p>注入内容</p>"
        })

        assert res.status_code == 200
        assert "登录" in res.text or "/user/login" in res.text or "csrf-token" in res.text

    def test_unauthorized_comment(self, base_url):
        """未登录状态下尝试评论（安全测试）"""
        res = requests.post(f"{base_url}/post/1/comment", data={
            "content": "<p>恶意评论</p>"
        })
        assert res.status_code == 200
        assert "登录" in res.text or "/user/login" in res.text or "csrf-token" in res.text

    def test_rich_text_xss_injection(self, base_url):
        """测试富文本 XSS 过滤（安全测试）"""
        session = requests.Session()

        # 登录
        login_res = session.post(f"{base_url}/user/login", data={
            "email": "user@qq.com",
            "password": "123456"
        })
        # 断言登录成功，如果失败就不往下跑了
        assert "退出登录" in login_res.text or "user" in login_res.text, "❌ 登录失败！"

        # 2. 发送带有恶意代码的帖子
        xss_payload = "<p>XSS安全测试</p><script>alert('XSS攻击')</script>"
        post_res = session.post(f"{base_url}/post/public", data={
            "title": "XSS自动化测试贴",
            "board_id": 1,
            "content": xss_payload
        })
        # 发帖成功可能是 200（返回 JSON）或 302（重定向）
        assert post_res.status_code in [200, 302]

        # 3. 去首页验证
        index_res = requests.get(f"{base_url}/")

        # 安全断言：被过滤后的页面里绝对不能有可执行的 <script> 标签
        assert "<script>alert('XSS攻击')</script>" not in index_res.text

        # 业务断言：帖子里的正文文字应该还能看到（标签被删，文字保留）
        assert "XSS安全测试" in index_res.text or "XSS自动化测试贴" in index_res.text

    def test_upload_malicious_image(self, base_url):
        """测试图片上传（安全测试：上传非图片格式的文件）"""
        session = requests.Session()

        # 先正常登录（必须登录，因为接口有 @login_required）
        login_res = session.post(f"{base_url}/user/login", data={
            "email": "admin@qq.com",
            "password": "123456"
        })
        # 确保登录成功（如果你连登录都失败了，上传肯定 404 或 302）
        assert "退出登录" in login_res.text or "admin" in login_res.text

        # 伪造一个恶意文件（比如一个 HTML 文件）
        malicious_content = b"<script>alert('Upload XSS')</script>"
        files = {
            # 字段名通常是 'image'，具体看你前端上传组件传的 name
            'image': ('hack.html', malicious_content, 'text/html')
        }

        # 发送上传请求 (替换为真实的 /upload/image 路由)
        upload_res = session.post(f"{base_url}/upload/image", files=files)

        # 验证结果（安全断言）
        if upload_res.status_code == 200:
            data = upload_res.json()
            # 如果后端返回了成功，检查返回的文件名或 URL，不能是 .html
            # 假设你的后端返回格式是 {"code": 200, "data": {"url": "/static/upload/xxx.jpg"}}
            url = data.get("data", {}).get("url", "") or data.get("url", "")

            # 断言：绝对不允许返回 .html 后缀的文件
            assert not url.endswith(".html"), "❌ 严重漏洞：允许上传 HTML 文件，存在 XSS 风险！"
            # 也可以断言它被强制改成了图片后缀
            assert ".jpg" in url or ".png" in url or ".jpeg" in url

        else:
            # 如果后端直接拦截（比如返回了 400, 403, 500），说明安全拦截生效
            print(f"⚠️ 上传被拦截，状态码: {upload_res.status_code}")
            assert upload_res.status_code in [400, 403, 500]

    def test_create_post(self, base_url):
        """测试正常发布帖子（业务正向流程）"""
        session = requests.Session()

        # 使用前面注册成功的账号登录
        session.post(f"{base_url}/user/login", data={
            "email": "user@qq.com",
            "password": "123456"
        })

        # 发布正常的帖子
        post_data = {
            "title": "Pytest 自动化正常测试贴",
            "board_id": 1,
            "content": "<p>这是一条由自动化测试脚本发出的正常内容，用于验证业务正向流程。</p>"
        }
        res = session.post(f"{base_url}/post/public", data=post_data)

        # 验证结果
        assert res.status_code in [200, 302]

        # 去首页验证这条帖子是不是真的展示出来了
        index_res = requests.get(f"{base_url}")
        assert "Pytest 自动化正常测试贴" in index_res.text

    def test_create_comment(self, base_url):
        """测试正常发表评论（业务正向流程）"""
        session = requests.Session()

        # 登录
        session.post(f"{base_url}/user/login", data={
            "email": "admin@qq.com",
            "password": "123456"
        })

        # 发评论（假设对 ID 为 1 的帖子进行评论）
        comment_data = {
            "content": "<p>这是一条正常的测试评论，同意楼主的看法！</p>"
        }
        res = session.post(f"{base_url}/post/1/comment", data=comment_data)

        # 验证结果
        assert res.status_code == 200
        data = res.json()
        assert data.get("code") == 200
        assert "评论成功" in data.get("message", "")

    def test_send_normal_chat_message(self, base_url):
        """测试正常发送聊天消息（安全测试：防止非法 POST 攻击）"""
        session = requests.Session()

        # 登录
        session.post(f"{base_url}/user/login", data={
            "email": "admin@qq.com",
            "password": "123456"
        })

        # 尝试向展示页面的 /chat 发起 POST 发消息请求
        chat_data = {"content": "大家好啊，我是自动化测试机器人！", "type": "text"}
        res = session.post(f"{base_url}/chat", data=chat_data)

        # 断言：后端应该拒绝这个请求（返回 405），因为聊天页面只允许 GET 访问
        assert res.status_code == 405

    def test_upload_normal_image(self, base_url):
        """测试正常上传一张真实的合法图片（正向业务流程）"""
        session = requests.Session()

        # 登录
        session.post(f"{base_url}/user/login", data={"email": "admin@qq.com", "password": "123456"})

        # 伪造一张极小的合法 PNG 图片的二进制数据
        # 这是一个 1x1 像素的透明 PNG 图片
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'

        files = {
            'image': ('test_image.png', png_data, 'image/png')
        }

        # 上传
        upload_res = session.post(f"{base_url}/upload/image", files=files)

        # 断言：必须返回 200，且成功返回了图片 URL
        assert upload_res.status_code == 200
        data = upload_res.json()
        assert data.get("errno") == 0
        assert len(data.get("data")) > 0
        assert data.get("data")[0].get("url") is not None

        print("\n✅ 正常图片上传成功，返回 URL:", data.get("data")[0].get("url"))

    def test_comment_with_img_tag(self, base_url):
        """测试使用 [IMG][/IMG] 标签正常发评论（业务逻辑）"""
        session = requests.Session()

        # 登录
        session.post(f"{base_url}/user/login", data={"email": "admin@qq.com", "password": "123456"})

        # 伪造一个带 [IMG] 标签的评论
        comment_data = {
            "content": "<p>看看我刚上传的图片：[IMG]/static/upload/test_image.png[/IMG]</p>"
        }

        # 发评论（假设对 ID 为 1 的帖子发）
        res = session.post(f"{base_url}/post/1/comment", data=comment_data)

        # 验证结果
        assert res.status_code == 200
        assert res.json().get("code") == 200

    def test_search_api_success(self, base_url):
        """测试搜索接口（正向流程：根据关键字搜索）"""
        # 我们之前测试发帖时，发过一个叫 "Pytest 自动化正常测试贴" 的帖子
        # 我们用 "自动化" 作为关键字去搜，应该能搜到
        keyword = "自动化"
        res = requests.get(f"{base_url}/api/search?keyword={keyword}")

        # 断言：返回 200，并且 JSON 格式正确
        assert res.status_code == 200
        data = res.json()

        assert data.get("code") == 200
        assert "data" in data
        assert "total_pages" in data
        print(f"\n✅ 搜索 '{keyword}' 返回了 {len(data.get('data'))} 条结果")

    def test_search_api_empty_keyword(self, base_url):
        """测试搜索接口（异常流程：关键字为空）"""
        res = requests.get(f"{base_url}/api/search?keyword=")

        assert res.status_code == 200
        data = res.json()
        assert data.get("code") == 200
        assert len(data.get("data")) == 0
        assert data.get("total_pages") == 0

    def test_search_api_not_found(self, base_url):
        """测试搜索接口（异常流程：搜不到任何结果）"""
        keyword = "这是一个绝对搜不到的词汇_xyz12345"
        res = requests.get(f"{base_url}/api/search?keyword={keyword}")

        assert res.status_code == 200
        data = res.json()
        assert data.get("code") == 200
        assert len(data.get("data")) == 0