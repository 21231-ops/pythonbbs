$(function() {
    var socket = io();
    socket.on('update_online_count', function (data) {
        var countElement = document.getElementById('online-count-text');
        if (countElement) {
            countElement.innerText = data.count + ' 人';
        }
    });
});