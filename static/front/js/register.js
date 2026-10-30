$(function () {
    $('#captcha-btn').on('click', function (event) {
        event.preventDefault();
        var $btn = $(this);
        var email = $("input[name='email']").val().trim();
        var emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
        if (!email) {
            alert("请先输入邮箱！");
            return;
        }
        if (!emailRegex.test(email)) {
            alert("邮箱格式不正确，请重新输入！");
            return;
        }

        $btn.prop('disabled', true).text('发送中...');
        zlajax.get({
            'url': '/user/mail/register',
            'data': {
                'mail': email
            },
            'success': function (result) {
                if (result.code === 200) {
                    // 成功发送
                    alert("验证码发送成功，请查收邮件！");
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
                } else {
                    alert(result.message);
                    $btn.prop('disabled', false).text('发送验证码');
                }
            },
            'error': function (error) {
                alert(error.message || "网络错误");
                $btn.prop('disabled', false).text('发送验证码');
            }
        });
    });

     $('#register-form').on('submit', function (event) {
        event.preventDefault(); // 阻止表单默认刷新页面

        var $btn = $('#submit-btn');
        $btn.prop('disabled', true).text('注册中...');

        var formData = $(this).serialize();

        zlajax.post({
            'url': '/user/register', // 对应后端的注册路由
            'data': formData,
            'success': function (result) {
                if (result.code === 200) {
                    alert("注册成功！即将跳转到登录页");
                    // 后端返回了 redirect_url，前端用 JS 跳转
                    window.location.href = result.redirect_url;
                } else {
                    // 如果后端返回了错误（比如验证码错误、邮箱已注册）
                    alert(result.message);
                    $btn.prop('disabled', false).text('立即注册');
                }
            },
            'error': function (error) {
                alert("网络错误或服务器异常");
                $btn.prop('disabled', false).text('立即注册');
            }
        });
    });
});

