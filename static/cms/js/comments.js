$(function () {
    function getCsrfToken() {
        return $("meta[name='csrf-token']").attr("content");
    }

    // 单条评论 隐藏/显示
    $('.active-btn').on('click', function (event) {
        event.preventDefault();
        var $this = $(this);
        var is_active = parseInt($this.attr("data-active"));
        var comment_id = $this.attr("data-comment-id");

        if (!confirm(is_active ? "您确定要隐藏此评论吗？" : "您确定要显示此评论吗？")) {
            return;
        }

        var data = {
            is_active: is_active ? 0 : 1,
            csrf_token: getCsrfToken()
        };

        $.ajax({
            url: '/cms/comments/active/' + comment_id,
            type: 'POST',
            data: data,
            success: function () {
                window.location.reload();
            },
            error: function (xhr) {
                alert("操作失败，状态码：" + xhr.status);
            }
        });
    });

    // 全选功能
    $('#check-all').on('change', function () {
        // 当全选框状态改变时，让所有下方的复选框状态与其保持一致
        $('.comment-checkbox').prop('checked', $(this).prop('checked'));
    });

    // 如果手动取消勾选了某一项，全选框也要跟着取消
    $('.comment-checkbox').on('change', function () {
        if ($('.comment-checkbox:checked').length === $('.comment-checkbox').length) {
            $('#check-all').prop('checked', true);
        } else {
            $('#check-all').prop('checked', false);
        }
    });

    // 批量隐藏
    $('#batch-hide-btn').on('click', function () {
        // 找出所有被选中，并且当前状态是“显示中”（data-active="1"）的评论ID
        var ids = [];
        $('.comment-checkbox:checked').each(function () {
            ids.push($(this).val());
        });

        if (ids.length === 0) {
            alert("请先勾选需要隐藏的评论！");
            return;
        }

        if (!confirm("确定要批量隐藏选中的 " + ids.length + " 条评论吗？")) {
            return;
        }

        sendBatchRequest(ids, 0);
    });

    // 批量显示
    $('#batch-show-btn').on('click', function () {
        // 找出所有被选中，并且当前状态是“隐藏中”（data-active="0"）的评论ID
        var ids = [];
        $('.comment-checkbox:checked').each(function () {
            ids.push($(this).val());
        });

        if (ids.length === 0) {
            alert("请先勾选需要显示的评论！");
            return;
        }

        if (!confirm("确定要批量显示选中的 " + ids.length + " 条评论吗？")) {
            return;
        }

        sendBatchRequest(ids, 1);
    });

    // 发送批量请求的公共函数
    function sendBatchRequest(ids, is_active) {
        $.ajax({
            url: window.location.pathname + '/batch_update', // 需要后端配合写这个接口
            type: 'POST',
            data: {
                ids: ids, // 传一个数组过去
                is_active: is_active,
                csrf_token: getCsrfToken()
            },
            success: function (res) {
                alert("批量操作成功！");
                window.location.reload();
            },
            error: function (xhr) {
                alert("批量操作失败，状态码：" + xhr.status);
            }
        });
    }
});