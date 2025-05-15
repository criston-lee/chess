import pygame
import sys
import random
import traceback

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
        self.mode = "title"
        self.player_color = None

        # Define buttons for the main menu
        self.hvh_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 60)
        self.hvai_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 20, 300, 60)
        self.ai_advanced_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 60)

    def draw_title_screen(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont("arial", 60)
        small_font = pygame.font.SysFont("arial", 36)

        title_text = font.render("Chess Game", True, (255, 255, 255))
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Draw buttons
        pygame.draw.rect(self.screen, (70, 130, 180), self.hvh_button)
        pygame.draw.rect(self.screen, (180, 70, 70), self.hvai_button)
        pygame.draw.rect(self.screen, (70, 180, 70), self.ai_advanced_button)

        # Draw button text
        hvh_text = small_font.render("Human vs Human", True, (255, 255, 255))
        hvai_text = small_font.render("Human vs AI (Basic)", True, (255, 255, 255))
        ai_advanced_text = small_font.render("Human vs AI (Neural Net)", True, (255, 255, 255))

        self.screen.blit(hvh_text, (self.hvh_button.centerx - hvh_text.get_width() // 2,
                                    self.hvh_button.centery - hvh_text.get_height() // 2))

        self.screen.blit(hvai_text, (self.hvai_button.centerx - hvai_text.get_width() // 2,
                                     self.hvai_button.centery - hvai_text.get_height() // 2))
                                     
        self.screen.blit(ai_advanced_text, (self.ai_advanced_button.centerx - ai_advanced_text.get_width() // 2,
                                     self.ai_advanced_button.centery - ai_advanced_text.get_height() // 2))

    def mainloop(self):
        game = self.game
        screen = self.screen
        board = self.game.board
        dragger = self.game.dragger

        while True:
            if self.mode == "title":
                self.draw_title_screen()
            else:
                game.show_bg(screen)
                game.show_last_move(screen)
                game.show_moves(screen)
                game.show_pieces(screen)
                game.show_hover(screen)

                if dragger.dragging:
                    dragger.update_blit(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.mode == "title":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.hvh_button.collidepoint(event.pos):
                            print("Selected Human vs Human mode")
                            self.mode = "game"
                            game.vs_ai = False
                            game.ai = None
                            self.player_color = "white"  # Human vs Human both default to white

                        elif self.hvai_button.collidepoint(event.pos):
                            print("Selected Human vs AI (Basic) mode")
                            self.mode = "game"
                            # Randomly assign human to white or black
                            self.player_color = random.choice(["white", "black"])
                            # AI gets the opposite color
                            ai_color = "black" if self.player_color == "white" else "white"
                            print(f"Human is: {self.player_color}, AI is: {ai_color}")
                            
                            # Use simple evaluation, depth 2
                            game.set_ai_mode(enable=True, ai_color=ai_color, depth=2, use_nn=False) 
                            
                            # If AI is white, it should make the first move
                            if ai_color == "white":
                                print("AI should make first move")
                                pygame.display.update()  # Update display before AI thinks
                                game.try_ai_move()
                                
                        elif self.ai_advanced_button.collidepoint(event.pos):
                            print("Selected Human vs AI (Neural Net) mode")
                            self.mode = "game"
                            # Randomly assign human to white or black
                            self.player_color = random.choice(["white", "black"])
                            # AI gets the opposite color
                            ai_color = "black" if self.player_color == "white" else "white"
                            print(f"Human is: {self.player_color}, AI is: {ai_color}")
                            
                            # Use neural network, depth 2
                            game.set_ai_mode(enable=True, ai_color=ai_color, depth=1, use_nn=True) 
                            
                            # If AI is white, it should make the first move
                            if ai_color == "white":
                                print("AI should make first move")
                                pygame.display.update()  # Update display before AI thinks
                                game.try_ai_move()

                elif self.mode == "game":
                    # Only allow the human player to interact when it's their turn
                    human_turn = (not game.vs_ai) or (game.next_player == self.player_color)
                    
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if human_turn:
                            dragger.update_mouse(event.pos)
                            clicked_row = dragger.mouseY // SQSIZE
                            clicked_col = dragger.mouseX // SQSIZE

                            # Safety check
                            if 0 <= clicked_row < ROWS and 0 <= clicked_col < COLS:
                                if board.squares[clicked_row][clicked_col].has_piece():
                                    piece = board.squares[clicked_row][clicked_col].piece
                                    if piece.color == game.next_player:
                                        board.calc_moves(piece, clicked_row, clicked_col, bool=True)
                                        dragger.save_initial(event.pos)
                                        dragger.drag_piece(piece)
                                        game.show_bg(screen)
                                        game.show_moves(screen)

                    elif event.type == pygame.MOUSEMOTION:
                        motion_row = event.pos[1] // SQSIZE
                        motion_col = event.pos[0] // SQSIZE
                        
                        # Safety check
                        if 0 <= motion_row < ROWS and 0 <= motion_col < COLS:
                            game.set_hover(motion_row, motion_col)

                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            game.show_hover(screen)
                            dragger.update_blit(screen)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if human_turn and dragger.dragging:
                            dragger.update_mouse(event.pos)
                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

                            # Safety check
                            if 0 <= released_row < ROWS and 0 <= released_col < COLS:
                                initial = Square(dragger.initial_row, dragger.initial_col)
                                final = Square(released_row, released_col)
                                move = Move(initial, final)

                                if board.valid_move(dragger.piece, move):
                                    captured = board.squares[released_row][released_col].has_piece()
                                    board.move(dragger.piece, move)
                                    board.set_true_en_passant(dragger.piece)
                                    game.play_sound(captured)
                                    game.show_bg(screen)
                                    game.show_last_move(screen)
                                    game.show_pieces(screen)
                                    game.next_turn()
                                    game.check_game_over()

                        dragger.undrag_piece()

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_t:
                            game.change_theme()
                        elif event.key == pygame.K_r:
                            print("Resetting game")
                            game.reset()
                            self.mode = "title"  # Reset to title screen
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger

            pygame.display.update()
        


if __name__ == "__main__":
    main = Main()
    main.mainloop()