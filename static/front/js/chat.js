const socket = io();
let pendingImageFile = null; // 用来暂存你选好但还没发送的图片
// 监听连接
socket.on("connect", () => console.log("WebSocket 已连接"));

// 获取 DOM
const chatBtn = document.getElementById('chat-btn');
const chatBox = document.getElementById('chat-box');
const closeBtn = document.getElementById('close-chat-btn');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const targetNameSpan = document.getElementById('chat-target-name');
const chatHeader = document.getElementById('chat-header');
const sideBar = document.getElementById('sidebar');
let isDragging = false;
let startX, startY, initialLeft, initialTop;
let currentTargetUserId = '';
let currentTargetUserName = '';
let currentTargetUserAvatar = '';


// 把发送逻辑提炼成全局函数
function sendMessage(overrideMsg = null) {
    // 如果 overrideMsg 是字符串，才去 trim；如果是图片 HTML，直接放行
    const rawMsg = overrideMsg || chatInput.value;
    if (!rawMsg) return;

    // 校验是不是空白文本
    if (typeof rawMsg === 'string' && !rawMsg.trim()) return;
    if (!currentTargetUserId) return;

    // 发给后端
    socket.emit("personal", {
        "to_user_id": currentTargetUserId,
        "message": rawMsg
    });

    // 如果之前显示的是“没有聊天记录”，发送时清空它
    if (chatMessages.innerHTML.includes('还没有聊天记录')) {
        chatMessages.innerHTML = '';
    }

    // 渲染到自己的屏幕上
    chatMessages.innerHTML += renderMessage({
        is_me: true,
        message: rawMsg
    });

    renderRecentUser();

    // 如果是文字消息（不是图片），清空输入框
    if (!overrideMsg) {
        chatInput.value = '';
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 提取出来的拉取历史记录函数
function loadChatHistory() {
    if (!currentTargetUserId) return;

    fetch(`/chat/history/${currentTargetUserId}`)
        .then(res => res.json())
        .then(data => {
            if (data.code === 200) {
                chatMessages.innerHTML = '';
                if (data.data.length === 0) {
                    chatMessages.innerHTML = '<div style="text-align:center; color:#999; font-size:12px;">还没有聊天记录，快发个消息吧~</div>';
                    return;
                }
                data.data.forEach(msg => {
                    chatMessages.innerHTML += renderMessage(msg)
                });
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        });
}

function renderMessage(msg) {
    const isMe = msg.is_me;
    const bgStyle = isMe ? 'msg-self' : 'msg-other';
    const senderId = isMe ? window.myInfo.id : (msg.from_user_id || currentTargetUserId);

    let avatarUrl = '';
    if (isMe) {
        avatarUrl = window.myInfo.avatar;
    } else if (msg.from_avatar && msg.from_avatar !== 'null') {
        avatarUrl = msg.from_avatar;
    } else if (currentTargetUserAvatar && currentTargetUserAvatar !== 'null') {
        avatarUrl = currentTargetUserAvatar;
    } else {
        avatarUrl = window.myInfo.defaultAvatar;
    }

    const flexStyle = isMe ? 'flex-direction: row-reverse;' : 'flex-direction: row;';

    let safeMessage = msg.message;
    let isImage = false;

    // 判断是不是带有 [IMG] 暗号的图片消息
    // 因为有时候外面可能会不小心包个 <p> 标签，所以用 includes 来查
    if (msg.message && msg.message.includes('[IMG]') && msg.message.includes('[/IMG]')) {
        isImage = true;
        // 提取里面的图片链接
        const match = msg.message.match(/\[IMG\](.*?)\[\/IMG\]/);
        if (match && match[1]) {
            const imgUrl = match[1];
            safeMessage = `<img src="${imgUrl}" style="max-width: 200px; max-height: 200px; border-radius: 5px;">`;
        }
    } else {
        // 如果没有暗号，说明是纯文本，全部转义（防手打攻击）
        safeMessage = msg.message
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;")
            .replace(/\n/g, "<br>");
    }

    const bubbleStyle = isImage
        ? 'display: inline-block; margin: 5px; max-width: 60%;'
        : 'display: inline-block; border:1px solid #ccc; margin:5px; max-width: 60%; padding: 8px 12px; border-radius: 8px; text-align: justify; overflow-wrap: anywhere; word-break: break-word;';

    return `
        <div style="display: flex; ${flexStyle} width: 100%; padding: 10px; box-sizing: border-box;">
            <div style="transform:translateY(5px)">
                <a href="/user/profile/${senderId}" style="text-decoration: none; flex-shrink: 0;">
                    <img src="${avatarUrl}" alt="头像" style="width: 40px; height: 40px; border-radius: 10%; object-fit: cover; border: 1px solid #eee; cursor: pointer;">
                </a>
            </div>

            <div style="${bubbleStyle}">
                <div>${safeMessage}</div>
            </div>
        </div>`;
}

function renderRecentUser() {
    fetch(`/api/recent_contacts`)
        .then(res => res.json())
        .then(data => {
            if (data.code === 200) {
               sideBar.innerHTML = '';
                if (data.data.length === 0) {
                    return;
                }
            }

            data.data.forEach(msg => {
                const avatarUrl = msg.avatar ? msg.avatar : window.myInfo.defaultAvatar
                sideBar.innerHTML += `
                    <div style="width: 50px; height: 50px;margin:10px auto">
                        <img src="${avatarUrl}" alt="头像" style="width: 45px; height: 45px; border-radius: 50%;
                         object-fit: cover; border: 1px solid #eee; cursor: pointer;" onclick="openChat('${msg.id}', '${msg.username}', '${msg.avatar}')" ">
                    </div>`
                });

        });
}

function openChat(userId, userName, userAvatar) {
    currentTargetUserId = userId;
    currentTargetUserName = userName;
    currentTargetUserAvatar = userAvatar;
    loadChatHistory()
    chatBox.style.display = 'block';
    targetNameSpan.innerText = currentTargetUserName;
    chatMessages.scrollTop = chatMessages.scrollHeight;

}

// 点击私信按钮初始化
if (chatBtn) {
    // 拿到按钮上的目标用户名
    currentTargetUserId = chatBtn.dataset.userId;
    currentTargetUserName = chatBtn.dataset.username;
    currentTargetUserAvatar = chatBtn.dataset.useravatar;
    loadChatHistory()

    chatBtn.addEventListener('click', function() {
        if (!currentTargetUserId) return;

        // 显示窗口，更新标题
        chatBox.style.display = 'block';
        targetNameSpan.innerText = currentTargetUserName;
        renderRecentUser()

        // 直接滚动到底部（因为历史记录在上面已经加载好了）
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
}

// 关闭弹窗
if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        chatBox.style.display = 'none';
    });
}

// 发送消息 (点击按钮 + 回车键)
if (sendBtn && chatInput) {
    // 绑定点击发送
    sendBtn.addEventListener('click', () => sendMessage());

    // 绑定回车发送
    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.isComposing) {
            event.preventDefault();
            sendMessage();
        }
    });
}

