function make_player(player_name, score, words) {
    console.log('PLAYER NAME ', player_name);
    var player =
    `<div class="player">
        <div class="player-name"><span>`+player_name+`</span><span class="player-score">`+score+`</span></div>
        <div class="wordlist">`+make_wordlist(words)+`</div>
    </div>`
    return player
}

function make_middle(letters, letters_remaining) {
    var middle = '';
    letters.forEach(function(letter) {
        tilt = Math.floor(Math.random() * 17 ) - 8;
        middle += `<span class="tile" style="margin:4px; transform:rotate(`+tilt+`deg);">
            <span class="tile-3d"></span>    
            <span class="tile-letter">`+letter+`</span>
            <span class="tile-letter-overlay">`+letter+`</span>
        </span>`;
    });
    $('#letters-remaining').text(letters_remaining+' Letters Remaining')
    return middle;
}

function make_wordlist(words) {
    console.log('WORDS');
    console.log(words);
    console.log();
    var wordlist = '';
    words.forEach(function(word) {
        var word_display = '<div class="word">';
        word.split('').forEach(function(letter) {
            console.log(letter)
            word_display += `<span class="tile">
                <span class="tile-3d"></span>    
                <span class="tile-letter">`+letter+`</span>
                <span class="tile-letter-overlay">`+letter+`</span>
            </span>`;
        });
        word_display += '</div>';
        wordlist += word_display
    });
    return wordlist;
}

function make_all_players(user_list, user_scores, username) {
    $('.player-space').html('');
    console.log('UNORDERED:', user_list);
    var ordered_players = {};
    var sorted_usernames = Object.keys(user_list).sort(function(p1) {
        return (p1 == username)? -1 : 1;
    })
    sorted_usernames.forEach(function(key) {
        ordered_players[key] = user_list[key];
    });
    console.log('ORDERED:', ordered_players);
    for (const [idx, [player_name, player_words]] of Object.entries(Object.entries(ordered_players))) {
        var score = user_scores[player_name]
        var player = make_player(player_name, score, player_words);
        if (idx % 2 == 0) {
            $('#player-space-left').append(player);
        } else {
            $('#player-space-right').append(player);
        }
    }
}

function game_over() {
    $("body").css('background', 'black');
    $("body *").css('background', 'black');
    $("#header-bar *").css('color', 'white');
    $("#header-bar *").css('background', 'transparent');
    $("#header-bar *").css('z-index', '1');
    $(".player-space").css('z-index', '1');
    $("input").css('display', 'none');
    $("button").css('display', 'none');
    $("body").fireworks();
    setTimeout(function(){
        $("body").fireworks('destroy');
    }, 2000);
}