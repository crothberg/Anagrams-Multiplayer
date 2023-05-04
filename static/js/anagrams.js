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
    var typing_start_time = 0;

    socket.on('connect', function() {
        socket.emit('join_game', {'username': username, 'game_name': game_name});
    });

    socket.on('game_joined', function() {
        socket.emit('get_game_state', {'game_name': game_name});
    });

    socket.on('user_added', function(data) {
        $("#player-space").append(make_player(data['username']));
        $('audio#join')[0].play(); 
    });

    socket.on('game_state_update', function(data) {

        console.log('GAME STATE UPDATED')
        console.log(data);
        var status = data['status'];
        var users = data['game_state']['users'];
        var middle = data['game_state']['middle'];
        var scores = data['game_state']['scores'];
        var letters_remaining = data['game_state']['letters_remaining'];
        var history = data['game_state']['prev_source'];
        var event = data['event'];
        
        if (!data['game_state']['challenge']) {
            hide_modal();
        }

        var delay = 0;
        play_flip = false;
        if (event == 'flip') {
            delay = 3;
            typing_start_time = 0;
        } else if (event == 'steal') {
            $('audio#steal')[0].play();
        } else if (event == 'self_challenge') {
            //pass
        } else if (event == 'end_challenge') {
            //pass
        }
        
        // Update middle
        if (delay == 0) {
            $('#middle').html(make_middle(middle, letters_remaining));
            // Update status
            $('#status').text(status);
        } else {
            $('#status').text('Flipping in '+delay);
            delay -= 1;
        }
        var flip_timer = setInterval(function() {
            if (delay == 1) {
                play_flip = true;
            }
            if (delay > 0) {
                $('#status').text('Flipping in '+delay);
                delay -= 1;
            } else {   
                if (play_flip) {
                    $('audio#flip')[0].play();
                }
                $('#middle').html(make_middle(middle, letters_remaining));
                // Update status
                $('#status').text(status);
                clearInterval(flip_timer);
            }
        }, 400);
        
        // Update all users simultaneously
        $("#player-space").html(make_all_players(users, scores, username));

        console.log('LETTERS REMAINING:', letters_remaining);

        // if (letters_remaining == 0) {
        //     game_over()
        // }
        
        // Update history
        make_history(history);

        $('.word').click(function() {
            socket.emit('challenge', {'room': game_name, 'user': username, 'target_user': this.getAttribute('player'), 'word': this.getAttribute('word')});
        });
    });

    $("#flip-action").focus();
    function submit_word() {
        // Get user input on press enter
        word = $("#flip-action-text").val().toUpperCase();
        if (!word) {
            // If just enter (with no word), flip tile
            socket.emit('flip', {'user': username, 'room': game_name});
            console.log('Flip request sent.')
        } else {
            // If a word has been entered, try to steal it
            var typing_end_time = new Date().getTime();
            var typing_time = typing_end_time - typing_start_time;
            console.log('TIME:', typing_time);
            console.log('A word has been stolen!');
            socket.emit('steal', {'user': username, 'room': game_name, 'word': word, 'start_time': typing_start_time, 'typing_time': typing_time});
        }
        // Clear input
        $("#flip-action-text").val('');
    }

    $( "#flip-action-text" ).keydown(function(e) {
        var key = e.keyCode;
        if ((key < 65 || key > 90) && !([8, 17, 18, 9, 116, 189, 187, 16, 191].includes(key))) {
            e.preventDefault();
        } else {
            if (!typing_start_time) {
                typing_start_time = new Date().getTime();
            }
        }
        if ([8, 17].includes(key)) {
            typing_start_time = 0;
        }
        if ([32, 13].includes(key)) {
            submit_word();
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
        }
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
            $("#history").delay(300).slideToggle();
            history_open = true;
            $("#chatbar").delay(200).slideUp();
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

    function make_history(history_states) {
        $('#history').html('');
        history_states.reverse().slice(0, 10).forEach(function(item) {
            // if (item[3].length) {
            //     source = item[3][0][0] + '\'s word ' + item[3][0][1];
            // } else {
            //     source = 'the middle';
            // }
            var text = item[0] + ' stole ' + item[1]// + ' from ' + source;
            $('#history').append(`<p class="history-item" player="` + item[0] + `" + word="` + item[1] + `">` + text + `</p>`);
        });
    
        $(".history-item").click(function() {
            console.log(this);
            socket.emit('challenge', {'room': game_name, 'user': username, 'target_user': this.getAttribute('player'), 'word': this.getAttribute('word')});
        });
    }

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