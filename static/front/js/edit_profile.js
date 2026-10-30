document.addEventListener('DOMContentLoaded', function() {
    const tagContainer = document.getElementById('tag-container');
    // 获取所有标签的 checkbox
    const checkboxes = document.querySelectorAll('.tag-checkbox');
    const MAX_SELECT = 5;

    // 核心函数：只负责禁用/解禁 checkbox
    function updateVisualStatus() {
        // 获取当前选中的数量
        const checkedCount = document.querySelectorAll('.tag-checkbox:checked').length;

        checkboxes.forEach(box => {
            // 如果选满了 5 个，且这个没被选中，就禁用（禁用的 input 浏览器会自动拦截点击）
            if (checkedCount >= MAX_SELECT && !box.checked) {
                box.disabled = true;
                box.parentElement.style.opacity = '0.5'; // 视觉变灰
                box.parentElement.style.cursor = 'not-allowed';
            } else {
                box.disabled = false;
                box.parentElement.style.opacity = '1';
                box.parentElement.style.cursor = 'pointer';
            }
        });
    }

    if (tagContainer) {
        // 使用 change 事件监听复选框的变化
        tagContainer.addEventListener('change', function(e) {
            if (e.target.classList.contains('tag-checkbox')) {

                const checkedCount = document.querySelectorAll('.tag-checkbox:checked').length;

                // 如果当前点了一下，数量超过上限了
                if (checkedCount > MAX_SELECT) {
                    alert('最多只能选择 5 个标签哦~');
                    // 把刚刚点击的那个取消选中
                    e.target.checked = false;
                    return;
                }

                // 每次点击后，更新一次视觉效果
                updateVisualStatus();
            }
        });
    }

    // 页面刚加载时，先执行一次（防止回显历史数据时超过 5 个）
    if (checkboxes.length > 0) {
        updateVisualStatus();

    const avatarInput = document.getElementById('avatar-input');
    const avatarPreview = document.getElementById('avatar-preview');

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    avatarPreview.src = e.target.result; // 替换预览图
                };
                reader.readAsDataURL(file);
            }
        });
    }

    }
});