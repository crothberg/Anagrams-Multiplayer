from flask import Flask, render_template, request
from flask_socketio import SocketIO
import game_data
import ZODB, ZODB.FileStorage, transaction

app = Flask(__name__)
socketio = SocketIO(app)

#db_storage = ZODB.FileStorage.FileStorage('tmp_anagrams_online.db')
db = ZODB.DB(None)
try:
    active_games = db.active_games
except AttributeError:
    db.active_games = {}
    transaction.commit()

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/<game_name>')
def visit_game(game_name):
    return render_template('game.html', game_name=game_name)

@socketio.on('json')
def json_dispacher(json):
    if(json.get('command') == 'join_game'):
        join_game(json)

@socketio.on('disconnect')
def user_disc():
    sid = request.sid
    #TODO: This is slow fix later with user -> game map
    for game_name in db.active_games:
        game = db.active_games[game_name]
        game.remove_user(sid)
        if game.num_users == 0:
            del db.active_games[game_name]

    transaction.commit()


def join_game(command):
    game_name = command.get('game_name')
    username = ''
    sid = request.sid
    user = game_data.user(username, sid)
    game_obj = db.active_games.get(game_name)
    if game_obj is None:
        ##create the game:
        game_obj = game_data.game_room(user)
        db.active_games[game_name] = game_obj

    game_obj.add_user(user)
    transaction.commit()

    new_state = game_obj.generate_game_state()
    for user in game_obj.active_users:
        socketio.emit('json', new_state, room = user.sid)

@socketio.on('flip')
def flip_tile(args):
    user = args.get('user')
    flipped_tile, middle = flip_tile()
    socketio.emit(
        'tile_flipped',
        {'user': user, 'tile': flipped_tile, 'middle': middle}
    )

@socketio.on('steal')
def flip_tile(args):
    user = args.get('user')
    word = args.get('word')
    flipped_tile, updated_boards = flip_tile()
    socketio.emit(
        'word_stolen',
        {'user': user, 'tile': flipped_tile, 'updated_boards': updated_boards}
    )

if __name__ == '__main__':
    socketio.run(app)
    app.run(debug=True)
