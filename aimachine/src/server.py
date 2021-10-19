import json
import os
import random
import threading
import time
from typing import Dict, List, Tuple

import flask
import numpy as np
import websocket

from aimachine.src import boardsoccer
from aimachine.src.utils.movementtree import MovementTree, SoccerStrategyPushing

APP = flask.Flask(__name__)

BACKEND_DOMAIN_NAME = os.environ.get('AIM_BACKEND_DOMAIN_NAME', 'localhost')
WEBSOCKET_SERVER_BASE_URL = 'ws://{}:8080/games'.format(BACKEND_DOMAIN_NAME)
TICTACTOE_URL = '{}/tictactoe'.format(WEBSOCKET_SERVER_BASE_URL)
TICTACTOE_EXTENDED_URL = '{}/tictactoenfields'.format(WEBSOCKET_SERVER_BASE_URL)
SOCCER_URL = '{}/soccer'.format(WEBSOCKET_SERVER_BASE_URL)

CLIENTS: Dict[str, websocket.WebSocketApp] = {}
GAME_IDS: Dict[websocket.WebSocket, str] = {}
CLIENT_IDS: Dict[websocket.WebSocket, str] = {}
BOARDS: Dict[websocket.WebSocket, np.ndarray] = {}
BOARDS_SOCCER: Dict[websocket.WebSocket, boardsoccer.BoardSoccer] = {}
BLANK_VALUE = 0

BOARD_HEIGHT = boardsoccer.BoardSoccer.BOARD_HEIGHT
BOARD_WIDTH = boardsoccer.BoardSoccer.BOARD_WIDTH
MOVEMENT_LIST_SOCCER: List[Tuple[int, int]] = list()
SOCCER_STRATEGY = SoccerStrategyPushing()


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
    elif event_type == 'new_move_to_mark':
        field_data = json.loads(event_message)
        row_index = field_data['rowIndex']
        col_index = field_data['colIndex']
        print('rowIndex, colIndex: {}-{}'.format(row_index, col_index))
        BOARDS_SOCCER[socket].make_link(row_index, col_index)
    elif event_type == 'current_player':
        if event_message == CLIENT_IDS[socket]:
            handle_movement_soccer(socket)
    else:
        print(event_message)


def handle_movement_soccer(socket: websocket.WebSocket):
    global MOVEMENT_LIST_SOCCER
    if len(MOVEMENT_LIST_SOCCER) < 1:
        board = BOARDS_SOCCER[socket]
        movement_tree = MovementTree(board)
        if len(movement_tree.safe_nearest_movement_list) > 0:
            movements_list = movement_tree.get_movements_list(SOCCER_STRATEGY)
            MOVEMENT_LIST_SOCCER = movements_list
        else:
            MOVEMENT_LIST_SOCCER = [random.choice(board.get_available_node_indices())]
    field_to_click = MOVEMENT_LIST_SOCCER[0]
    data_to_send = json.dumps({
        'eventType': 'make_move',
        'eventMessage': {
            'gameId': GAME_IDS[socket],
            'rowIndex': str(field_to_click[0]),
            'colIndex': str(field_to_click[1])
        }
    })
    socket.send(data_to_send)
    MOVEMENT_LIST_SOCCER.pop(0)


def on_message_tictactoe(socket: websocket.WebSocket, event: str):
    data = json.loads(event)
    event_type = data['eventType']
    event_message = data['eventMessage']
    print('event message: ' + event_message)
    if event_type == 'game_id':
        GAME_IDS[socket] = event_message
    elif event_type == 'client_id':
        CLIENT_IDS[socket] = event_message
    elif event_type == 'new_move_to_mark':
        field_data = json.loads(event_message)
        row_index = field_data['rowIndex']
        col_index = field_data['colIndex']
        field_token = field_data['fieldToken']
        print('rowIndex, colIndex: {}-{}'.format(row_index, col_index))
        BOARDS[socket][row_index, col_index] = field_token
    elif event_type == 'current_player':
        if event_message == CLIENT_IDS[socket]:
            row_indices, col_indices = np.where(BOARDS[socket] == BLANK_VALUE)
            free_pairs = list(zip(row_indices, col_indices))
            field_to_click = random.choice(free_pairs)
            data_to_send = json.dumps({
                'eventType': 'make_move',
                'eventMessage': {
                    'gameId': GAME_IDS[socket],
                    'rowIndex': str(field_to_click[0]),
                    'colIndex': str(field_to_click[1])
                }
            })
            socket.send(data_to_send)
    else:
        print(event_message)


def on_error(socket: websocket.WebSocket, err):
    print('game: {} has been disbanded'.format(GAME_IDS[socket]))
    print('error at: {}'.format(err))
    game_id: str = GAME_IDS[socket]
    CLIENTS[game_id].close()


def on_close(socket: websocket.WebSocket, close_status_code, close_msg):
    print('client socket closed')
    print('close code: {}'.format(close_status_code))
    print('close message: {}'.format(close_msg))
    del GAME_IDS[socket]
    del CLIENT_IDS[socket]
    del BOARDS[socket]
    del BOARDS_SOCCER[socket]


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
    thread_name = 'ws_client_{}'.format(game_id)
    print('thread name: {}'.format(thread_name))
    thread = threading.Thread(name=thread_name, target=client.run_forever, daemon=True)
    thread.start()
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
    thread_name = 'ws_client_{}'.format(game_id)
    print('thread name: {}'.format(thread_name))
    thread = threading.Thread(name=thread_name, target=client.run_forever, daemon=True)
    thread.start()
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
    CLIENTS[game_id] = client
    thread_name = 'ws_client_{}'.format(game_id)
    print('thread name: {}'.format(thread_name))
    thread = threading.Thread(name=thread_name, target=client.run_forever, daemon=True)
    thread.start()
    return 'AI client created', 201
