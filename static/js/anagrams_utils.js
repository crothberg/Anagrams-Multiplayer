function make_middle(letters) {
    var middle = '';
    letters.foreach(letter =>
        middle += '<span class="tile">'+letter+'</span>'
    );
    return middle;
}

function make_player_list(words) {
    var player_list = '';
    words.foreach(function(word) {
        var word_display = '<div class="word">';
        word.foreach(function(letter) {
            word_display += '<span class="tile">'+letter+'</span>'
        });
        word_display += '</div>';
        player_list += word_display
    });
    return player_list;
}