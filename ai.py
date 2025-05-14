import numpy as np
import random
from const import *
from square import Square
from piece import *
from move import Move
from board import Board
import traceback

piece_values = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
    "king": 100  # High value, but not so high it distorts calculations
}

class SimpleNN:
    def __init__(self):
        self.weights = np.random.randn(64)  # One input per square (simplified)

    def evaluate(self, board_squares):
        # Simple material evaluation plus positional factors
        score = 0
        
        # Material score
        for row in range(ROWS):
            for col in range(COLS):
                square = board_squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    # Add proper piece value
                    value = piece_values.get(piece.name, 0)
                    sign = 1 if piece.color == "white" else -1
                    score += value * sign
                    
                    # Simple positional bonus for pawns
                    if piece.name == "pawn":
                        # Pawns are more valuable as they advance
                        if piece.color == "white":
                            score += 0.05 * (7 - row)  # White pawns advance toward row 0
                        else:
                            score += 0.05 * row  # Black pawns advance toward row 7
                            
                    # Center control bonus
                    if (2 <= row <= 5) and (2 <= col <= 5):
                        score += 0.05 * sign
                        
        return score

class AIPlayer:
    def __init__(self, depth=3):
        self.nn = SimpleNN()
        self.depth = depth
        print(f"AI Player initialized with depth {depth}")

    def get_best_move(self, board_squares, color):
        print(f"AI thinking for {color}...")
        best_score = float('-inf') if color == "white" else float('inf')
        best_move = None
        valid_moves_count = 0
        
        # Create a temporary board for move calculations
        temp_board = Board()
        temp_board.squares = board_squares
        
        # Find all valid moves for the AI's color
        for row in range(ROWS):
            for col in range(COLS):
                square = board_squares[row][col]
                if square.has_piece() and square.piece.color == color:
                    piece = square.piece
                    # Calculate possible moves for this piece
                    temp_board.calc_moves(piece, row, col, bool=True)
                    
                    for move in piece.moves:
                        # Make the move
                        old_piece = board_squares[move.final.row][move.final.col].piece
                        board_squares[move.final.row][move.final.col].piece = piece
                        board_squares[move.initial.row][move.initial.col].piece = None
                        
                        # Evaluate the move
                        if color == "white":
                            score = self.minimax(temp_board, self.depth - 1, False, float('-inf'), float('inf'))
                            if score > best_score:
                                best_score = score
                                best_move = move
                        else:
                            score = self.minimax(temp_board, self.depth - 1, True, float('-inf'), float('inf'))
                            if score < best_score:
                                best_score = score
                                best_move = move
                        
                        # Undo the move
                        board_squares[move.initial.row][move.initial.col].piece = piece
                        board_squares[move.final.row][move.final.col].piece = old_piece
                        
        return best_move
        

    def minimax(self, board, depth, maximizing, alpha, beta):
        if depth == 0:
            return self.nn.evaluate(board.squares)
        
        if maximizing:  # White's turn (maximize)
            max_eval = float('-inf')
            for row in range(ROWS):
                for col in range(COLS):
                    square = board.squares[row][col]
                    if square.has_piece() and square.piece.color == "white":
                        piece = square.piece
                        board.calc_moves(piece, row, col, bool=True)
                        
                        for move in piece.moves:
                            # Make move
                            old_piece = board.squares[move.final.row][move.final.col].piece
                            board.squares[move.final.row][move.final.col].piece = piece
                            board.squares[move.initial.row][move.initial.col].piece = None
                            
                            # Evaluate
                            eval = self.minimax(board, depth - 1, False, alpha, beta)
                            max_eval = max(max_eval, eval)
                            
                            # Undo move
                            board.squares[move.initial.row][move.initial.col].piece = piece
                            board.squares[move.final.row][move.final.col].piece = old_piece
                            
                            # Alpha-beta pruning
                            alpha = max(alpha, eval)
                            if beta <= alpha:
                                break
            return max_eval
        
        else:  # Black's turn (minimize)
            min_eval = float('inf')
            for row in range(ROWS):
                for col in range(COLS):
                    square = board.squares[row][col]
                    if square.has_piece() and square.piece.color == "black":
                        piece = square.piece
                        board.calc_moves(piece, row, col, bool=True)
                        
                        for move in piece.moves:
                            # Make move
                            old_piece = board.squares[move.final.row][move.final.col].piece
                            board.squares[move.final.row][move.final.col].piece = piece
                            board.squares[move.initial.row][move.initial.col].piece = None
                            
                            # Evaluate
                            eval = self.minimax(board, depth - 1, True, alpha, beta)
                            min_eval = min(min_eval, eval)
                            
                            # Undo move
                            board.squares[move.initial.row][move.initial.col].piece = piece
                            board.squares[move.final.row][move.final.col].piece = old_piece
                            
                            # Alpha-beta pruning
                            beta = min(beta, eval)
                            if beta <= alpha:
                                break
            return min_eval
