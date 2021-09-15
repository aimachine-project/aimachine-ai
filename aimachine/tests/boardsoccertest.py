from unittest import TestCase
import aimachine.src.boardsoccer as bs


class BoardSoccerTest(TestCase):

    def test_init(self):
        board = bs.BoardSoccer()
        self.assertFalse(2 == 1)
