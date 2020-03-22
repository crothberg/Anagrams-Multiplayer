from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods=['GET'])
def hello():
    return render_template('index.html')

@app.route('/game', methods=['GET'])
def visit_game():
    return 'Currently in game: ' + request.args.get('game_name')

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

if __name__ == '__main__':
    socketio.run(app)
    app.run(debug=True)
