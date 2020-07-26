function make_player(player_name) {
    <div class="player">
        <div class="player-name">player_name</div>
        <div class="wordlist">
        </div>
    </div>
}

function make_middle(letters) {
    var middle = '';
    letters.foreach(letter =>
        middle += '<span class="tile">'+letter+'</span>'
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