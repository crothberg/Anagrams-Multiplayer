from flask import Flask, render_template, request
from flask_socketio import SocketIO
import game_data
import ZODB, transaction

app = Flask(__name__)
socketio = SocketIO(app)

db = ZODB.DB('/tmp/anagrams_online.db')
if db.active_games is None:
    db.active_games = {}
    transaction.commit()

@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')

@app.route('/game', methods=['GET'])
def visit_game():
    return 'Currently in game: ' + request.args.get('game_name', None)

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

if __name__ == '__main__':
    socketio.run(app)
    app.run(debug=True)
