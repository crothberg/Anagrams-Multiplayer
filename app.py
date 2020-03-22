from flask import Flask, render_template, request
from flask_socketio import SocketIO
import game_data
import ZODB, ZODB.FileStorage, transaction

app = Flask(__name__)
socketio = SocketIO(app)

#db_storage = ZODB.FileStorage.FileStorage('tmp_anagrams_online.db')

DATABASE_URL = os.environ['DATABASE_URL']
db = psycopg2.connect(DATABASE_URL, sslmode='require')

def setup_db():
    cur = db.cursor()
    cur.execute('CREATE TABLE USERS (                   \
                    SID INT PRIMARY KEY     NOT NULL,   \
                    NAME    TEXT            NOT NULL,   \
                    GAME    TEXT                    )')
    cur.execute('CREATE TABLE GAMES (                   \
                    NAME TEXT)')

setup_db(db)

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
    cur = db.cursor()
    #remove users
    cur.execute('DELETE FROM USERS WHERE SID = %s', (sid,))
    #remove newly empty games
    cur.execute('DELETE FROM GAMES WHERE NAME NOT IN (  \
                    SELECT NAME FROM USERS)'
def generate_game_state(cur, game_name):
    cur.execute('SELECT SID FROM USERS WHERE GAME = %s', (game_name,))
    num_users = len(cur.fetchall())
    return {'game_state' : {'num_users' : num_users}}

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
    flipped_tile, middle = None, None #flip_tile()
    socketio.emit(
        'tile_flipped',
        {'user': user, 'tile': flipped_tile, 'middle': middle}
    )

@socketio.on('steal')
def steal_word(args):
    user = args.get('user')
    word = args.get('word')
    source, updated_boards = None, None #steal_word()
    socketio.emit(
        'word_stolen',
        {'user': user, 'word': word, 'source': source, 'updated_boards': updated_boards}
    )

if __name__ == '__main__':
    socketio.run(app)
    app.run(debug=True)
