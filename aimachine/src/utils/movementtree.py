from __future__ import annotations

import copy
from typing import List, Tuple

from aimachine.src import boardsoccer
from aimachine.src.boardsoccer import BoardSoccer
from aimachine.src.nodelink import NodeLink

BOARD_HEIGHT = boardsoccer.BoardSoccer.BOARD_HEIGHT
BOARD_WIDTH = boardsoccer.BoardSoccer.BOARD_WIDTH


class MovementTree:
    def __init__(self, board: BoardSoccer):
        self.board = board
        self.safe_nearest_movement_list = MovementTree._get_safe_movements(self.board)
        self.subtrees: List[MovementTree] = list()

    def get_movements_list(self, decision_strategy: SoccerStrategy) -> List[Tuple[int, int]]:
        self._set_possible_movement_paths()
        iterator = MovementTreeIterator(self, decision_strategy)
        movements_list: List[Tuple[int, int]] = list()
        while iterator.has_subtrees():
            subtree = iterator.chose_subtree()
            current_node = subtree.board.current_node
            movements_list.append((current_node.row_index, current_node.col_index))
        return movements_list

    def _set_possible_movement_paths(self):
        for indices in self.safe_nearest_movement_list:
            tmp = copy.deepcopy(self.board)
            tmp.make_link(indices[0], indices[1])
            subtree = MovementTree(tmp)
            self._add_subtree(subtree)
            safe_movements = MovementTree._get_safe_movements(tmp)
            if len(safe_movements) > 0 and len(tmp.current_node.links) != 1:
                subtree._set_possible_movement_paths()

    def _add_subtree(self, subtree: MovementTree):
        self.subtrees.append(subtree)

    @staticmethod
    def _get_safe_movements(board: BoardSoccer) -> List[Tuple[int, int]]:
        filtered = list()
        for indices in board.get_available_node_indices():
            node_candidate = board.nodes[indices[0]][indices[1]]
            if len(node_candidate.links) < len(NodeLink) - 1:
                filtered.append(indices)
        return filtered


class MovementTreeIterator:
    def __init__(self, tree: MovementTree, decision_strategy: SoccerStrategy):
        self.current_root = tree
        self._decision_strategy = decision_strategy

    def has_subtrees(self) -> bool:
        return len(self.current_root.subtrees) > 0

    def chose_subtree(self) -> MovementTree:
        chosen_indices = self._decision_strategy.get_movement(self.current_root.board)
        self.current_root = self._find_subtree_by_current_node_indices(chosen_indices)
        return self.current_root

    def _find_subtree_by_current_node_indices(self, indices: Tuple[int, int]) -> MovementTree:
        for subtree in self.current_root.subtrees:
            node = subtree.board.current_node
            if node.row_index == indices[0] and node.col_index == indices[1]:
                return subtree
        raise RuntimeError("Element should be found but it wasn't")


class SoccerStrategy:
    @staticmethod
    def get_movement(board: BoardSoccer) -> Tuple[int, int]:
        pass


class SoccerStrategyPushing(SoccerStrategy):
    @staticmethod
    def get_movement(board: BoardSoccer) -> Tuple[int, int]:
        indices = board.get_available_node_indices()
        indices.sort(key=lambda x: len(board.nodes[x[0]][x[1]].links))
        indices = sorted(indices, key=lambda x: (BOARD_HEIGHT - x[0], abs(board.middleColIndex - x[1])))
        return indices[0]
