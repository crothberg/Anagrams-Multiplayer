function make_player(player_name) {
    var player =
    `<div class="player">
        <div class="player-name">`+player_name+`</div>
        <div class="wordlist">`+make_wordlist()+`</div>
    </div>`
}

function make_middle(letters) {
    console.log(typeof letters)
    var middle = '';
    letters.forEach(letter =>
        middle += '<div class="tile"><span class="letter">'+letter+'</span></div>'
    );
    return middle;
}

function make_wordlist(words) {
    var wordlist = '';
    words.foreach(function(word) {
        var word_display = '<div class="word">';
        word.foreach(function(letter) {
            word_display += '<span class="tile">'+letter+'</span>'
        });
        word_display += '</div>';
        wordlist += word_display
    });
    return wordlist;
}