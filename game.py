import pygame
from const import *
from board import Board
from dragger import Dragger
from move import Move
from config import Config
from square import Square

class Game:
    def __init__(self):
        self.next_player = "white"
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
    
    #Blit methods

    def show_bg(self,surface):
        theme = self.config.theme
        #Draw board
        for row in range(ROWS):
            for col in range(COLS):

                #color of board
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark

                rectangle = (col * SQSIZE,row * SQSIZE, SQSIZE, SQSIZE)

                pygame.draw.rect(surface,color,rectangle)

                #Show coordinates
                if col == 0:
                    # show color
                    color = theme.bg.dark if row % 2 ==0 else theme.bg.light

                    #show label
                    lbl = self.config.font.render(str(ROWS-row),1,color)
                    lbl_pos = (3,5+row * SQSIZE)

                    #blit label
                    surface.blit(lbl,lbl_pos)

                if row == 7:
                    color = theme.bg.dark if (row+col) % 2 == 0 else theme.bg.light

                    # show label
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 78, HEIGHT - 20)

                    # blit label
                    surface.blit(lbl, lbl_pos)





    def show_pieces(self,surface):
        for row in range(ROWS):
            for col in range(COLS):
                #check if piece in square
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    #All pieces except the one being dragged
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80) #Default parameter anw, but nicer to be explicit
                        img = pygame.image.load(piece.texture)
                        img_center = col*SQSIZE + SQSIZE // 2,row * SQSIZE + SQSIZE // 2 #Centralises Image
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img,piece.texture_rect) #Surface received image, and tells it where to be placed
    
    def show_moves(self,surface):
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece
            #loop all valid moves
            for move in piece.moves:

                #color
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark

                #rect
                #now is a coloring the entire sqaure, next time make it a dot?
                rectangle = (move.final.col * SQSIZE,move.final.row * SQSIZE, SQSIZE, SQSIZE)
                
                #blit
                pygame.draw.rect(surface,color,rectangle)
    
    def show_last_move(self,surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final
            
            for position in [initial,final]:
                #color
                color = theme.trace.light if (position.row + position.col) % 2 == 0 else theme.trace.dark

                #rect
                #now is a coloring the entire sqaure, next time make it a dot?
                rectangle = (position.col * SQSIZE,position.row * SQSIZE, SQSIZE, SQSIZE)
                
                #blit
                pygame.draw.rect(surface,color,rectangle)
    
    def show_hover(self,surface):
        if self.hovered_sqr:
            #color
                color = (180,180,180) #if (position.row + position.col)%2==0 else something...

                #rect
                #now is a coloring the entire sqaure, next time make it a dot?
                rectangle = (self.hovered_sqr.col * SQSIZE,self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
                
                #blit
                pygame.draw.rect(surface,color,rectangle,width=3)

    #Other methods
    def next_turn(self):
        self.next_player = 'white' if self.next_player == "black" else "black"
    

    def set_hover(self,row,col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self,captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()




