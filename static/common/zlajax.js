var zlajax = {
    'get': function (args) {
        args['method'] = 'get';
        return this.ajax(args);
    },
    'post': function (args) {
        args['method'] = 'post';
        return this.ajax(args);
    },
    'put': function (args) {
        args['method'] = 'put';
        return this.ajax(args);
    },
    'delete': function (args) {
        args['method'] = 'delete';
        return this.ajax(args);
    },
    'ajax': function (args) {
        // 设置 csrftoken
        this._ajaxSetup();
        return $.ajax(args);
    },
    '_ajaxSetup': function () {
        $.ajaxSetup({
            'beforeSend': function (xhr, settings) {
                // 如果不是 GET/HEAD/OPTIONS/TRACE 请求，并且不是跨域请求
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    // 从 meta 标签中获取 csrftoken
                    var csrftoken = $('meta[name=csrf-token]').attr('content');
                    // 将 csrftoken 设置到请求头中
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
    }
};