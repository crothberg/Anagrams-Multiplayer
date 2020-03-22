window.onload = function() {
    $("#flip-action").focus();
    var socket = io();

    socket.on('connect', function() {
        socket.emit('json', {command: 'join_game', game_name: 'my_game'});
    });

    socket.on('json', function(data) {
        console.log(data);
    });

    $("#flip-action").on("keyup", function(event) {
        if (event.key == 'Enter') {
            console.log($(this).text)
        }
    });
}