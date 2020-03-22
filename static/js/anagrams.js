var socket = io();

socket.on('connect', function() {
    socket.emit('my event', {data: 'I\'m connected!'});
});

$(document).ready(function(){
    $("body").addEventListener("keyup", function(event) {
        alert('pressed enter!');
    });
});