window.onload = function() {

    $("#flip-action").focus();
    var socket = io();

    socket.on('connect', function() {
        socket.emit('json', {command: 'join_game', game_name: 'my_game'});
    });

    socket.on('json', function(data) {
        console.log(data);
    });

    $("#flip-action").submit(function(event) {
        // Get user input on press enter
        word = $("#flip-action-text").val();
        if (!word) {
            // If just enter (with no word), flip tile
            socket.emit('flip');
        } else {
            // If a word has been entered, try to steal it
            socket.emit('steal', {'word': word});
        }
        // Clear input
        $("#flip-action-text").val('');
        // Prevent form from redirecting
        return false;
    });

    $("#contest").click(function() {
        socket.emit('contest');
    });

}