// 接收实时消息
socket.on("personal_msg", function(data) {
    if (data.is_me) return;

    renderRecentUser()
    // 如果发消息的人，正好是当前聊天对象
    if (data.from_user_id === currentTargetUserId) {

        // 清除“没有聊天记录”的占位提示
        if (chatMessages.innerHTML.includes('还没有聊天记录')) {
            chatMessages.innerHTML = '';
        }

        chatMessages.innerHTML += renderMessage(data)
        chatMessages.scrollTop = chatMessages.scrollHeight;

    }
});

// 弹窗拖拽功能
if (chatHeader && chatBox) {
    chatHeader.addEventListener('mousedown', function(e) {
        isDragging = true;
        startX = e.clientX;
        startY = e.clientY;
        const rect = chatBox.getBoundingClientRect();
        initialLeft = rect.left;
        initialTop = rect.top;
        // 防止拖拽时因为 right/bottom 的 css 定位导致跳动
        chatBox.style.right = 'auto';
        chatBox.style.bottom = 'auto';
        chatBox.style.left = initialLeft + 'px';
        chatBox.style.top = initialTop + 'px';
        e.preventDefault();
    });

    document.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        chatBox.style.left = (initialLeft + dx) + 'px';
        chatBox.style.top = (initialTop + dy) + 'px';
    });

    document.addEventListener('mouseup', function() {
        isDragging = false;
    });
}

$(function () {
    // 1. 监听文件选择框的点击和改变
    $('#chat-file-input').on('change', function () {
        var file = this.files[0];
        if (!file) return;

        var formData = new FormData();
        formData.append('image', file); // 对应后端 request.files.get('image')

        // 获取 CSRF Token（从base.html 的 meta 标签里拿）
        var csrfToken = $("meta[name='csrf-token']").attr("content");
        if(csrfToken) {
            formData.append('csrf_token', csrfToken);
        }

        // 发送 AJAX 请求，把图片传给后端
        $.ajax({
            url: '/upload/image', // 填后端的上传接口地址
            type: 'POST',
            data: formData,
            processData: false, // 必须 false
            contentType: false, // 必须 false
            success: function (res) {
            if (res.errno === 0 && res.data && res.data.length > 0) {
                var imgUrl = res.data[0].url;

                // 必须带 [IMG] 暗号发出去
                var imgHtml = '[IMG]' + imgUrl + '[/IMG]';
                sendMessage(imgHtml);

                $('#chat-file-input').val('');
            } else {
                alert("图片上传失败！");
            }
        },
            error: function () {
                alert("上传接口出错，请检查网络或登录状态");
            }
        });
    });

    window.openGlobalChat = function() {
        // 显示聊天框
        const chatBox = document.getElementById('chat-box');
        if (chatBox) {
            chatBox.style.display = 'block';
        }

        const chatMessages = document.getElementById('chat-messages');
        const targetNameSpan = document.getElementById('chat-target-name');
        chatMessages.innerHTML = '<div style="text-align:center; color:#999; font-size:12px; margin-top:20px;">加载中...</div>';

        // 调用函数去渲染左侧列表
        renderRecentUser();

        // 使用定时器等待 DOM 渲染完毕（因为 fetch 请求需要几十毫秒）
        setTimeout(function() {
            // 抓取左侧列表里的第一个头像图片
            const firstAvatar = document.querySelector('#sidebar img');

            if (firstAvatar) {
                // 如果找到图片，模拟点击它
                // 原来的 HTML 里写了 onclick="openChat(...)"，所以点击就能打开聊天
                firstAvatar.click();
            } else {
                chatMessages.innerHTML = '<div style="text-align:center; color:#999; font-size:12px; margin-top:20px;">还没有聊天记录，快发个消息吧~</div>';
                targetNameSpan.innerText = "私信";
            }
        }, 300);
    };

});