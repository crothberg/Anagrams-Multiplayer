var socket = io();

socket.on('connect', function() {
    socket.emit('json', {command: 'join_game', game_name: 'my_game'});
});

window.onload = function() {
    alert($("body").html());
    $("body").addEventListener("keyup", function(event) {
        alert('pressed enter!');
    });
}