import json
import multiprocessing
from typing import Dict, List

import flask
import websocket

APP = flask.Flask(__name__)

WEBSOCKET_CLIENTS: List[websocket.WebSocketApp] = []
PROCESSES: Dict[websocket.WebSocketApp, multiprocessing.Process] = {}
TICTACTOE_URL = 'ws://localhost:8080/games/tictactoe'


@APP.route("/")
def health_check():
    return "<h1>Greetings from Aimachine AI!</h1>", 200


def on_message(ws, event):
    data = json.loads(event)
    event_type = data['eventType']
    event_message = data['eventMessage']
    print('event message: ' + event_message)
    if event_type == 'game_id':
        pass
    elif event_type == 'client_id':
        pass
    elif event_type == 'field_to_be_marked':
        field_data = json.loads(event_message)
        row_index = field_data['rowIndex']
        col_index = field_data['colIndex']
        print('rowIndex, colIndex: {}-{}'.format(row_index, col_index))
        pass
    elif event_type == 'movement_allowed':
        pass
    elif event_type == 'server_message':
        pass
    else:
        pass


def on_error(ws, error):
    print('error: '.format(error))


def on_close(ws, close_status_code, close_msg):
    print("client socket closed")
    PROCESSES[ws].terminate()


def on_open(ws):
    print("client socket open")


def create_ws(ws):
    ws.run_forever()


@APP.route("/tictactoe")
def connect_computer_player():
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
    return "AI client created", 201


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8081, debug=False)
