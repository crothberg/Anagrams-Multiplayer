from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
import flask_socketio
import game_data
import psycopg2
import os
import json

app = Flask(__name__)
socketio = SocketIO(app)

#db_storage = ZODB.FileStorage.FileStorage('tmp_anagrams_online.db')
#To run locally on Windows: set DATABASE_URL= user='postgres' host='localhost'

DATABASE_URL = os.environ['DATABASE_URL']
db = psycopg2.connect(DATABASE_URL, sslmode='allow')

def setup_db():
    cur = db.cursor()
    cur.execute('CREATE TABLE USERS (                   \
                    NAME    TEXT            NOT NULL,   \
                    GAME    TEXT                    )')
    cur.execute('CREATE TABLE GAMES (                   \
                    NAME TEXT               NOT NULL,   \
                    STATE TEXT )')

setup_db()

@app.route('/')
def hello():
    return render_template('index.html')
@app.route('/status')
def get_status():
    cur = db.cursor('SELECT * FROM GAMES')
    game_status = cur.fetchall()
    return json.dumps(game_status)

@app.route('/game', methods=['POST'])
def redirect_to_game():
    return redirect('/game/'+request.form['game_name'])

@app.route('/game/<game_name>')
def visit_game(game_name):
    return render_template('game.html', game_name=game_name)

@socketio.on('disconnect')
def user_disc():
    pass
    cur = db.cursor()
    #remove users
    #cur.execute('DELETE FROM USERS WHERE SID = %s', (sid,))
    #remove newly empty games
    #cur.execute('DELETE FROM GAMES WHERE NAME NOT IN (  \
    #                SELECT NAME FROM USERS)')

@socketio.on('join_game')
def join_game(data):
    username = data['username']
    game_name = data['game_name']
    cur = db.cursor()
    cur.execute('SELECT NAME FROM GAMES WHERE NAME = %s', (game_name,))
    game_state_str = cur.fetchone()
    game_state = None
    if game_state_str is None:
        ##create the game:
        cur.execute('INSERT INTO GAMES (NAME) VALUES (%s)', (game_name,))
        game_state = game_data.game_room(username)
    else:
        game_state = game_data.deserialize_game_room(json.loads(game_state_str))
        if game_state.has_user(username):
            return None

    cur.execute('INSERT INTO USERS (NAME, GAME) VALUES (%s, %s)', (username, game_name))

    cur.execute('UPDATE GAMES SET STATE = %s WHERE NAME = %s', (json.dumps(game_state.generate_game_state()), game_name))

    flask_socketio.join_room(game_name)
    state_update = game_state.generate_game_state()
    socketio.emit('json', state_update, room = game_name)

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

@socketio.on('send_message')
def send_message(args):
    user = args.get('user')
    message = args.get('message')
    socketio.emit(
        'message_sent',
        {'user': user, 'message': message}
    )

if __name__ == '__main__':
    socketio.run(app)
    #app.run(debug=True)
