import json
import multiprocessing
import time
from typing import Dict, List

import flask
import websocket

APP = flask.Flask(__name__)

WEBSOCKET_CLIENTS: List[websocket.WebSocketApp] = []
PROCESSES: Dict[websocket.WebSocketApp, multiprocessing.Process] = {}
TICTACTOE_URL = 'ws://localhost:8080/games/tictactoe'


@APP.route("/")
def health_check():
    return "<p>Hello, World!</p>"


def on_message(ws, message):
    print(message)


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    PROCESSES[ws].terminate()


def on_open(ws):
    while True:
        time.sleep(1)
        ws.send(json.dumps({"eventType": "hello"}))


def create_ws(ws):
    ws.run_forever()


@APP.route("/tictactoe")
def connect_computer_player():
    print("yo yo")
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp(TICTACTOE_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    WEBSOCKET_CLIENTS.append(ws)
    process_name = 'ws_{}'.format(WEBSOCKET_CLIENTS.index(ws))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=create_ws, args=(ws,), daemon=True)
    process.start()
    # process.join()
    PROCESSES[ws] = process
    return "OK"


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8081, debug=False)
