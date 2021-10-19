from unittest import TestCase

from aimachine.src.boardsoccer import BoardSoccer
from aimachine.src.utils.movementtree import MovementTree, SoccerStrategyPushing


class TestMovementTree(TestCase):

    def test_simple(self):
        board = BoardSoccer()
        board.make_link(board.current_node.row_index, board.current_node.col_index - 1)
        board.make_link(board.current_node.row_index - 1, board.current_node.col_index + 1)
        tree = MovementTree(board)
        strategy = SoccerStrategyPushing()
        movements = tree.get_movements_list(strategy)
        self.assertEquals([(6, 5), (7, 5)], movements)

    def test_complex(self):
        board = BoardSoccer()
        movements = [(7, 6), (6, 6), (7, 5), (6, 4), (7, 4), (6, 3), (7, 3), (6, 2), (7, 2), (8, 2), (9, 3), (9, 4),
                     (10, 5), (9, 6), (10, 6), (10, 7)]
        for movement in movements:
            board.make_link(movement[0], movement[1])
        tree = MovementTree(board)
        strategy = SoccerStrategyPushing()
        movements = tree.get_movements_list(strategy)
        self.assertEquals([(11, 6), (12, 5)], movements)
