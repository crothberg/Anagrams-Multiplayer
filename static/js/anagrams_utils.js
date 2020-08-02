function make_player(player_name, words) {
    console.log('PLAYER NAME ', player_name);
    var player =
    `<div class="player">
        <div class="player-name">`+player_name+`</div>
        <div class="wordlist">`+make_wordlist(words)+`</div>
    </div>`
    return player
}

function make_middle(letters) {
    console.log(typeof letters)
    var middle = '';
    letters.forEach(function(letter) {
        tilt = Math.floor(Math.random() * 17 ) - 8;
        middle += `<span class="tile" style="margin:4px; transform:rotate(`+tilt+`deg);">
            <span class="tile-3d"></span>    
            <span class="tile-letter">`+letter+`</span>
            <span class="tile-letter-overlay">`+letter+`</span>
        </span>`;
    });
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

function make_all_players(user_list) {
    $('.player-space').html('');
    // Object.keys(user_list).sort(function(p1, p2) {return user_list[p2].length - user_list[p1].length})
    for (const [idx, [player_name, player_words]] of Object.entries(Object.entries(user_list))) { 
        console.log('HERE', idx, player_name, player_words);
        var player = make_player(player_name, player_words);
        if (idx % 2 == 0) {
            $('#player-space-left').append(player);
        } else {
            $('#player-space-right').append(player);
        }
    }
}