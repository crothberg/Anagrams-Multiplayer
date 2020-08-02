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

function make_all_players(user_list, user_scores) {
    $('.player-space').html('');
    // Object.keys(user_list).sort(function(p1, p2) {return user_list[p2].length - user_list[p1].length})
    for (const [idx, [player_name, player_words]] of Object.entries(Object.entries(user_list))) { 
        var score = user_scores[player_name]
        console.log('HERE', idx, player_name, score, player_words);
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