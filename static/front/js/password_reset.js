$(function () {
    $('#send-code-btn').on('click', function () {
        // 注意：获取输入框的值，你的 HTML 里需要有一个 name="email" 的输入框
        var email = $("input[name='email']").val().trim();
        if (!email) {
            alert("请输入邮箱！");
            return;
        }

        var $btn = $(this);
        $btn.prop('disabled', true).text('发送中...');

        // 用 zlajax 发送 GET 请求
        zlajax.get({
            'url': '/user/mail/password-reset',
            'data': {'mail': email},
            'success': function (result) {
                // 这里只保留一个 success 回调
                alert("验证码已发送，请查收邮件！");

                // 60 秒倒计时
                var countdown = 60;
                $btn.text(countdown + '秒后重试');
                var timer = setInterval(function () {
                    countdown--;
                    if (countdown > 0) {
                        $btn.text(countdown + '秒后重试');
                    } else {
                        clearInterval(timer);
                        $btn.prop('disabled', false).text('发送验证码');
                    }
                }, 1000);

            },
            'error': function (error) {
                alert("请求失败，请检查网络");
                $btn.prop('disabled', false).text('发送验证码');
            }
        });
    });
});

$(function () {
    $('#submit-reset-btn').on('click', function (e) {
        e.preventDefault();
        var $btn = $(this);
        $btn.prop('disabled', true).text('重置中...');

        // 获取表单数据（包含 csrf_token, code, new_password, confirm_new_password）
        var formData = $('#reset-form').serialize();

        // 须把上面输入的 email 也一起拼进去，否则后端找不到人
        var email = $("input[name='email']").val().trim();
        if (!email) {
            alert("请先在上方输入邮箱并获取验证码！");
            $btn.prop('disabled', false).text('确认重置密码');
            return;
        }
        formData += "&email=" + encodeURIComponent(email);

        // 发送 POST 请求给后端
        zlajax.post({
            'url': '/user/password_reset_verify',
            'data': formData,
            'success': function (result) {
                // 后端可能返回了类似 {"code": 200, "message": "..."}
                // 直接重定向，先看返回结果
                if (result.code === 200) {
                    alert("密码重置成功，请前往登录！");
                    // 如果后端给了跳转地址就跳，没给就手动跳到登录页
                    window.location.href = result.redirect_url;
                } else {
                    // 如果后端返回了错误信息（比如验证码错误、参数为空）
                    alert(result.message || "重置失败，请检查验证码！");
                    $btn.prop('disabled', false).text('确认重置密码');
                }
            },
            'error': function (error) {
                alert("网络请求失败或服务器异常");
                $btn.prop('disabled', false).text('确认重置密码');
            }
        });
    });
});