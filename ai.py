import numpy as np
import random
from const import *
from square import Square
from piece import *
from move import Move
from board import Board
import traceback
import os

# Import TensorFlow - make sure it's installed
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    from tensorflow.keras import layers, models
    TF_AVAILABLE = True
except ImportError:
    print("TensorFlow not available, falling back to simple evaluation")
    TF_AVAILABLE = False

piece_values = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
    "king": 100  # High value, but not so high it distorts calculations
}

# Piece-Square tables for positional evaluation
# These tables provide bonus/penalty values for piece positions
pawn_table = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

knight_table = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]

bishop_table = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]

rook_table = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0]
]

queen_table = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]

king_middle_table = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

king_end_table = [
    [-50, -40, -30, -20, -20, -30, -40, -50],
    [-30, -20, -10, 0, 0, -10, -20, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 30, 40, 40, 30, -10, -30],
    [-30, -10, 20, 30, 30, 20, -10, -30],
    [-30, -30, 0, 0, 0, 0, -30, -30],
    [-50, -30, -30, -30, -30, -30, -30, -50]
]

piece_position_tables = {
    "pawn": pawn_table,
    "knight": knight_table,
    "bishop": bishop_table,
    "rook": rook_table,
    "queen": queen_table,
    "king": king_middle_table  # Default to middle game
}

# Updated class to encode chess board for neural network
class ChessEncoder:
    @staticmethod
    def board_to_matrix(board_squares):
        # Create an 8x8x12 matrix representation for the neural network
        # 12 channels for 6 piece types × 2 colors
        matrix = np.zeros((8, 8, 12))
        
        for row in range(ROWS):
            for col in range(COLS):
                square = board_squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    # Map piece type to index
                    piece_type_map = {
                        "pawn": 0,
                        "knight": 1,
                        "bishop": 2,
                        "rook": 3,
                        "queen": 4,
                        "king": 5
                    }
                    
                    piece_type = piece_type_map.get(piece.name, 0)
                    # Add color offset (0 for white, 6 for black)
                    piece_color = 0 if piece.color == "white" else 6
                    matrix[row, col, piece_type + piece_color] = 1
                    
        return matrix[np.newaxis, ...]  # Add batch dimension

# Improved evaluator with position tables for better positional understanding
class ImprovedEvaluator:
    def __init__(self):
        pass
        
    def evaluate(self, board_squares):
        # Material and positional evaluation
        score = 0
        material_score = 0
        position_score = 0
        
        # Check if endgame (simplified check - fewer than 10 pieces)
        piece_count = 0
        for row in range(ROWS):
            for col in range(COLS):
                if board_squares[row][col].has_piece():
                    piece_count += 1
        
        is_endgame = piece_count <= 10
        
        # Material and position score
        for row in range(ROWS):
            for col in range(COLS):
                square = board_squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    # Add proper piece value
                    value = piece_values.get(piece.name, 0)
                    sign = 1 if piece.color == "white" else -1
                    material_score += value * sign
                    
                    # Position value from tables
                    position_table = piece_position_tables.get(piece.name)
                    
                    # Special case for king in endgame
                    if piece.name == "king" and is_endgame:
                        position_table = king_end_table
                    
                    if position_table:
                        # For black pieces, we need to flip the table
                        if piece.color == "white":
                            position_score += position_table[row][col] * 0.01 * sign
                        else:
                            position_score += position_table[7-row][col] * 0.01 * sign
                    
        # Control of center squares
        center_control = 0
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for row, col in center_squares:
            square = board_squares[row][col]
            if square.has_piece():
                center_control += 0.1 if square.piece.color == "white" else -0.1
                
        # Combine all evaluation factors
        score = material_score + position_score + center_control
        
        return score

