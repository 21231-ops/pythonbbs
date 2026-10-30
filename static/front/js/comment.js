$(function() {
    // 初始化 Quill
    var quill = new Quill('#comment-editor', {
        theme: 'snow',
        placeholder: '写下你的评论...',
        modules: {
            toolbar: [
                ['bold', 'italic', 'underline'],
                ['image'] // 只留图片按钮
            ]
        }
    });

    // 自定义图片上传逻辑（把 Base64 改为服务器上传）
    var toolbar = quill.getModule('toolbar');
    toolbar.addHandler('image', function() {
        // 弹出一个隐藏的 input 让用户选图片
        var input = document.createElement('input');
        input.setAttribute('type', 'file');
        input.setAttribute('accept', 'image/*');
        input.click();

        input.onchange = function() {
            var file = input.files[0];
            if (!file) return;

            var maxSize = 2 * 1024 * 1024;
            if (file.size > maxSize) {
                alert("图片太大了，请上传 2MB 以内的图片！");
                return;
            }

            var formData = new FormData();
            formData.append('image', file);
            var csrfToken = $("meta[name='csrf-token']").attr("content");
            if(csrfToken) formData.append('csrf_token', csrfToken);

            // 请求你的上传接口
            $.ajax({
                url: '/upload/image',
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(res) {
                    if (res.errno === 0 && res.data && res.data.length > 0) {
                        var imgUrl = res.data[0].url;
                        // 获取当前光标位置
                        var range = quill.getSelection(true);
                        // 把图片插入到 Quill 中
                        quill.insertEmbed(range.index, 'image', imgUrl);
                    } else {
                        alert("图片上传失败");
                    }
                }
            });
        };
    });

    // 提交评论
    $('#submit-comment-btn').on('click', function(e) {
        e.preventDefault();
        // 获取 Quill 里的 HTML 内容
        var contentHtml = quill.root.innerHTML;

        // 如果是空内容（Quill 默认空内容是 <p><br></p>）
        if (contentHtml === '<p><br></p>') {
            alert("评论内容不能为空！");
            return;
        }

        var postId = $('#submit-comment-btn').data('post-id');
        var csrfToken = $("meta[name='csrf-token']").attr("content");

        // 发给后端
        $.ajax({
            url: '/post/' + postId + '/comment',
            type: 'POST',
            data: {
                content: contentHtml,
                csrf_token: csrfToken
            },
            success: function(res) {
                if (res.code === 200) {
                    window.location.reload(); // 刷新页面看评论
                } else {
                    alert(res.message);
                }
            },
             error: function(xhr) {
                if (xhr.status === 400) {
                    alert(xhr.responseJSON.message);
                } else {
                    alert("网络错误");
                }
            }
        });
    });
});