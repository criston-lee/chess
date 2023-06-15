from const import *
from square import Square
from piece import *
from move import Move
import copy
from sound import Sound
import os


class Board:
    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self._create()
        self._add_pieces("white")
        self._add_pieces("black")
        self.last_move = None

    def _create(self):  # underscore indicates a private function aka cannot be accessed outside the class
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].is_empty()

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        #Pawn Promotion & En Passant
        if isinstance(piece, Pawn):
            # En Passant Capturing
            if final.col - initial.col != 0 and en_passant_empty:
                self.squares[initial.row][final.col].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(os.path.join("assets/sounds/capture.wav"))
                    sound.play()
            else:
                self.check_promotion(piece, final)

        # King Castling
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        # move
        piece.moved = True

        # Clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)
            # now hardcoded queen, can edit to make it other pieces later

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self,piece):
        if not isinstance(piece,Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece,Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True

    def in_check(self,piece,move):
        temp_board = copy.deepcopy(self) #clone board
        temp_piece = copy.deepcopy(piece)
        temp_board.move(temp_piece, move,testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece #just a piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True

        return False
    def _add_pieces(self, color):
        if color == "white":
            row_pawn, row_other = (6, 7)  # White
        else:
            row_pawn, row_other = (1, 0)  # Black

        # For all pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # For knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # For bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # For rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # For Queens
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # EDIT HERE FOR CHANGE QUEEN VS KINGSIDE, IF I WANT TO MAKE A DIFFERENT SIDE KING ALSO CHANGE HERE

        # For Kings
        self.squares[row_other][4] = Square(row_other, 4, King(color))

    def calc_moves(self, piece, row, col, bool=True):
        "Calculate all legal moves of a specific piece, at a given position"

        def knight_moves():
            possible_moves = [
                (row - 2, col + 1),
                (row - 2, col - 1),
                (row + 2, col + 1),
                (row + 2, col - 1),
                (row + 1, col + 2),
                (row + 1, col - 2),
                (row - 1, col + 2),
                (row - 1, col - 2)
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # if square is empty, or there is an enemy piece there (capture), move is valid
                        # assuming nothing in the way of course
                        # below are squares of move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # insert move here
                        move = Move(initial, final)
                        # Check if piece is pinned / blocks check
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

        def pawn_moves():
            steps = 1 if piece.moved else 2

            # Normal Pawn Pushes
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))  # for loop is exclusive, that's why need 1 extra

            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].is_empty():
                        # Create initial and final move squares
                        # Generate new move
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)
                        move = Move(initial, final)

                        #Check if piece is pinned / blocks check
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)



                    else:  # blocked, if cannot 1 square obv cannot 2 square
                        break
                else:
                    break

            # Capture moves
            possible_move_row = row + piece.dir
            possible_move_cols = [col - 1, col + 1]
            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # create new initial and final move squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)

                        # Check if piece is pinned / blocks check
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            #En Passant
            r = 3 if piece.color == 'white' else 4
            final_row = 2 if piece.color == 'white' else 5

            #Left Side
            if Square.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p,Pawn):
                        if p.en_passant:
                            initial = Square(row,col)
                            final = Square(final_row,col-1,p)
                            move = Move(initial,final)
                            if bool:
                                if not self.in_check(piece,move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            #Right Side
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col + 1].has_enemy_piece(piece.color):
                    p = self.squares[row][col + 1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(final_row, col + 1, p)
                            move = Move(initial, final)
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)




        def straight_line_moves(increments):
            for incr in increments:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:  # make it break when hits an enemy piece, else continue loop of finding squares
                    if Square.in_range(possible_move_row, possible_move_col):

                        # create squares of new possible move
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)
                        # create new move
                        move = Move(initial, final)

                        # empty square --> continue loops
                        if self.squares[possible_move_row][possible_move_col].is_empty():
                            # Check if piece is pinned / blocks check
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        # has enemy piece
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            # Check if piece is pinned / blocks check
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break  # stop at piece, cannot continue further

                        # has own piece
                        elif self.squares[possible_move_row][possible_move_col].has_own_piece(piece.color):
                            break  # stop at piece, cannot continue further


                    # not in range
                    else:
                        break

                    # Incrementing the increments, making it hit a wall at all possible moves
                    possible_move_row += row_incr
                    possible_move_col += col_incr

        def king_moves():
            # Normal King Moves
            adjs = [
                (row + 1, col + 1),
                (row + 1, col + 0),
                (row + 1, col - 1),
                (row + 0, col + 1),
                (row + 0, col - 1),
                (row - 1, col + 1),
                (row - 1, col + 0),
                (row - 1, col - 1)
            ]

            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move
                if Square.in_range(possible_move_row, possible_move_col):  # KIV create function for this
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)
                        move = Move(initial, final)
                        # Check if piece is pinned / blocks check
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else:
                                break
                        else:
                            piece.add_move(move)

            # Castling Moves

            if not piece.moved:  # King has not moved

                # Kingside Castle
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for column in range(5, 7):
                            if self.squares[row][column].has_piece():  # piece in between castle
                                break

                            if column == 6:
                                # assigns right rook to king
                                piece.right_rook = right_rook

                                # rook move
                                initial = Square(row, 7)
                                final = Square(row, 5)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 6)
                                moveK = Move(initial, final)
                                if bool: #check if there's a check / pin
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    right_rook.add_move(moveR)
                                    piece.add_move(moveK)


                # Queenside Castle
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for column in range(1, 4):
                            if self.squares[row][column].has_piece():  # piece in between castle
                                break

                            if column == 3:
                                # assigns left rook to king
                                piece.left_rook = left_rook

                                # rook move
                                initial = Square(row, 0)
                                final = Square(row, 3)
                                moveR = Move(initial, final)

                                # king move
                                initial = Square(row, col)
                                final = Square(row, 2)
                                moveK = Move(initial, final)
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        # append new move to rook and king
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    left_rook.add_move(moveR)
                                    piece.add_move(moveK)


        if piece.name == "pawn":
            pawn_moves()

        elif piece.name == "knight":
            knight_moves()

        elif piece.name == "bishop":
            straight_line_moves([
                (-1, 1),  # towards H8
                (-1, -1),  # towards A8
                (1, 1),  # towards A8
                (1, -1)  # towards A1
            ])

        elif piece.name == "rook":
            straight_line_moves([
                (1, 0),  # towards 1st rank
                (-1, 0),  # towards 8th rank
                (0, -1),  # towards A file
                (0, 1)  # towards H file
            ])

        elif piece.name == "queen":
            straight_line_moves([
                (-1, 1),  # towards H8
                (-1, -1),  # towards A8
                (1, 1),  # towards A8
                (1, -1),  # towards A1
                (1, 0),  # towards 1st rank
                (-1, 0),  # towards 8th rank
                (0, -1),  # towards A file
                (0, 1)  # towards H file
            ])

        elif piece.name == "king":
            king_moves()
