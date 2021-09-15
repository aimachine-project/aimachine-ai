import json
import multiprocessing
import random
from typing import Dict, List
import boardsoccer
import numpy as np

import flask
import websocket


APP = flask.Flask(__name__)
TICTACTOE_URL = 'ws://localhost:8080/games/tictactoe'
TICTACTOE_EXTENDED_URL = 'ws://localhost:8080/games/tictactoenfields'
SOCCER_URL = 'ws://localhost:8080/games/soccer'

WEBSOCKET_CLIENTS: List[websocket.WebSocketApp] = []
PROCESSES: Dict[websocket.WebSocketApp, multiprocessing.Process] = {}
GAME_IDS: Dict[websocket.WebSocket, str] = {}
CLIENT_IDS: Dict[websocket.WebSocket, str] = {}
BOARDS: Dict[websocket.WebSocket, np.ndarray] = {}
BOARDS_SOCCER: Dict[websocket.WebSocket, boardsoccer.BoardSoccer] = {}
BLANK_VALUE = 0


@APP.route("/")
def health_check():
    return "<h1>Greetings from Aimachine AI!</h1>", 200


def on_open_tictactoe(socket):
    print("client socket open")
    BOARDS[socket] = BLANK_VALUE * np.zeros((3, 3), int)


def on_open_tictactoe_extended(socket):
    print("client socket open")
    BOARDS[socket] = BLANK_VALUE * np.zeros((14, 14), int)


def on_open_soccer(socket):
    print("client socket open")
    BOARDS_SOCCER[socket] = boardsoccer.BoardSoccer()


def on_message_tictactoe(socket: websocket.WebSocket, event: str):
    data = json.loads(event)
    event_type = data['eventType']
    event_message = data['eventMessage']
    print('event message: ' + event_message)
    if event_type == 'game_id':
        GAME_IDS[socket] = event_message
    elif event_type == 'client_id':
        CLIENT_IDS[socket] = event_message
    elif event_type == 'field_to_be_marked':
        field_data = json.loads(event_message)
        row_index = field_data['rowIndex']
        col_index = field_data['colIndex']
        print('rowIndex, colIndex: {}-{}'.format(row_index, col_index))
        BOARDS_SOCCER[socket].make_link(row_index, col_index)
    elif event_type == 'movement_allowed':
        if event_message == CLIENT_IDS[socket]:
            available_indices = BOARDS_SOCCER[socket].get_available_node_indices()
            field_to_click = random.choice(available_indices)
            data_to_send = json.dumps({
                'eventType': 'field_clicked',
                'eventMessage': {
                    'gameId': GAME_IDS[socket],
                    'rowIndex': str(field_to_click[0]),
                    'colIndex': str(field_to_click[1])
                }
            })
            socket.send(data_to_send)
    elif event_type == 'server_message':
        print(event_message)
    else:
        print('unhandled message occurred')


def on_message_soccer(socket: websocket.WebSocket, event: str):
    data = json.loads(event)
    event_type = data['eventType']
    event_message = data['eventMessage']
    print('event message: ' + event_message)
    if event_type == 'game_id':
        GAME_IDS[socket] = event_message
    elif event_type == 'client_id':
        CLIENT_IDS[socket] = event_message
    elif event_type == 'field_to_be_marked':
        field_data = json.loads(event_message)
        row_index = field_data['rowIndex']
        col_index = field_data['colIndex']
        field_token = field_data['fieldToken']
        print('rowIndex, colIndex: {}-{}'.format(row_index, col_index))
        BOARDS[socket][row_index, col_index] = field_token
    elif event_type == 'movement_allowed':
        if event_message == CLIENT_IDS[socket]:
            row_indices, col_indices = np.where(BOARDS[socket] == BLANK_VALUE)
            free_pairs = list(zip(row_indices, col_indices))
            field_to_click = random.choice(free_pairs)
            data_to_send = json.dumps({
                'eventType': 'field_clicked',
                'eventMessage': {
                    'gameId': GAME_IDS[socket],
                    'rowIndex': str(field_to_click[0]),
                    'colIndex': str(field_to_click[1])
                }
            })
            socket.send(data_to_send)
    elif event_type == 'server_message':
        print(event_message)
    else:
        print('unhandled message occurred')


def on_error():
    print('error occurred')


def on_close(socket, close_status_code, close_msg):
    print("client socket closed")
    print("close code: {}".format(close_status_code))
    print("close message: {}".format(close_msg))
    PROCESSES[socket].terminate()


def run_websocket_app(socket):
    socket.run_forever()


@APP.route("/tictactoe")
def connect_ai_tictactoe():
    websocket.enableTrace(True)
    client = websocket.WebSocketApp(TICTACTOE_URL,
                                    on_open=on_open_tictactoe,
                                    on_message=on_message_tictactoe,
                                    on_error=on_error,
                                    on_close=on_close)
    WEBSOCKET_CLIENTS.append(client)
    process_name = 'ws_process_{}'.format(WEBSOCKET_CLIENTS.index(client))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=run_websocket_app, args=(client,), daemon=True)
    process.start()
    PROCESSES[client] = process
    return "AI client created", 201


@APP.route("/tictactoeextended")
def connect_ai_tictactoe_extended():
    websocket.enableTrace(True)
    client = websocket.WebSocketApp(TICTACTOE_EXTENDED_URL,
                                    on_open=on_open_tictactoe_extended,
                                    on_message=on_message_tictactoe,
                                    on_error=on_error,
                                    on_close=on_close)
    WEBSOCKET_CLIENTS.append(client)
    process_name = 'ws_{}'.format(WEBSOCKET_CLIENTS.index(client))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=run_websocket_app, args=(client,), daemon=True)
    process.start()
    PROCESSES[client] = process
    return "AI client created", 201


@APP.route("/soccer")
def connect_ai_soccer():
    websocket.enableTrace(True)
    client = websocket.WebSocketApp(SOCCER_URL,
                                    on_open=on_open_soccer,
                                    on_message=on_message_soccer,
                                    on_error=on_error,
                                    on_close=on_close)
    WEBSOCKET_CLIENTS.append(client)
    process_name = 'ws_{}'.format(WEBSOCKET_CLIENTS.index(client))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=run_websocket_app, args=(client,), daemon=True)
    process.start()
    PROCESSES[client] = process
    return "AI client created", 201


if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8081, debug=False)
