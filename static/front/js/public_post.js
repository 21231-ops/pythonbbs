var editor = new window.wangEditor("#editor");
editor.config.uploadImgServer = "/front/upload/image";
editor.config.uploadFileName = "image";
editor.config.uploadImgMaxSize = 5 * 1024 * 1024;
editor.create();

$('#submit-btn').on('click', function (event) {
    event.preventDefault();

    var title = $("input[name='title']").val();
    var board_id = $("select[name='board_id']").val();
    var content = editor.txt.html();

    if (!title.trim()) {
            alert("标题不能为空！");
            return;
        }

    if (!content || content === '<p><br></p>') {
        alert("正文内容不能为空！");
        return;
    }

    zlajax.post({
        'url': '/post/public',
        'data': {title, board_id, content}
        }).done(function(data){
            setTimeout(function (){
                window.location = "/";
            },2000);
        }).fail(function(error){
            alert(error.message);
        });
});