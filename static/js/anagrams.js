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

    socket.on('user_added', function(data) {
        $("#player-space").append(make_player(data['username']));
    });

    socket.on('game_state_update', function(data) {
        console.log(data);
        var status = data['status'];
        game_state = JSON(data['game_state']);
        console.log(game_state)
        var users = data['users'];
        var middle = data['middle'];
        
        // // Update status
        // var determiner = 'a'
        // if ('erioasfhlx'.includes(letter)) {determiner='an'};
        // $('#status').text(user+' flipped '+determiner+' \''+letter+'\'');
        $('#status').text(status);
        
        // Update all users simultaneously
        $("#player-space").html(make_player_spaces(data['users']));
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