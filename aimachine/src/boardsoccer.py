from typing import Tuple, List

from aimachine.src.nodelink import NodeLink


class BoardSoccer:
    _BOARD_HEIGHT = 12
    _BOARD_WIDTH = 10
    GATE_WIDTH = 2
    middleRowIndex = int(round(_BOARD_HEIGHT / 2))
    middleColIndex = int(round(_BOARD_WIDTH / 2))
    gateHalfWidth = int(round(GATE_WIDTH / 2))

    def __init__(self):
        self.nodes = [[Node(i, j, self) for j in range(self._BOARD_WIDTH + 1)] for i in range(self._BOARD_HEIGHT + 1)]
        self.current_node = self.nodes[self.middleRowIndex][self.middleColIndex]

        # link gate rear borders
        for i in range(0, self.gateHalfWidth):
            self.nodes[0][self.middleColIndex - i].make_link(NodeLink.LINK_LEFT)
            self.nodes[0][self.middleColIndex + i].make_link(NodeLink.LINK_RIGHT)
            self.nodes[self._BOARD_HEIGHT][self.middleColIndex - i].make_link(NodeLink.LINK_LEFT)
            self.nodes[self._BOARD_HEIGHT][self.middleColIndex + i].make_link(NodeLink.LINK_RIGHT)
        # link gate skews
        self.nodes[1][self.middleColIndex - self.gateHalfWidth].make_link(NodeLink.LINK_TOP_LEFT)
        self.nodes[1][self.middleColIndex + self.gateHalfWidth].make_link(NodeLink.LINK_TOP_RIGHT)
        self.nodes[self._BOARD_HEIGHT - 1][self.middleColIndex - self.gateHalfWidth].make_link(
            NodeLink.LINK_BOTTOM_LEFT)
        self.nodes[self._BOARD_HEIGHT - 1][self.middleColIndex + self.gateHalfWidth].make_link(
            NodeLink.LINK_BOTTOM_RIGHT)
        # link gate side borders
        self.nodes[0][self.middleColIndex - 1].make_link(NodeLink.LINK_BOTTOM)
        self.nodes[0][self.middleColIndex + 1].make_link(NodeLink.LINK_BOTTOM)
        self.nodes[self._BOARD_HEIGHT][self.middleColIndex - 1].make_link(NodeLink.LINK_TOP)
        self.nodes[self._BOARD_HEIGHT][self.middleColIndex + 1].make_link(NodeLink.LINK_TOP)
        # link vertical borders
        for i in range(1, self._BOARD_HEIGHT):
            left_border_node = self.nodes[i][1]
            left_border_node.make_link(NodeLink.LINK_TOP)
            left_border_node.make_link(NodeLink.LINK_TOP_LEFT)
            left_border_node.make_link(NodeLink.LINK_LEFT)
            left_border_node.make_link(NodeLink.LINK_BOTTOM_LEFT)
            left_border_node.make_link(NodeLink.LINK_BOTTOM)

            right_border_node = self.nodes[i][self._BOARD_WIDTH - 1]
            right_border_node.make_link(NodeLink.LINK_TOP)
            right_border_node.make_link(NodeLink.LINK_TOP_RIGHT)
            right_border_node.make_link(NodeLink.LINK_RIGHT)
            right_border_node.make_link(NodeLink.LINK_BOTTOM_RIGHT)
            right_border_node.make_link(NodeLink.LINK_BOTTOM)

        # link horizontal borders beside gates
        for i in range(1, self.middleColIndex - self.gateHalfWidth):
            top_left_border_node = self.nodes[1][i]
            top_left_border_node.make_link(NodeLink.LINK_LEFT)
            top_left_border_node.make_link(NodeLink.LINK_TOP_LEFT)
            top_left_border_node.make_link(NodeLink.LINK_TOP)
            top_left_border_node.make_link(NodeLink.LINK_TOP_RIGHT)
            top_left_border_node.make_link(NodeLink.LINK_RIGHT)

            top_right_border_node = self.nodes[1][self._BOARD_WIDTH - i]
            top_right_border_node.make_link(NodeLink.LINK_RIGHT)
            top_right_border_node.make_link(NodeLink.LINK_TOP_RIGHT)
            top_right_border_node.make_link(NodeLink.LINK_TOP)
            top_right_border_node.make_link(NodeLink.LINK_TOP_LEFT)
            top_right_border_node.make_link(NodeLink.LINK_LEFT)

            bottom_left_node = self.nodes[self._BOARD_HEIGHT - 1][i]
            bottom_left_node.make_link(NodeLink.LINK_LEFT)
            bottom_left_node.make_link(NodeLink.LINK_BOTTOM_LEFT)
            bottom_left_node.make_link(NodeLink.LINK_BOTTOM)
            bottom_left_node.make_link(NodeLink.LINK_BOTTOM_RIGHT)
            bottom_left_node.make_link(NodeLink.LINK_RIGHT)

            bottom_right_node = self.nodes[self._BOARD_HEIGHT - 1][self._BOARD_WIDTH - i]
            bottom_right_node.make_link(NodeLink.LINK_RIGHT)
            bottom_right_node.make_link(NodeLink.LINK_BOTTOM_RIGHT)
            bottom_right_node.make_link(NodeLink.LINK_BOTTOM)
            bottom_right_node.make_link(NodeLink.LINK_BOTTOM_LEFT)
            bottom_right_node.make_link(NodeLink.LINK_LEFT)

        self.current_node = self.nodes[self.middleRowIndex][self.middleColIndex]

    def get_available_node_indices(self) -> List[Tuple[int, int]]:
        indices = list()
        if not self.current_node.has_link(NodeLink.LINK_TOP):
            indices.append((self.current_node.row_index - 1, self.current_node.col_index))
        if not self.current_node.has_link(NodeLink.LINK_TOP_RIGHT):
            indices.append((self.current_node.row_index - 1, self.current_node.col_index + 1))
        if not self.current_node.has_link(NodeLink.LINK_RIGHT):
            indices.append((self.current_node.row_index, self.current_node.col_index + 1))
        if not self.current_node.has_link(NodeLink.LINK_BOTTOM_RIGHT):
            indices.append((self.current_node.row_index + 1, self.current_node.col_index + 1))
        if not self.current_node.has_link(NodeLink.LINK_BOTTOM):
            indices.append((self.current_node.row_index + 1, self.current_node.col_index))
        if not self.current_node.has_link(NodeLink.LINK_BOTTOM_LEFT):
            indices.append((self.current_node.row_index + 1, self.current_node.col_index - 1))
        if not self.current_node.has_link(NodeLink.LINK_LEFT):
            indices.append((self.current_node.row_index, self.current_node.col_index - 1))
        if not self.current_node.has_link(NodeLink.LINK_TOP_LEFT):
            indices.append((self.current_node.row_index - 1, self.current_node.col_index - 1))
        return indices

    def make_link(self, other_node_row_index: int, other_node_col_index: int):
        current_node_row_index = self.current_node.row_index
        current_node_col_index = self.current_node.col_index
        rows_diff = other_node_row_index - current_node_row_index
        cols_diff = other_node_col_index - current_node_col_index
        if rows_diff == -1 and cols_diff == 0:
            if not self.current_node.has_link(NodeLink.LINK_TOP):
                self.current_node = self.current_node.make_link(NodeLink.LINK_TOP)
        elif rows_diff == -1 and cols_diff == 1:
            if not self.current_node.has_link(NodeLink.LINK_TOP_RIGHT):
                self.current_node = self.current_node.make_link(NodeLink.LINK_TOP_RIGHT)
        elif rows_diff == 0 and cols_diff == 1:
            if not self.current_node.has_link(NodeLink.LINK_RIGHT):
                self.current_node = self.current_node.make_link(NodeLink.LINK_RIGHT)
        elif rows_diff == 1 and cols_diff == 1:
            if not self.current_node.has_link(NodeLink.LINK_BOTTOM_RIGHT):
                self.current_node = self.current_node.make_link(NodeLink.LINK_BOTTOM_RIGHT)
        elif rows_diff == 1 and cols_diff == 0:
            if not self.current_node.has_link(NodeLink.LINK_BOTTOM):
                self.current_node = self.current_node.make_link(NodeLink.LINK_BOTTOM)
        elif rows_diff == 1 and cols_diff == -1:
            if not self.current_node.has_link(NodeLink.LINK_BOTTOM_LEFT):
                self.current_node = self.current_node.make_link(NodeLink.LINK_BOTTOM_LEFT)
        elif rows_diff == 0 and cols_diff == -1:
            if not self.current_node.has_link(NodeLink.LINK_LEFT):
                self.current_node = self.current_node.make_link(NodeLink.LINK_LEFT)
        elif rows_diff == -1 and cols_diff == -1:
            if not self.current_node.has_link(NodeLink.LINK_TOP_LEFT):
                self.current_node = self.current_node.make_link(NodeLink.LINK_TOP_LEFT)


