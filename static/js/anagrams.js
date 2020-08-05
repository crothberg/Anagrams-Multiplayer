window.onload = function() {

    var username = Cookies.get("username");
    if (!username) {
        alert('Please enter a username before joining a game.')
        window.location.href = '/';
    }

    var socket = io();
    var game_name = window.location.pathname.split('/').pop();
    var nav_open = false;
    var chat_open = false;
    var history_open = false;
    var voted = false;

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
        
        if (!data['game_state']['challenge']) {
            hide_modal();
        }

        $('audio#flip')[0].play()
        // if (data['game_state']['event'] == 'flip') {
        //     $('audio#flip')[0].play()
        // } else if (data['game_state']['event'] == 'steal') {
        //     $('audio#steal')[0].play()
        // }
        
        // Update status
        $('#status').text(status);
        
        // Update middle
        $('#middle').html(make_middle(middle, letters_remaining));
        
        // Update all users simultaneously
        $("#player-space").html(make_all_players(users, scores, username));

        console.log('LETTERS REMAINING:', letters_remaining);

        // if (letters_remaining == 0) {
        //     game_over()
        // }
        
        $('.word').click(function() {
            socket.emit('challenge', {'room': game_name, 'user': username, 'target_user': this.getAttribute('player'), 'word': this.getAttribute('word')});
        });
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

    $( "#flip-action-text" ).keydown(function(e) {
        var key = e.keyCode;
        if ((key < 65 || key > 90) && !([8, 13, 17, 189, 187, 16, 191].includes(key))) {
            e.preventDefault();
        }
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
        if (!(chat_open)) {
            $("#chat-icon .icon-overlay").show();
        }
        console.log(data);
        $("#chats").append(
            `<div class="message">
                <p class="message-sender">`+data['user']+`</p>
                <p class="message-body">`+data['message']+`</p>
            </div>`
        )
    });

    socket.on('challenge', function(data) {
        $("#challenge-status").text(data['status']);
        $("#modal-background").show('fade', 'slow');
        $("#challenge-modal").show('bounce', {times: 1}, 'slow');
    });

    socket.on('vote_cast', function(data) {
        var no_votes = '';
        var yes_votes = '';
        votes = JSON.parse(data['votes']);
        Object.values(votes).forEach(function(vote) {
            console.log('VOTE', vote);
            if (vote == 1) {
                no_votes += '✋';
            }
            else if (vote == -1) {
                yes_votes += '✋';
            }
        });
        $("#no-votes").text(no_votes);
        $("#yes-votes").text(yes_votes);
    })

    $("#undo").click(function() {
        socket.emit('undo', {'room': game_name});
    });
    $("#redo").click(function() {
        socket.emit('redo', {'room': game_name});
    });

    function hide_modal() {
        $("#modal-background").hide('fade', 'slow');
        $("#challenge-modal").hide('drop', {direction: 'up'}, 'slow');
        $("#flip-action-text").focus();
        $("#challenge-status").text('')
        $("#challenge-question").text('How do you vote?')
        $(".vote").css('background', 'white');
        $(".vote").css('color', 'black');
        $("#no-votes").text('');
        $("#yes-votes").text('');
        voted = false;
    }

    $("#vote-yes").click(function() {
        if (!voted) {
            socket.emit('vote', {'room': game_name, 'user': username, 'vote': 'accept'});
            $("#challenge-status").text('You voted "It\'s a word."')
            $("#challenge-question").text('')
            $(".vote").css('background', 'lightgray');
            $(".vote").css('color', 'darkgray');
            voted = true;
            console.log('Voted accept.')
        }
    });

    $("#vote-no").click(function() {
        if (!voted) {
            socket.emit('vote', {'room': game_name, 'user': username, 'vote': 'reject'});
            $("#challenge-status").text('You voted "It\'s not a word."')
            $("#challenge-question").text('')
            $(".vote").css('background', 'lightgray');
            $(".vote").css('color', 'darkgray');
            voted = true;
            console.log('Voted reject.')
        }
    });

    $(".history-item").click(function() {
        console.log(this);
    });


    $("#chat-icon").click(function() {
        if (!(nav_open)) {
            $("#chatbar").delay(200).slideToggle();
            chat_open = true;
            $("#chat-icon .icon-overlay").hide();
            $("#history").delay(200).slideUp();
            history_open = false;
        }
    })
    $("#history-icon").click(function() {
        if (!(nav_open)) {
            $("#history").delay(100).slideToggle();
            history_open = true;
            $("#chatbar").delay(100).slideUp();
            chat_open = false;
        }
    })
    $("#nav-toggle, #right-nav * .icon").click(function() {
        if (!nav_open) {
            $("#nav-toggle").animate(
                { deg: 180 },
                {
                duration: 500,
                    step: function(now) {
                        $(this).css({ transform: 'rotate(' + now + 'deg)' });
                    }
                }
            );
            $("#right-nav * h2").animate({'width': '250px'});
            $("#right-nav * .icon").animate({
                'border-top-left-radius': '3px',
                'border-top-right-radius': '0px',
                'border-bottom-left-radius': '0px',
                'border-bottom-right-radius': '0px'
            });
            nav_open = true;
        } else {
            $("#nav-toggle").animate(
                { deg: -360 },
                {
                duration: 500,
                    step: function(now) {
                        $(this).css({ transform: 'rotate(' + now + 'deg)' });
                    }
                }
            );
            $("#right-nav * h2").animate({'width': '0px'});
            $("#right-nav * .icon").animate({'border-radius': '20px'});
            $("#chatbar").hide();
            chat_open = false;
            $("#history").hide();
            history_open = false;
            nav_open = false;
        }
    });
    $("#chat-title").click(function(){
        $("#chatbar").slideToggle();
        chat_open = !(chat_open);
        $("#chat-icon .icon-overlay").hide();
        $("#history").slideUp();
        history_open = false;
    });
    $("#history-title").click(function(){
        $("#history").slideToggle();
        history_open = !(history_open);
        $("#chatbar").slideUp();
        chat_open = false;
    });

    $("#share-game").click(function() {
        var copyText = document.getElementById("current-url");
        copyText.type = 'text';
        copyText.value = window.location.href;
        copyText.select();
        document.execCommand("copy");
        copyText.type = 'hidden';
        alert('URL copied to clipboard!')
    });

    $("#leave-game").click(function() {
        window.location.href = '/';
    })

}