# This class creates a custom model if the saved model can't be loaded
class ModelBuilder:
    @staticmethod
    def create_chess_model():
        if not TF_AVAILABLE:
            return None
            
        try:
            # Build a new CNN model for chess position evaluation
            model = models.Sequential([
                layers.Conv2D(64, (3, 3), activation='relu', input_shape=(8, 8, 12), padding='same'),
                layers.BatchNormalization(),
                layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
                layers.BatchNormalization(),
                layers.Flatten(),
                layers.Dense(256, activation='relu'),
                layers.Dropout(0.3),
                layers.Dense(1, activation='tanh')  # Output a single evaluation score between -1 and 1
            ])
            
            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            print("Created new chess model")
            return model
        except Exception as e:
            print(f"Failed to create model: {e}")
            return None

# Neural Network evaluator using TensorFlow model with better error handling
class NeuralNetworkEvaluator:
    def __init__(self, model_path="./ai_models/TF_50EPOCHS.keras"):
        self.model = None
        
        # Try to load the model with improved error handling
        if TF_AVAILABLE:
            try:
                # allow legacy fields in the .keras archive
                self.model = tf.keras.models.load_model(
                    model_path,
                    compile=False,      # not training here
                    safe_mode=False     # ← key line
                )
                print(f"Loaded NN model from {model_path}")
            except Exception as e:
                print(f"Error loading saved model: {e}")
                print("Attempting to create a new model...")
                self.model = ModelBuilder.create_chess_model()
    
    def evaluate(self, board_squares):
        # If model is still not available, fall back to improved evaluator
        if self.model is None:
            improved_eval = ImprovedEvaluator()
            return improved_eval.evaluate(board_squares)
        
        try:
            # Convert board to matrix representation for the neural network
            input_matrix = ChessEncoder.board_to_matrix(board_squares)
            
            # Get model predictions
            prediction = self.model.predict(input_matrix, verbose=0)
            
            # For a model that outputs a single evaluation score
            if prediction.shape[-1] == 1:
                # Scale from [-1, 1] to a reasonable chess evaluation range
                nn_eval = float(prediction[0][0]) * 10  # Scale to roughly -10 to +10
            else: 
                # For models that output move probabilities or other formats
                # We'll still need a fallback evaluation
                improved_eval = ImprovedEvaluator()
                basic_eval = improved_eval.evaluate(board_squares)
                
                # Use confidence of best move as a modifier to the basic evaluation
                confidence = np.max(prediction)
                side_advantage = 1 if basic_eval > 0 else -1
                nn_eval = basic_eval + (confidence * side_advantage)
            
            return nn_eval
            
        except Exception as e:
            print(f"Error in neural network evaluation: {e}")
            print(traceback.format_exc())
            # Fall back to improved evaluator
            improved_eval = ImprovedEvaluator()
            return improved_eval.evaluate(board_squares)

class AIPlayer:
    def __init__(self, depth=3, use_nn=True):
        self.depth = depth
        
        # Try to use neural network if requested
        if use_nn and TF_AVAILABLE:
            self.evaluator = NeuralNetworkEvaluator()
            print(f"AI Player initialized with neural network evaluation, depth {depth}")
        else:
            self.evaluator = ImprovedEvaluator()
            print(f"AI Player initialized with improved evaluation, depth {depth}")

    def get_best_move(self, board_squares, color):
        print(f"AI thinking for {color}...")
        best_score = float('-inf') if color == "white" else float('inf')
        best_move = None
        valid_moves_count = 0
        all_valid_moves = []
        
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
                        all_valid_moves.append((piece, move))
        
        # Randomize move order for better search and less predictable play
        random.shuffle(all_valid_moves)
        
        # Evaluate each move
        for piece, move in all_valid_moves:
            valid_moves_count += 1
            
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
        
        print(f"Analyzed {valid_moves_count} possible moves")
        
        # If no best move found (shouldn't happen in normal gameplay)
        if best_move is None and len(all_valid_moves) > 0:
            print("Warning: No best move found, selecting random move")
            piece, move = random.choice(all_valid_moves)
            best_move = move
            
        return best_move
        
    def minimax(self, board, depth, maximizing, alpha, beta):
        # Terminal node or max depth reached
        if depth == 0:
            return self.evaluator.evaluate(board.squares)
        
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
                                
                    if beta <= alpha:
                        break
                        
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
                                
                    if beta <= alpha:
                        break
                        
                if beta <= alpha:
                    break
                    
            return min_eval