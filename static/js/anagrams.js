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

    socket.emit('get_game_state', {'game_name': game_name});

    socket.on('user_added', function(data) {
        $("#player-space").append(make_player(data['username']));
    });

    socket.on('game_state_update', function(data) {

        console.log('GAME STATE UPDATED')
        console.log(data);
        var status = data['status'];
        var users = data['game_state']['users'];
        var middle = data['game_state']['middle'];
        var scores = data['game_state']['scores'];
        var letters_remaining = data['game_state']['letters_remaining'];
        
        // Update status
        $('#status').text(status);
        
        // Update middle
        $('#middle').html(make_middle(middle, letters_remaining));
        
        // Update all users simultaneously
        $("#player-space").html(make_all_players(users, scores));

        console.log('LETTERS REMAINING:', letters_remaining);

        // if (letters_remaining == 0) {
        //     game_over()
        // }
    });

    $("#flip-action").focus();
    $("#flip-action").submit(function(event) {

        // Get user input on press enter
        word = $("#flip-action-text").val().toUpperCase();
        if (!word) {
            // If just enter (with no word), flip tile
            socket.emit('flip', {'user': username, 'room': game_name});
            console.log('Flip request sent.')
        } else {
            // If a word has been entered, try to steal it
            console.log('A word has been stolen!');
            socket.emit('steal', {'user': username, 'room': game_name, 'word': word});
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

    socket.on('challenge', function(data) {
        console.log('Challege initiated.')
        $("#challenge-status").text(data['status']);
        $("#modal-background").show('fade', 'slow');
        $("#challenge-modal").show('bounce', {times: 1}, 'slow');
    });

    $("#challenge").click(function() {
        socket.emit('challenge', {'room': game_name, 'user': username});
        console.log('Challenge request sent.')
    });

    $("#vote-yes").click(function() {
        socket.emit('vote', {'room': game_name, 'user': username, 'vote': 'accept'});
        $("#modal-background").hide('fade', 'slow');
        $("#challenge-modal").hide('drop', {direction: 'up'}, 'slow');
        console.log('Voted accept.')
    });

    $("#vote-no").click(function() {
        socket.emit('vote', {'room': game_name, 'user': username, 'vote': 'reject'});
        $("#modal-background").hide('fade', 'slow');
        $("#challenge-modal").hide('drop', {direction: 'up'}, 'slow');
        console.log('Voted reject.')
    });

}