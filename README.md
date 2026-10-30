# PythonBBS - 基于 Flask 的全栈论坛系统

这是一个基于 Python Flask 框架从零开发的全栈 Web 论坛系统，包含前台用户端与后台 CMS 管理系统。项目已实现完整的生产环境部署。

## 🌐 在线预览
*   **线上地址**：[http://你的公网IP或域名](http://你的公网IP或域名) 
    *(注：如果服务器没买，可写：本地运行请参考下方部署指南)*
*   **测试账号**：管理员 `zhangsan@zlkt.net` / `123456`，普通用户 `mumu@qq.com` / `mumu123`

## ✨ 核心功能
*   **用户系统**：注册、登录、邮箱验证码找回密码、个人主页及资料修改。
*   **内容模块**：文章发布（支持富文本编辑器）、文章分类、评论、点赞、全站搜索。
*   **实时通讯**：集成 Flask-SocketIO，实现用户间的实时在线聊天及消息通知。
*   **后台管理 (CMS)**：基于 RBAC 权限控制，支持对用户、文章、评论、板块的批量管理与封禁/隐藏。
*   **异步任务**：使用 Celery + Redis 实现邮件异步发送，提升系统响应速度。

## 🛠️ 技术栈
*   **后端**：Python 3.10, Flask, Flask-SQLAlchemy, Flask-Login, Flask-SocketIO
*   **前端**：HTML5, CSS3, Bootstrap, JavaScript (jQuery), Quill 富文本编辑器
*   **数据库**：MySQL / SQLite (开发环境), Redis (缓存与消息队列)
*   **部署**：Ubuntu 22.04, Nginx, Gunicorn, Systemd

## 🚀 本地运行指南
1. 克隆项目：`git clone https://github.com/你的用户名/pythonbbs.git`
2. 创建并激活虚拟环境：`python -m venv venv` & `source venv/bin/activate`
3. 安装依赖：`pip install -r requirements.txt`
4. 配置环境变量：复制 `.env.example` (如果有) 为 `.env`，填入数据库及邮箱配置。
5. 初始化数据库：`flask db upgrade`
6. 运行项目：`flask run` 或 `python app.py`

## 📦 生产环境部署架构 (已实现)
*   使用 **Gunicorn** 作为 WSGI 服务器运行 Flask 应用。
*   使用 **Nginx** 作为反向代理服务器，处理静态文件并转发动态请求。
*   使用 **Systemd** 守护 Gunicorn 进程，实现开机自启与崩溃重启。