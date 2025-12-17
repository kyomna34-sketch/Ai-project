# ----------------------------------------------------
#  GUI HELPER FUNCTIONS
# ----------------------------------------------------
import pygame
import copy
import math
import sys
import random
from connect4 import Connect4
from Ai import alpha_beta

# ----------------------------------------------------
# GUI HELPER FUNCTIONS
# ----------------------------------------------------
def draw_board(screen, game, state, SQUARESIZE, width, BG_COLOR, BOARD_COLOR, EMPTY_COLOR, RED, YELLOW, TEXT_COLOR, WIN_HIGHLIGHT_COLOR,
               small_font, turn_count, game_over, screen_state, ai_thinking, human_delay_active, hover_col=None, winning_line=[]):
    """Draws the Connect 4 grid, pieces, and current game status."""
    
    # 1. Background and Top/Bottom bars
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, (225, 225, 225), (0, 0, width, SQUARESIZE))
    pygame.draw.rect(screen, BOARD_COLOR, (0, SQUARESIZE, width, game.rows * SQUARESIZE))
    status_y = (game.rows + 1) * SQUARESIZE
    pygame.draw.rect(screen, (225, 225, 225), (0, status_y, width, SQUARESIZE))

    # 2. Status text
    if not game_over and screen_state == "GAME":
        current = game.current_player(turn_count)
        if current == "X" and not ai_thinking and not human_delay_active:
            text = "Your Turn (Red)"
            color = RED
        elif current == "O" and ai_thinking:
            text = "AI is thinking..."
            color = TEXT_COLOR
        elif current == "O" and human_delay_active: 
            text = "Wait..."
            color = TEXT_COLOR
        else:
            text = "" 
            color = TEXT_COLOR
        
        if text:
            label = small_font.render(text, True, color)
            center_x = width // 2
            center_y = (game.rows + 1) * SQUARESIZE + SQUARESIZE // 2
            screen.blit(label, label.get_rect(center=(center_x, center_y)))

        indicator_color = RED if current == "X" else YELLOW
        pygame.draw.circle(screen, indicator_color, (width - 30, SQUARESIZE // 2), 15)

    # 3. Draw cells
    for r in range(game.rows):
        for c in range(game.cols):
            center_x = c * SQUARESIZE + SQUARESIZE // 2
            center_y = r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2
            radius = SQUARESIZE // 2 - 5 
            pygame.draw.circle(screen, EMPTY_COLOR, (center_x, center_y), radius)

            piece_color = None
            if state[r][c] == 1:
                piece_color = RED
            elif state[r][c] == 2:
                piece_color = YELLOW

            if piece_color is not None and winning_line and (r, c) in winning_line:
                piece_color = WIN_HIGHLIGHT_COLOR 

            if piece_color is not None:
                pygame.draw.circle(screen, piece_color, (center_x, center_y), radius)

    # 4. Hover piece
    if hover_col is not None and not game_over:
        if game.current_player(turn_count) == "X" and not ai_thinking and not human_delay_active:
            pygame.draw.circle(screen, RED, (hover_col * SQUARESIZE + SQUARESIZE // 2, SQUARESIZE // 2), SQUARESIZE // 2 - 5)

    pygame.display.update()


def animate_drop(screen, game, state, col, player, SQUARESIZE, RED, YELLOW, clock, draw_board_func):
    color = RED if player == "X" else YELLOW
    try:
        row_to_drop = next(r for r in reversed(range(game.rows)) if state[r][col] == 0)
    except StopIteration:
        return

    start_y = SQUARESIZE // 2
    end_y = row_to_drop * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2
    radius = SQUARESIZE // 2 - 5 
    
    for y in range(start_y, end_y, 20):
        draw_board_func(state, winning_line=[])
        pygame.draw.circle(screen, color, (col * SQUARESIZE + SQUARESIZE // 2, y), radius)
        pygame.display.update()
        clock.tick(60)


def start_screen(screen, width, height, font, small_font, BOARD_COLOR, GREEN, EMPTY_COLOR):
    screen.fill((245, 245, 245))
    title = font.render("Connect 4", True, BOARD_COLOR)
    screen.blit(title, title.get_rect(center=(width//2, height//3)))

    start_rect = pygame.Rect(width//2 - 100, height//2, 200, 50)
    pygame.draw.rect(screen, GREEN, start_rect, border_radius=10)
    start_text = small_font.render("Start Game", True, EMPTY_COLOR)
    screen.blit(start_text, start_text.get_rect(center=start_rect.center))

    pygame.display.update()
    return start_rect


def game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR, WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner):
    screen.fill(BG_COLOR)
    if winner is None:
        text = "Game Over: Draw!"
        color = DRAW_COLOR 
    else:
        text = "YOU WIN! " if winner == 'X' else "YOU LOSE! "
        color = WINNER_COLOR if winner == 'X' else LOSE_COLOR
        
    label = small_font.render(text, True, color)
    screen.blit(label, label.get_rect(center=(width//2, height//3)))

    play_rect = pygame.Rect(width//2 - 100, height//2, 200, 50)
    end_rect = pygame.Rect(width//2 - 100, height//2 + 70, 200, 50)
    pygame.draw.rect(screen, GREEN, play_rect, border_radius=10)
    pygame.draw.rect(screen, END_RED, end_rect, border_radius=10)

    screen.blit(small_font.render("Play Again", True, EMPTY_COLOR), small_font.render("Play Again", True, EMPTY_COLOR).get_rect(center=play_rect.center))
    screen.blit(small_font.render("End Game", True, EMPTY_COLOR), small_font.render("End Game", True, EMPTY_COLOR).get_rect(center=end_rect.center))

    pygame.display.update()
    return play_rect, end_rect
