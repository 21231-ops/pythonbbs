# PythonBBS - 基于 Flask 的全栈论坛系统

这是一个基于 Python Flask 框架从零开发的全栈 Web 论坛系统，包含前台用户端与后台 CMS 管理系统。项目已实现完整的本地开发与 Docker 容器化生产环境部署。

## 🌐 在线预览
*   **线上地址**：[http://127.0.0.1:8000](http://127.0.0.1:8000) *(注：此为本地启动后的默认地址，如需外网访问请自行配置反向代理)*
*   **测试账号**：管理员 `zhangsan@zlkt.net` / `123456`，普通用户 `mumu@qq.com` / `mumu123`

## ✨ 核心功能
*   **用户系统**：注册、登录、邮箱验证码找回密码、个人主页及资料修改。
*   **内容模块**：文章发布（支持富文本编辑器）、文章分类、评论、点赞、全站搜索。
*   **社交互动**：关注/粉丝系统、私信聊天、文章评论与互动。
*   **实时通讯**：集成 Flask-SocketIO，实现用户间的实时在线聊天及消息通知。
*   **后台管理 (CMS)**：基于 RBAC 权限控制，支持对用户、文章、评论、板块的批量管理与封禁/隐藏。
*   **异步任务**：使用 Celery + Redis 实现邮件异步发送，提升系统响应速度。

## 🛠️ 技术栈
*   **后端**：Python 3.10, Flask, Flask-SQLAlchemy, Flask-Login, Flask-SocketIO, Celery
*   **前端**：HTML5, CSS3, Bootstrap, JavaScript (jQuery), Quill 富文本编辑器
*   **数据库**：MySQL / SQLite, Redis (缓存与消息队列)
*   **部署**：Ubuntu 22.04, Docker, Docker Compose, Nginx, Gunicorn (gevent模式)

## 🚀 本地开发运行指南
1. 克隆项目：`git clone https://github.com/21231-ops/pythonbbs.git`
2. 创建并激活虚拟环境：`python -m venv venv` & `source venv/bin/activate` (Windows 使用 `venv\Scripts\activate`)
3. 安装依赖：`pip install -r requirements.txt`
4. 配置环境变量：复制 `.env.example` 为 `.env`，填入数据库、邮箱及 Redis 配置。
5. 初始化数据库：`flask db upgrade`
6. 运行项目：`flask run` 或 `python app.py`

## 📦 生产环境部署架构 (Docker 容器化部署)
本项目已实现基于 Docker 的现代化容器部署，确保开发与生产环境的一致性：
*   **应用容器化**：编写 `Dockerfile`，基于 `python:3.10-slim` 构建轻量级镜像。
*   **多服务编排**：使用 `docker-compose.yml` 一键启动 Web 服务 (Gunicorn + Flask) 和 Redis 容器。
*   **并发与异步支持**：使用 **Gunicorn** 作为 WSGI 服务器，并采用 **gevent** 模式完美支撑 Flask-SocketIO 的高并发 WebSocket 长连接。
*   **反向代理与静态资源**：使用 **Nginx** 作为反向代理，处理前端静态文件（CSS/JS/图片）并转发动态请求至 Docker 内部端口。
*   **数据持久化**：通过 Docker Volumes 将容器内的用户上传文件（`static/upload`）和数据库数据挂载到宿主机，保证数据安全。