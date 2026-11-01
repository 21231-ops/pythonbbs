var editor = new window.wangEditor("#editor");
editor.config.uploadImgServer = "/front/upload/image";
editor.config.uploadFileName = "image";
editor.config.uploadImgMaxSize = 5 * 1024 * 1024;
editor.create();
// 声明一个全局的锁变量
var isSubmitting = false;
$('#submit-btn').on('click', function (event) {
    event.preventDefault();

    // 如果正在提交，直接拦截后续的疯狂点击
    if (isSubmitting) {
        return;
    }

    var title = $("input[name='title']").val();
    var board_id = $("select[name='board_id']").val();
    var content = editor.txt.html();
    var $btn = $(this);

    if (!title.trim()) {
            alert("标题不能为空！");
            return;
        }

    if (!content || content === '<p><br></p>') {
        alert("正文内容不能为空！");
        return;
    }

    // 上锁，并把按钮变灰，文字变成“发布中...”
    isSubmitting = true;
    $btn.prop('disabled', true).text('发布中...');

    zlajax.post({
        'url': '/post/public',
        'data': {title, board_id, content}
        }).done(function(data){
            setTimeout(function (){
                window.location = "/";
            },2000);
        }).fail(function(error){
            alert(error.message);
            // 失败：解锁并恢复按钮状态，让用户可以重新点击
            isSubmitting = false;
            $btn.prop('disabled', false).text('发布');
        });
});