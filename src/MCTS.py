import chess
import math
import numpy
import random

class MCTS:
    def __init__(self, board=chess.Board(), C=1.41421356):
        self.board = board
        self.C = C # exploration constant for UCB1
        self.positions = {} # [0] = wins, [1] = plays
    

    def best_move(self):
        children = []
        heuristics = []
        parent_fen = self.board.fen()
        for move in self.board.legal_moves:
            # print(f'18 {move}')
            children.append(move)
            self.board.push(move)
            # print(f'21 {self.board.move_stack}')
            if self.get_plays() == 0:
                self.playout()
            # print(f'24 {self.board.move_stack}')
            heuristics.append(self.heuristic(parent_fen))
            # print(f'26 {self.board.move_stack}')
            self.board.pop()
        
        # get best child
        best = children[heuristics.index(max(heuristics))]

        # backpropagate result if terminal node
        self.board.push(best)
        if self.board.is_game_over():
            self.backpropagate()
        self.board.pop()

        return best


    # return heuristic for move based on UCT algorithm
    def heuristic(self, parent: str):
        win_percentage = self.get_wins() / self.get_plays()
        exploration = self.C * math.sqrt(math.log(self.get_plays(parent)) / self.get_plays())
        return win_percentage + exploration


    # randomly move until end
    def playout(self):
        # hold current board attributes
        restore_fen = self.board.fen()
        stack = self.board.move_stack[:]

        # push random moves until outcome reached
        while not self.board.is_game_over():
            self.board.push(random.choice(list(self.board.legal_moves)))

        # backpropagate result of playout throughout tree and restore board attributes
        self.backpropagate()

        # restore old board attributes
        self.board.set_fen(restore_fen)
        self.board.move_stack = stack

    def backpropagate(self):
        if not self.board.outcome():
            raise RuntimeError('Game is not over, cannot backpropagate.')
        
        if self.board.is_checkmate():
            result = -1
        else: # draw
            result = 0

        for i in range(len(self.board.move_stack), -1, -1): # stop at -1 since we have (len(stack) + 1) positions
            if result == 1 or result == 0: # got checkmated or drew
                self.add_loss()
            else: # checkmated opponent
                self.add_win()
            result *= -1
            if i > 0:
                self.board.pop()


    def add_win(self, fen=None):
        if fen is None:
            fen = self.board.fen()
        if fen not in self.positions:
            self.positions[fen] = numpy.zeros(2, dtype=numpy.uint32)
        self.positions[fen] += 1


    def add_loss(self, fen=None):
        if fen is None:
            fen = self.board.fen()
        if fen not in self.positions:
            self.positions[fen] = numpy.zeros(2, dtype=numpy.uint32)
        self.positions[fen][1] += 1


    def get_wins(self, fen=None):
        if fen is None:
            fen = self.board.fen()
        return self.positions[fen][0]


    def get_plays(self, fen=None):
        if fen is None:
            fen = self.board.fen()
        if fen not in self.positions:
            self.positions[fen] = numpy.zeros(2, dtype=numpy.uint32)
        return self.positions[fen][1]


def moveStack_toString(board):
    moves = ''
    for i, move in enumerate(board.move_stack):
        if (i % 2 == 0):
            moves += '\n' + (i + 1) + '.' # add move num
        moves += ' ' + move.san()
    return moves


if __name__ == '__main__':
    NUM_GAMES = 1
    board = chess.Board()
    tree = MCTS(board)
    for game in range(NUM_GAMES):
        print(f'Game ({game})')
        while not board.is_game_over():
            move = tree.best_move()
            board.push(move)
        print(moveStack_toString(board))
