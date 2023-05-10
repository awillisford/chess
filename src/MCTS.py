import chess
import chess.pgn
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
            children.append(move)
            self.board.push(move)
            if self.get_plays() == 0:
                self.playout()
            heuristics.append(self.heuristic(parent_fen))
            self.board.pop()
        
        # get best child
        best = children[heuristics.index(max(heuristics))]

        # backpropagate result if terminal node
        self.board.push(best)
        if self.board.is_game_over():
            stack = self.board.move_stack[:-1]
            self.backpropagate()
            for move in stack:
                self.board.push(move)
        else:
            self.board.pop()
        # print(f'best stack = {self.board.move_stack}\n', flush=True)

        return best


    # return heuristic for move based on UCT algorithm
    def heuristic(self, parent: str):
        win_percentage = self.get_wins() / self.get_plays()
        exploration = self.C * math.sqrt(math.log(self.get_plays(parent)) / self.get_plays())
        return win_percentage + exploration


    # randomly move until end
    def playout(self):
        stack = self.board.move_stack[:]
        # print(f'playout stack = {stack}\n')

        while not self.board.is_game_over():
            self.board.push(random.choice(list(self.board.legal_moves)))

        self.backpropagate()

        for move in stack:
            self.board.push(move)


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


if __name__ == '__main__':
    NUM_GAMES = 1
    
    board = chess.Board()
    tree = MCTS(board)

    for game in range(NUM_GAMES):
        print(f'Game ({game})')
        while not board.is_game_over():
            move = tree.best_move()
            board.push(move)

        print(chess.pgn.Game().from_board(board))