class Node:
    def __init__(self, row_index: int, col_index: int, board: BoardSoccer):
        self.row_index = row_index
        self.col_index = col_index
        self._board = board
        self.links: List[NodeLink] = []

    def has_link(self, link: NodeLink) -> bool:
        return self.links.__contains__(link)

    def has_any_free_link(self) -> bool:
        return len(self.links) < len(NodeLink)

    def make_link(self, link: NodeLink):
        if link is NodeLink.LINK_TOP:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index - 1][self.col_index]
            linked_node.links.append(NodeLink.LINK_BOTTOM)
            return linked_node
        elif link is NodeLink.LINK_TOP_RIGHT:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index - 1][self.col_index + 1]
            linked_node.links.append(NodeLink.LINK_BOTTOM_LEFT)
            return linked_node
        elif link is NodeLink.LINK_RIGHT:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index][self.col_index + 1]
            linked_node.links.append(NodeLink.LINK_LEFT)
            return linked_node
        elif link is NodeLink.LINK_BOTTOM_RIGHT:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index + 1][self.col_index + 1]
            linked_node.links.append(NodeLink.LINK_TOP_LEFT)
            return linked_node
        elif link is NodeLink.LINK_BOTTOM:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index + 1][self.col_index]
            linked_node.links.append(NodeLink.LINK_TOP)
            return linked_node
        elif link is NodeLink.LINK_BOTTOM_LEFT:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index + 1][self.col_index - 1]
            linked_node.links.append(NodeLink.LINK_TOP_RIGHT)
            return linked_node
        elif link is NodeLink.LINK_LEFT:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index][self.col_index - 1]
            linked_node.links.append(NodeLink.LINK_RIGHT)
            return linked_node
        elif link is NodeLink.LINK_TOP_LEFT:
            self.links.append(link)
            linked_node = self._board.nodes[self.row_index - 1][self.col_index - 1]
            linked_node.links.append(NodeLink.LINK_BOTTOM_RIGHT)
            return linked_node
        else:
            return self._board.current_node
