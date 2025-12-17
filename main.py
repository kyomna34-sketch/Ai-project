# ------------------- Main Game Loop -------------------
import pygame
import sys
import copy
import math
from connect4 import Connect4
from Ai import alpha_beta
from draw import draw_board, animate_drop, start_screen, game_over_screen


def play_connect4_gui():
    pygame.init()
    pygame.font.init()

    # ---------- Colors and Constants ----------
    BG_COLOR = (245, 245, 245)
    BOARD_COLOR = (65, 105, 225)
    EMPTY_COLOR = (255, 255, 255)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    TEXT_COLOR = (40, 40, 40)
    GREEN = (80, 180, 80)
    END_RED = (200, 80, 80)
    WINNER_COLOR = (0, 150, 0)
    LOSE_COLOR = (200, 50, 50)
    DRAW_COLOR = (150, 150, 150)
    WIN_HIGHLIGHT_COLOR = (255, 140, 0)
    SQUARESIZE = 80

    game = Connect4()
    width = game.cols * SQUARESIZE
    height = (game.rows + 2) * SQUARESIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Connect 4 – Human vs AI")

    font = pygame.font.SysFont("arial", 50, bold=True)
    small_font = pygame.font.SysFont("arial", 25, bold=True)
    clock = pygame.time.Clock()

    state = copy.deepcopy(game.initial_grid)
    turn_count = 0
    game_over = False
    screen_state = "START"
    hover_col = None
    play_rect = end_rect = None
    ai_thinking = False
    human_delay_active = False
    HUMAN_MOVE_DELAY_MS = 750
    END_SCREEN_DELAY_MS = 1500

    def draw_board_wrapper(board_state, winning_line=[]):
        return draw_board(screen, game, board_state, SQUARESIZE, width, BG_COLOR, BOARD_COLOR, EMPTY_COLOR, RED, YELLOW, TEXT_COLOR,
                          WIN_HIGHLIGHT_COLOR, small_font, turn_count, game_over, screen_state, ai_thinking, human_delay_active, hover_col, winning_line)

    def animate_drop_wrapper(board_state, col, player):
        return animate_drop(screen, game, board_state, col, player, SQUARESIZE, RED, YELLOW, clock, draw_board_wrapper)

    def ai_move():
        nonlocal state, turn_count, ai_thinking, game_over, screen_state
        col, _ = alpha_beta(game, state, 5, -math.inf, math.inf, True, "O")
        if col is not None:
            animate_drop_wrapper(state, col, "O")
            state = game.take_action(state, col, "O")
            turn_count += 1

    # ---------- Main Loop ----------
    start_rect = None
    running = True
    delay_start_time = 0
    winner = None

    while running:
        current_player = game.current_player(turn_count) if not game_over else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ---------- START SCREEN ----------
            if screen_state == "START":
                if event.type == pygame.MOUSEBUTTONDOWN and start_rect and start_rect.collidepoint(event.pos):
                    screen_state = "GAME"
                    state = copy.deepcopy(game.initial_grid)
                    turn_count = 0
                    game_over = False
                    winner = None

            # ---------- GAME SCREEN ----------
            elif screen_state == "GAME" and not game_over and not ai_thinking and not human_delay_active:
                if current_player == "X":
                    if event.type == pygame.MOUSEMOTION:
                        hover_col = event.pos[0] // SQUARESIZE
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        col = event.pos[0] // SQUARESIZE
                        if col in game.available_actions(state):
                            animate_drop_wrapper(state, col, "X")
                            state = game.take_action(state, col, "X")
                            turn_count += 1

                            terminal, winner = game.terminal_test(state)
                            if terminal:
                                _, winning_line_coords = game.get_winner(state)
                                draw_board_wrapper(state, winning_line=winning_line_coords)
                                pygame.time.wait(END_SCREEN_DELAY_MS)
                                game_over = True
                                play_rect, end_rect = game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR,
                                                                       WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner)
                                screen_state = "GAME_OVER"
                            elif game.current_player(turn_count) == "O":
                                human_delay_active = True
                                delay_start_time = pygame.time.get_ticks()

            # ---------- GAME OVER SCREEN ----------
            elif screen_state == "GAME_OVER":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_rect and play_rect.collidepoint(event.pos):
                        state = copy.deepcopy(game.initial_grid)
                        turn_count = 0
                        game_over = False
                        screen_state = "GAME"
                        winner = None
                    elif end_rect and end_rect.collidepoint(event.pos):
                        running = False

        # ---------- Human Delay Logic ----------
        if screen_state == "GAME" and human_delay_active:
            draw_board_wrapper(state, winning_line=[])
            if pygame.time.get_ticks() - delay_start_time > HUMAN_MOVE_DELAY_MS:
                human_delay_active = False
                ai_thinking = True

        # ---------- AI Turn Logic ----------
        if screen_state == "GAME" and not game_over and ai_thinking and not human_delay_active:
            ai_move()
            ai_thinking = False
            terminal, winner = game.terminal_test(state)
            if terminal:
                _, winning_line_coords = game.get_winner(state)
                draw_board_wrapper(state, winning_line=winning_line_coords)
                pygame.time.wait(END_SCREEN_DELAY_MS)
                game_over = True
                play_rect, end_rect = game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR,
                                                       WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner)
                screen_state = "GAME_OVER"

        # ---------- Drawing ----------
        if screen_state == "GAME":
            hover = hover_col if current_player == "X" and not ai_thinking and not human_delay_active else None
            temp_hover_col = hover_col
            hover_col = hover
            draw_board_wrapper(state, winning_line=[])
            hover_col = temp_hover_col
        elif screen_state == "GAME_OVER":
            play_rect, end_rect = game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR,
                                                   WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner)
        elif screen_state == "START":
            start_rect = start_screen(screen, width, height, font, small_font, BOARD_COLOR, GREEN, EMPTY_COLOR)

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    play_connect4_gui()
