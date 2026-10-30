$(function () {
    function getCsrfToken() {
        return $("meta[name='csrf-token']").attr("content");
    }

    // 单条评论 隐藏/显示
    $('.active-btn').on('click', function (event) {
        event.preventDefault();
        var $this = $(this);
        var is_active = parseInt($this.attr("data-active"));
        var user_id = $this.attr("data-user-id");

        if (!confirm(is_active ? "您确定要禁用此用户吗？" : "您确定要恢复此用户吗？")) {
            return;
        }

        var data = {
            is_active: is_active ? 0 : 1,
            csrf_token: getCsrfToken()
        };

        $.ajax({
            url: '/cms/users/active/' + user_id,
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
        $('.user-checkbox').prop('checked', $(this).prop('checked'));
    });

    // 如果手动取消勾选了某一项，全选框也要跟着取消
    $('.user-checkbox').on('change', function () {
        if ($('.user-checkbox:checked').length === $('.user-checkbox').length) {
            $('#check-all').prop('checked', true);
        } else {
            $('#check-all').prop('checked', false);
        }
    });

    // 批量禁用
    $('#batch-hide-btn').on('click', function () {
        // 找出所有被选中，并且当前状态是“显示中”（data-active="1"）的评论ID
        var ids = [];
        $('.user-checkbox:checked').each(function () {
            ids.push($(this).val());
        });

        if (ids.length === 0) {
            alert("请先勾选需要禁用的用户！");
            return;
        }

        if (!confirm("确定要批量禁用选中的 " + ids.length + " 个用户吗？")) {
            return;
        }

        sendBatchRequest(ids, 0);
    });

    // 批量恢复
    $('#batch-show-btn').on('click', function () {
        // 找出所有被选中，并且当前状态是“隐藏中”（data-active="0"）的评论ID
        var ids = [];
        $('.user-checkbox:checked').each(function () {
            ids.push($(this).val());
        });

        if (ids.length === 0) {
            alert("请先勾选需要恢复的用户！");
            return;
        }

        if (!confirm("确定要批量恢复选中的 " + ids.length + " 个用户吗？")) {
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