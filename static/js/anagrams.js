window.onload = function() {

    var username = Cookies.get("username");
    if (!username) {
        alert('Please enter a username before joining a game.')
        window.location.href = '/';
    }

    var socket = io();
    var game_name = window.location.pathname.split('/').pop();

    socket.on('connect', function() {
        socket.emit('join_game', {'username': username, 'game_name': game_name});
    });

    socket.on('tile_flipped', function(data) {
        console.log(data);
        var middle = data['middle'];
        var status = data['status'];

        // // Update status
        // var determiner = 'a'
        // if ('erioasfhlx'.includes(letter)) {determiner='an'};
        // $('#status').text(user+' flipped '+determiner+' \''+letter+'\'');
        $('#status').text(status);

        // Update middle
        $('#middle').html(make_middle(middle));
    });

    socket.on('word_stolen', function(data) {
        console.log(data);
        user = data['user'];
        word = data['word'];
        source = data['source'];

        // Update status
        $('#status').text(user+' took the word \''+word+'\' from '+source+'!')
    });

    $("#flip-action").focus();
    $("#flip-action").submit(function(event) {
        // Get user input on press enter
        word = $("#flip-action-text").val();
        if (!word) {
            // If just enter (with no word), flip tile
            console.log('A letter has been flipped!')
            socket.emit('flip', {'user': username, 'room': game_name});
        } else {
            // If a word has been entered, try to steal it
            console.log('A word has been stolen!');
            socket.emit('steal', {'user': username, 'word': word});
        }
        // Clear input
        $("#flip-action-text").val('');
        // Prevent form from redirecting
        return false;
    });

    $("#chat-input-form").submit(function(event) {
        message = $("#chat-input").val();
        socket.emit('send_message', {'user': username, 'message': message, 'room': game_name})
        // Clear input
        $("#chat-input").val('');
        // Prevent form from redirecting
        return false;
    });
    socket.on("message_sent", function(data) {
        console.log(data);
        $("#chats").append(
            `<div class="message">
                <p class="message-sender">`+data['user']+`</p>
                <p class="message-body">`+data['message']+`</p>
            </div>`
        )
    });

    $("#undo").click(function() {
        socket.emit('undo');
    });

}