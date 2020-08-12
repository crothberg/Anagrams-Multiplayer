from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO
import flask_socketio
import game_data
import os
import json
import time
from util import cursor, print_log_line

app = Flask(__name__)
socketio = SocketIO(app)

#db_storage = ZODB.FileStorage.FileStorage('tmp_anagrams_online.db')
#To run locally on Windows: set DATABASE_URL= user='postgres' host='localhost'

@app.before_first_request
def setup_db():
    destroy_db()
    cur = cursor()
    cur.execute('CREATE TABLE USERS (                   \
                    NAME    TEXT            NOT NULL,   \
                    SID     TEXT                    ,   \
                    GAME    TEXT                    )')
    cur.execute('CREATE TABLE GAMES (                   \
                    NAME TEXT               NOT NULL,   \
                    STATE TEXT )')
    cur.execute('CREATE TABLE LOGS  (                   \
                    LOG_LINE TEXT           NOT NULL,   \
                    TIME TIMESTAMP          NOT NULL)')

def destroy_db():
    cur = cursor()
    try:
        cur.execute('DROP TABLE USERS')
    except Exception:
        pass
    try:
        cur.execute('DROP TABLE GAMES')
    except Exception:
        pass
    try:
        cur.execute('DROP TABLE LOGS')
    except Exception:
        pass

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/status')
def get_status():
    cur = cursor()
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
    cur = cursor()
    cur.execute('SELECT LOG_LINE, TIME FROM LOGS ORDER BY TIME DESC LIMIT 1000')
    logs = cur.fetchall()
    return '<br>'.join(['%s: %s' % (log_line[1], log_line[0]) for log_line in logs])

def get_game_by_name(game_name):
    cur = cursor()
    cur.execute('SELECT STATE FROM GAMES WHERE NAME = %s', (game_name,))
    game_state_str = cur.fetchone()
    if game_state_str is None:
        return None
    game_state = game_data.deserialize_game_room(json.loads(game_state_str[0]))
    return game_state

def update_game_state(game_name, game_state):
    cur = cursor()
    cur.execute('UPDATE GAMES SET STATE = %s WHERE NAME = %s', (json.dumps(game_state.generate_game_state()), game_name))

@socketio.on('disconnect')
def user_disc():
    sid = request.sid
    cur = cursor()
    cur.execute('SELECT NAME, GAME FROM USERS WHERE SID = %s', (sid,))
    user_data = cur.fetchone()
    if user_data is None:
        print_log_line('Unknown user with SID = %s disconnected' % (sid,))
        return
    username, game = user_data
    print_log_line('%s (%s) disconnected' % (username, sid))
    cur.execute('UPDATE USERS SET SID = NULL WHERE SID = %s', (sid,))
    cur.execute('SELECT NAME FROM USERS WHERE GAME = %s AND SID IS NOT NULL', (game,))
    if cur.fetchone() is None:
        cur.execute('DELETE FROM GAMES WHERE NAME = %s', (game,))

def user_rem():
    sid = request.sid
    cur = cursor()
    cur.execute('SELECT NAME, GAME FROM USERS WHERE SID = %s', (sid,))
    user_data = cur.fetchone()
    if user_data is None:
        print_log_line('Phantom sid tried to disconnect: %s' % (sid,))
        return
    username = user_data[0]
    game = user_data[1]
    print_log_line('User %s (%s) leaving %s' % (username, sid, game))
    game_state = get_game_by_name(game)
    if game_state is None:
        print_log_line('Missing game data: %s' % (game,))
        return
    game_state.remove_user(username)
    if game_state.num_users() == 0:
        cur.execute('DELETE FROM GAMES WHERE NAME = %s', (game,))
    else:
        update_game_state(game, game_state)

    cur.execute('DELETE FROM USERS WHERE SID = %s', (sid,))
    new_state = game_state.generate_game_state()
    update_message = 'User %s has left' % (username,)
    socketio.emit('game_state_update',
        {'game_state' : new_state, 'event' : 'leave', 'status' : update_message},
        room = game
    )

@socketio.on('join_game')
def join_game(data):
    sid = request.sid
    username = data['username']
    game_name = data['game_name']
    cur = cursor()
    game_state = get_game_by_name(game_name)
    cur.execute('DELETE FROM USERS WHERE NAME = %s', (username,))
    cur.execute('INSERT INTO USERS (NAME, SID, GAME) VALUES (%s, %s, %s)', (username, sid, game_name))
    flask_socketio.join_room(game_name)
    if game_state is None:
        ##create the game:
        cur.execute('INSERT INTO GAMES (NAME) VALUES (%s)', (game_name,))
        game_state = game_data.game_room(username)
    else:
        if game_state.has_user(username):
            print_log_line('%s updating sid to %s' % (username, sid))
            send_challenge_updates(sid, game_state)
            return
        game_state.add_user(username)

    print_log_line('user %s (%s) joining game %s' % (username, sid, game_name))
    update_game_state(game_name, game_state)

    cur.execute('UPDATE GAMES SET STATE = %s WHERE NAME = %s', (json.dumps(game_state.generate_game_state()), game_name))

    new_state = game_state.generate_game_state()
    update_message = 'User %s has joined' % (username,)
    socketio.emit('game_state_update',
                    {'game_state' : new_state, 'event' : 'join', 'status' : update_message},
                    room = game_name)
    send_challenge_updates(sid, game_state)

