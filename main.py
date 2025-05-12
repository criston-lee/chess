import pygame
import sys

from const import *
from game import Game
from square import Square
from move import Move

class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Personal Chessboard")
        self.game = Game()

    def mainloop(self):

        game = self.game
        screen = self.screen
        board = self.game.board
        dragger = self.game.dragger

        while True:
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)

            game.show_hover(screen)

            if dragger.dragging: #Prevents stuttering
                dragger.update_blit(screen)

        
            for event in pygame.event.get():
                #Is there right click to do highlights?

                #Mouse click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)

                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    #Check if clicked square contains a piece
                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece

                        #check if piece is of correct color
                        if piece.color == game.next_player:
                            board.calc_moves(piece,clicked_row,clicked_col, bool=True)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece) 
                            #impt to do above within for loop, so it doesn't activate when we click on an empty square

                            game.show_bg(screen)
                            game.show_moves(screen)

                
                #Mouse Motion
                elif event.type == pygame.MOUSEMOTION:

                    motion_row = event.pos[1]//SQSIZE
                    motion_col=event.pos[0]//SQSIZE

                    game.set_hover(motion_row,motion_col)

                    if dragger.dragging: #Default False, only true when above satisfied
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)



                #Click Release
                elif event.type == pygame.MOUSEBUTTONUP:
                    
                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        released_row = dragger.mouseY // SQSIZE
                        released_col = dragger.mouseX // SQSIZE

                        #create possible move

                        initial = Square(dragger.initial_row,dragger.initial_col)
                        final = Square(released_row,released_col)
                        move = Move(initial,final)

                        #checking if move is valid
                        if board.valid_move(dragger.piece,move):
                            captured = board.squares[released_row][released_col].has_piece()
                            board.move(dragger.piece,move)

                            board.set_true_en_passant(dragger.piece)

                            #Play sound
                            game.play_sound(captured)

                            #show methods
                            game.show_bg(screen)

                            #On top of bg, below pieces
                            game.show_last_move(screen)

                            game.show_pieces(screen)

                            #next turn
                            game.next_turn() 

                            game.check_game_over()                  
                    
                    dragger.undrag_piece()


                #Key Press
                elif event.type == pygame.KEYDOWN:

                    #change theme
                    if event.key == pygame.K_t:
                        game.change_theme()

                    #Restart game
                    if event.key == pygame.K_r:
                        game.reset()
                        game = self.game
                        board = self.game.board
                        dragger = self.game.dragger


                #Quit App
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit() 





            pygame.display.update()


main = Main()
main.mainloop()