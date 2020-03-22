window.onload = function() {

    var socket = io();

    socket.on('connect', function() {
        socket.emit('json', {command: 'join_game', game_name: 'my_game'});
    });

    socket.on('json', function(data) {
        console.log(data);
    });

    socket.on('tile_flipped', function(data) {
        console.log(data);
    });
    socket.on('word_stolen', function(data) {
        console.log(data);
    });

    $("#flip-action").focus();
    $("#flip-action").submit(function(event) {
        // Get user input on press enter
        word = $("#flip-action-text").val();
        if (!word) {
            // If just enter (with no word), flip tile
            console.log('flipped!')
            socket.emit('flip', {'user': 'username_goes_here'});
        } else {
            // If a word has been entered, try to steal it
            console.log('stole!');
            socket.emit('steal', {'user': 'username_goes_here', 'word': word});
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