def send_challenge_updates(sid, game_state):
    challenge = game_state.get_challenge()
    if challenge is not None:
        c_time, c_user, c_word, c_votes = challenge
        status_msg = '%s\'s word: %s is being challenged' % (c_user, c_word)
        socketio.emit(
                    'challenge',
                    {'status': status_msg},
                    room = sid)

        socketio.emit(
                    'vote_cast',
                    {'status' : status_msg, 'votes' : game_state.get_votes()},
                    room = sid)

@socketio.on('flip')
def flip_tile(args):
    user = args.get('user')
    game = args.get('room')
    cur = cursor()
    game_state = get_game_by_name(game)
    if game_state is None:
        print_log_line('user %s attempted to access missing room %s' % (user, game))
        return

    flipped_tile = game_state.flip_tile()
    new_state = game_state.generate_game_state()
    update_game_state(game, game_state)
    state_update = 'No more letters'
    if flipped_tile is not None:
        article = 'an' if flipped_tile in 'ERIOASFHLXNM' else 'a'
        state_update = '%s flipped %s "%s"'  % (user, article, flipped_tile)
        print_log_line('room %s: %s flipped %s "%s"' % (game, user, article, flipped_tile))

    socketio.emit(
        'game_state_update',
        {'status' : state_update , 'event' : 'flip', 'game_state': new_state},
        room = game
    )

MAX_TYPING_TIME = 5
@socketio.on('steal')
def steal_word(args):
    user = args.get('user')
    word = args.get('word')
    room = args.get('room')
    typing_time = args.get('typing_time')
    if typing_time > MAX_TYPING_TIME:
        typing_time = MAX_TYPING_TIME
    word = game_data.char_strip(word)
    game_state = get_game_by_name(room)
    steal_result = game_state.steal_word(user, word, typing_time)
    print_log_line('word: %s typing_time: %s' % (word, typing_time))

    while steal_result == False:
        prev_time = game_state.prev_time()
        print_log_line('rollback %s - %s - %s' % (prev_time, time.time(), typing_time))
        if prev_time > time.time() - typing_time:
            game_state.rollback()
            steal_result = game_state.steal_word(user, word, typing_time)
        else:
            break

    old_game_state = get_game_by_name(room)
    truncate = game_state.hist_len()
    tail = old_game_state.hist_tail(truncate)
    for steal_record in tail:
        game_state.steal_word(steal_record[0], steal_record[1], time.time() - stail_record[4])

    new_state = game_state.generate_game_state()
    status_msg = '%s stole the word "%s"' % (user, word)
    if steal_result == False:
        status_msg = '%s tried to steal the word "%s"' % (user, word)
        game_state = old_game_state
    else:
        print_log_line('room %s: %s stole the word "%s"' % (room, user, word))
        update_game_state(room, game_state)

    socketio.emit(
        'game_state_update',
        {'status': status_msg, 'event' : 'steal', 'game_state' : new_state},
        room = room
    )

@socketio.on('undo')
def undo(args):
    room = args.get('room')

    game_state = get_game_by_name(room)
    game_state.rollback()

    update_game_state(room, game_state)

    new_state = game_state.generate_game_state()
    status_msg = 'Undo granted'
    socketio.emit(
        'game_state_update',
        {'status': status_msg, 'event' : 'undo', 'game_state' : new_state},
        room = room
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

@socketio.on('challenge')
def challenge(args):
    room = args.get('room')
    user = args.get('user')
    target_user = args.get('target_user')
    word = args.get('word')
    game_state = get_game_by_name(room)
    if target_user != user:
        game_state.create_challenge(target_user, word)
        update_game_state(room, game_state)
        print_log_line('room %s: %s is challenging %s\'s word - %s' % (room, user, target_user, word))
        status_msg = '%s is challenging %s\'s word: %s' % (user, target_user, word)
        socketio.emit(
            'challenge',
            {'status': status_msg},
            room = room)
    else:
        game_state.rollback(user, word)
        new_state = game_state.generate_game_state()
        update_game_state(room, game_state)
        status_msg = '%s Has self challenged: %s' % (user, word)
        socketio.emit(
            'game_state_update',
            {'status' : status_msg, 'event' : 'self_challenge', 'game_state' : new_state},
            room = room)

@socketio.on('get_game_state')
def get_game_state(args):
    room = args.get('game_name')
    game_state = get_game_by_name(room)
    new_state = game_state.generate_game_state()
    socketio.emit(
        'game_state_update',
        {'game_state' : new_state, 'event' : 'get_game_state'},
        room = request.sid)

def finish_challenge(game_state, room):
    challenge_result = game_state.finish_challenge()
    new_state = game_state.generate_game_state()
    update_game_state(room, game_state)
    status_msg = ''
    if challenge_result == True:
        status_msg = 'The challenge has succeeded'
    else:
        status_msg = 'The challenge has failed'
    socketio.emit(
            'game_state_update',
            {'status' : status_msg, 'event' : 'end_challenge', 'game_state' : new_state},
            room = room)

@socketio.on('vote')
def vote(args):
    room = args.get('room')
    user = args.get('user')
    vote = args.get('vote')
    print_log_line('room %s: %s votes to %s the word' % (room, user, vote))
    game_state = get_game_by_name(room)
    game_state.set_vote(user, vote)

    if game_state.all_votes_in():
        finish_challenge(game_state, room)
    else:
        update_game_state(room, game_state)
        status_msg = '%s has voted: %s' % (user, vote)
        socketio.emit(
            'vote_cast',
            {'status' : status_msg, 'votes' : game_state.get_votes()},
            room = room)

def print_log_line(log_line):
    cur = cursor()
    cur.execute('INSERT INTO LOGS (LOG_LINE, TIME) VALUES (%s, NOW())', (log_line,))

if __name__ == '__main__':
    socketio.run(app)
