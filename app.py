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
                    SID     TEXT            NOT NULL,   \
                    GAME    TEXT                    )')
    cur.execute('CREATE TABLE GAMES (                   \
                    NAME TEXT               NOT NULL,   \
                    STATE TEXT )')
    cur.execute('CREATE TABLE LOGS  (                   \
                    LOG_LINE TEXT           NOT NULL,   \
                    TIME TIMESTAMP          NOT NULL)')

setup_db()

@app.route('/')
def hello():
    return render_template('index.html')
@app.route('/status')
def get_status():
    cur = db.cursor()
    cur.execute('SELECT * FROM GAMES')
    game_status = cur.fetchall()
    cur.execute('SELECT * FROM USERS')
    user_status = cur.fetchall()
    return json.dumps(game_status) + '<br>' + json.dumps(user_status)

@app.route('/game', methods=['POST'])
def redirect_to_game():
    return redirect('/game/'+request.form['game_name'])

@app.route('/game/<game_name>')
def visit_game(game_name):
    return render_template('game.html', game_name=game_name)

@app.route('/logs')
def get_logs():
    cur = db.cursor()
    cur.execute('SELECT LOG_LINE, TIME FROM LOGS ORDER BY TIME DESC LIMIT 30')
    logs = cur.fetchall()
    return '<br>'.join(['%s: %s' % (log_line[1], log_line[0]) for log_line in logs])

@socketio.on('disconnect')
def user_disc():
    sid = request.sid
    cur = db.cursor()
    cur.execute('SELECT NAME, GAME FROM USERS WHERE SID = %s', (sid,))
    user_data = cur.fetchone()
    if user_data is None:
        print_log_line('Phantom sid tried to disconnect: %s' % (sid,))
        return
    username = user_data[0]
    game = user_data[1]
    print_log_line('User %s (%s) leaving %s' % (username, sid, game))
    cur.execute('SELECT STATE FROM GAMES WHERE NAME = %s', (game,))
    game_state_str = cur.fetchone()
    if game_state_str is None:
        print_log_line('Missing game data: %s' % (game,))
        return
    game_state = game_data.deserialize_game_room(json.loads(game_state_str[0]))
    game_state.remove_user(username)
    if game_state.num_users() == 0:
        cur.execute('DELETE FROM GAMES WHERE NAME = %s', (game,))
    else:
        cur.execute('UPDATE GAMES SET STATE = %s WHERE NAME = %s', (json.dumps(game_state.generate_game_state()), game))

    cur.execute('DELETE FROM USERS WHERE SID = %s', (sid,))

@socketio.on('join_game')
def join_game(data):
    sid = request.sid
    username = data['username']
    game_name = data['game_name']
    print_log_line('user %s (%s) joining game %s' % (username, sid, game_name))
    cur = db.cursor()
    cur.execute('SELECT STATE FROM GAMES WHERE NAME = %s', (game_name,))
    game_state_str = cur.fetchone()
    game_state = None
    if game_state_str is None:
        ##create the game:
        cur.execute('INSERT INTO GAMES (NAME) VALUES (%s)', (game_name,))
        game_state = game_data.game_room(username)
    else:
        print_log_line('gss: %s' % (game_state_str[0],))
        game_state = game_data.deserialize_game_room(json.loads(game_state_str[0]))
        if game_state.has_user(username):
            return None
        game_state.add_user(username)

    cur.execute('INSERT INTO USERS (NAME, SID, GAME) VALUES (%s, %s, %s)', (username, sid, game_name))

    cur.execute('UPDATE GAMES SET STATE = %s WHERE NAME = %s', (json.dumps(game_state.generate_game_state()), game_name))

    flask_socketio.join_room(game_name)
    state_update = game_state.generate_game_state()
    socketio.emit('json', state_update, room = game_name)

@socketio.on('flip')
def flip_tile(args):
    user = args.get('user')
    game = args.get('room')
    cur = db.cursor()
    cur.execute('SELECT STATE FROM GAMES WHERE NAME = %s', (room,))
    game_state_str = cur.fetchone()
    if game_state_str is None:
        print_log_line('user %s attempted to acces missing room %s' % (user, game))
        return

    game_state = game_data.deserialize_game_room(json.loads(game_state_str[0]))
    flipped_tile = game_state.flip_tile()
    new_state = json.dumps(game_state.generate_game_state())
    socketio.emit(
        'tile_flipped',
        {'user': user, 'tile': flipped_tile, 'game_state': new_state},
        room = game
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
    room = args.get('room')
    print_log_line('Message sent in %s' % (room,))
    socketio.emit(
        'message_sent',
        {'user': user, 'message': message},
        room = room
    )

def print_log_line(log_line):
    cur = db.cursor()
    cur.execute('INSERT INTO LOGS (LOG_LINE, TIME) VALUES (%s, NOW())', (log_line,))

if __name__ == '__main__':
    socketio.run(app)
    #app.run(debug=True)
