$(function () {
    // 1. 点击搜索按钮触发
    $('#search-btn').on('click', function () {
        doSearch(1); // 每次搜索都从第 1 页开始
    });

    // 2. 按回车键触发
    $('#search-input').on('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            doSearch(1); // 每次搜索都从第 1 页开始
        }
    });

    // 3. 核心搜索函数（带页码参数）
    window.doSearch = function(page) {
        var keyword = $('#search-input').val().trim();

        $.get('/api/search', { keyword: keyword, page: page }, function (result) {
            if (result.code === 200) {
                var postList = result.data;
                var html = '';

                // 如果没搜到
                if (postList.length === 0) {
                    html = '<li style="text-align:center; padding:20px; color:#999;">没有找到相关帖子~</li>';
                } else {
                    // 拼接列表（注意这里的 <a href> 我加了具体的帖子 ID）
                    postList.forEach(function (post) {
                        html += `
                            <li>
                                <div class="post-info-group">
                                    <p class="post-title">
                                        <a href="/posts/${post.id}">${post.title}</a>
                                    </p>
                                    <p class="post-info">
                                        <span>作者: ${post.author}</span>
                                        <span>发表时间: ${post.create_time}</span>
                                        <span>评论: ${post.comments_count}</span>
                                    </p>
                                </div>
                            </li>
                            <hr>
                        `;
                    });
                }

                // 替换列表
                $('#post-list-container').html(html);

                // 👈 动态生成底部分页
                renderPagination(result.total_pages, result.current_page);
            }
        });
    };

    // 4. 渲染分页组件的函数
    function renderPagination(totalPages, currentPage) {
        if (totalPages <= 1) {
            $('#pagination-container').html(''); // 只有一页就不显示分页
            return;
        }

        // 使用 Bootstrap 的分页样式
        var html = '<ul class="pagination mb-0">';

        // 上一页
        html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="javascript:void(0)" onclick="doSearch(${currentPage - 1})">上一页</a>
                 </li>`;

        // 页码 (为了不撑爆屏幕，可以用简单逻辑只显示前 5 页或者全部)
        for (let i = 1; i <= totalPages; i++) {
            html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                        <a class="page-link" href="javascript:void(0)" onclick="doSearch(${i})">${i}</a>
                     </li>`;
        }

        // 下一页
        html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="javascript:void(0)" onclick="doSearch(${currentPage + 1})">下一页</a>
                 </li>`;

        html += '</ul>';

        // 把拼接好的分页塞进坑位里
        $('#pagination-container').html(html);
    }
});