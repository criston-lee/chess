import pygame
import sys
import random

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

        # Define buttons
        self.hvh_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 70, 300, 60)
        self.hvai_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 10, 300, 60)

    def draw_title_screen(self):
        self.screen.fill((30, 30, 30))
        font = pygame.font.SysFont("arial", 60)
        small_font = pygame.font.SysFont("arial", 36)

        title_text = font.render("Choose Game Mode", True, (255, 255, 255))
        self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

        pygame.draw.rect(self.screen, (70, 130, 180), self.hvh_button)
        pygame.draw.rect(self.screen, (180, 70, 70), self.hvai_button)

        hvh_text = small_font.render("Human vs Human", True, (255, 255, 255))
        hvai_text = small_font.render("Human vs AI", True, (255, 255, 255))

        self.screen.blit(hvh_text, (self.hvh_button.centerx - hvh_text.get_width() // 2,
                                    self.hvh_button.centery - hvh_text.get_height() // 2))

        self.screen.blit(hvai_text, (self.hvai_button.centerx - hvai_text.get_width() // 2,
                                     self.hvai_button.centery - hvai_text.get_height() // 2))

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
                            self.mode = "game"
                            self.player_color = "white"  # Human vs Human both default to white

                        elif self.hvai_button.collidepoint(event.pos):
                            self.mode = "game"
                            self.player_color = random.choice(["white", "black"])
                            self.game.set_ai_mode(enable=True)
                            print("Human is:", self.player_color)

                elif self.mode == "game":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        dragger.update_mouse(event.pos)
                        clicked_row = dragger.mouseY // SQSIZE
                        clicked_col = dragger.mouseX // SQSIZE

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
                        if dragger.dragging:
                            dragger.update_mouse(event.pos)
                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE

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
                                game.check_game_over_checkmate()

                        dragger.undrag_piece()

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_t:
                            game.change_theme()
                        elif event.key == pygame.K_r:
                            game.reset()
                            game = self.game
                            board = self.game.board
                            dragger = self.game.dragger

            pygame.display.update()


if __name__ == "__main__":
    main = Main()
    main.mainloop()
