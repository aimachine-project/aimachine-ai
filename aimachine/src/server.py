import json
import multiprocessing
import random
import time
from typing import Dict

import flask
import numpy as np
import websocket

from aimachine.src import boardsoccer

APP = flask.Flask(__name__)

TICTACTOE_URL = 'ws://backend:8080/games/tictactoe'
TICTACTOE_EXTENDED_URL = 'ws://backend:8080/games/tictactoenfields'
SOCCER_URL = 'ws://backend:8080/games/soccer'

PROCESSES: Dict[websocket.WebSocketApp, multiprocessing.Process] = {}
GAME_IDS: Dict[websocket.WebSocket, str] = {}
CLIENT_IDS: Dict[websocket.WebSocket, str] = {}
BOARDS: Dict[websocket.WebSocket, np.ndarray] = {}
BOARDS_SOCCER: Dict[websocket.WebSocket, boardsoccer.BoardSoccer] = {}
BLANK_VALUE = 0


@APP.route('/')
def health_check():
    return '<h1>Greetings from Aimachine AI!</h1>', 200


def on_open_tictactoe(socket: websocket.WebSocket):
    print('client socket open')
    BOARDS[socket] = BLANK_VALUE * np.zeros((3, 3), int)


def on_open_tictactoe_extended(socket: websocket.WebSocket):
    print('client socket open')
    BOARDS[socket] = BLANK_VALUE * np.zeros((14, 14), int)


def on_open_soccer(socket: websocket.WebSocket):
    print('client socket open')
    BOARDS_SOCCER[socket] = boardsoccer.BoardSoccer()


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


def on_error(socket: websocket.WebSocket, err):
    print('game: {} has been disbanded'.format(GAME_IDS[socket]))
    print('at: {}'.format(err))


def on_close(socket, close_status_code, close_msg):
    print('client socket closed')
    print('close code: {}'.format(close_status_code))
    print('close message: {}'.format(close_msg))
    PROCESSES[socket].terminate()
    del GAME_IDS[socket]
    del CLIENT_IDS[socket]
    del BOARDS[socket]
    del BOARDS_SOCCER[socket]
    print('process {} terminated'.format(PROCESSES[socket].name))


def run_websocket_app(websocket_app: websocket.WebSocketApp):
    websocket_app.run_forever()


@APP.route('/tictactoe')
def connect_ai_tictactoe():
    time.sleep(1)
    game_type = flask.request.args.get('requestedGameType')
    game_id = flask.request.args.get('gameId')
    client = websocket.WebSocketApp("{}?gameType={}&gameId={}".format(TICTACTOE_URL, game_type, game_id),
                                    on_open=on_open_tictactoe,
                                    on_message=on_message_tictactoe,
                                    on_error=on_error,
                                    on_close=on_close)
    process_name = 'ws_client_{}'.format(len(PROCESSES))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=run_websocket_app, args=(client,), daemon=True)
    process.start()
    PROCESSES[client] = process
    return 'AI client created', 201


@APP.route('/tictactoeextended')
def connect_ai_tictactoe_extended():
    time.sleep(1)
    game_type = flask.request.args.get('requestedGameType')
    game_id = flask.request.args.get('gameId')
    client = websocket.WebSocketApp("{}?gameType={}&gameId={}".format(TICTACTOE_EXTENDED_URL, game_type, game_id),
                                    on_open=on_open_tictactoe_extended,
                                    on_message=on_message_tictactoe,
                                    on_error=on_error,
                                    on_close=on_close)
    process_name = 'ws_client_{}'.format(len(PROCESSES))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=run_websocket_app, args=(client,), daemon=True)
    process.start()
    PROCESSES[client] = process
    return 'AI client created', 201


@APP.route('/soccer')
def connect_ai_soccer():
    time.sleep(1)
    game_type = flask.request.args.get('requestedGameType')
    game_id = flask.request.args.get('gameId')
    client = websocket.WebSocketApp("{}?gameType={}&gameId={}".format(SOCCER_URL, game_type, game_id),
                                    on_open=on_open_soccer,
                                    on_message=on_message_soccer,
                                    on_error=on_error,
                                    on_close=on_close)
    process_name = 'ws_client_{}'.format(len(PROCESSES))
    print('process name: {}'.format(process_name))
    process = multiprocessing.Process(name=process_name, target=run_websocket_app, args=(client,), daemon=True)
    process.start()
    PROCESSES[client] = process
    return 'AI client created', 201
