import unittest
import chess
import math
import sys, os

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'src'))

from MCTS import MCTS

class TestPlayoutAndBackpropagate(unittest.TestCase):
    def setUp(self):
        self.tree = MCTS()
        self.tree.board.reset()
        self.board = self.tree.board

        # fool's mate
        self.board.push_san('f3')
        self.board.push_san('e5')
        self.board.push_san('g4')
        self.board.push_san('Qh4#')

        self.stack_before = self.board.move_stack[:]
        self.fen_before = self.board.fen()
        self.winner = self.board.outcome().winner
    

    def test_playout(self):
        self.tree.board = chess.Board()
        self.tree.board.reset()
        self.board = self.tree.board
        self.tree.board.push_san('e4')

        self.stack_before = self.board.move_stack[:]

        for i in range(2):
            self.tree.playout()

        self.assertEqual('e2e4', self.board.move_stack[0].uci())
        self.assertEqual(2, self.tree.positions[self.board.fen()][1]) # check num of plays
        
        for i in zip(self.stack_before, self.board.move_stack):
            self.assertEqual(i[0], i[1])


    def test_break_backpropagate(self):
        self.tree.board = chess.Board()
        with self.assertRaises(RuntimeError):
            self.tree.backpropagate()


    def test_backpropagate(self):
        self.tree.backpropagate()
        self.assertNotEqual(self.board.move_stack, self.stack_before)
        self.assertNotEqual(self.board.fen(), self.fen_before)
        temp = chess.Board()
        # white loses in fool's mate so starting position should return a win and an attempt
        self.assertEqual(self.tree.positions[temp.fen()][0], 1)
        self.assertEqual(self.tree.positions[temp.fen()][1], 1)
        temp.push_san('f3')
        self.assertEqual(self.tree.positions[temp.fen()][0], 0)
        self.assertEqual(self.tree.positions[temp.fen()][1], 1)

        # reverse fool's mate
        temp = chess.Board()
        temp.push_san('e3')
        temp.push_san('f6')
        temp.push_san('d3')
        temp.push_san('g5')
        temp.push_san('Qh5#')
        self.tree = MCTS() # reset tree
        self.assertEqual(len(self.tree.positions), 0)
        self.tree.board = temp
        self.tree.backpropagate() # resets temp to starting position

        # black loses in reverse fool's mate so starting positions return an attempt
        self.assertEqual(self.tree.positions[temp.fen()][0], 0)
        self.assertEqual(self.tree.positions[temp.fen()][1], 1)
        temp.push_san('e3')
        self.assertEqual(self.tree.positions[temp.fen()][0], 1)
        self.assertEqual(self.tree.positions[temp.fen()][1], 1)
        

    def test_heuristic(self):
        self.board = chess.Board('8/2k5/P7/8/8/3pq3/8/3K4 w - - 0 1')
        self.tree = MCTS(self.board)
        
        # make sure a7 isnt in positions 
        self.board.push_san('a7')
        self.assertEqual(self.tree.positions.get(self.board.fen(), 0), 0)
        self.board.pop()
        
        self.assertEqual(chess.Move(chess.parse_square('a6'), chess.parse_square('a7')), self.tree.best_move())
        
        parent_fen = self.board.fen()
        self.board.push_san('a7')
        self.assertIn(self.tree.heuristic(parent_fen), [0.0, 1.0])
        
        self.tree.positions.pop(self.board.fen())
        self.tree.add_win()
        self.tree.add_loss()
        self.tree.add_loss(parent_fen) # add play (win or loss) to parent
        self.assertTrue(abs(self.tree.heuristic(parent_fen) - 1.33255) < .00001)


if __name__ == '__main__':
    unittest.main()