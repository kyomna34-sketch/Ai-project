import math
import copy
import random
import pygame
import sys

# ------------------- Connect4 Class -------------------
class Connect4:
    def __init__(self):
        self.rows = 6
        self.cols = 7
        self.EMPTY = 0
        self.PLAYER_X_VAL = 1  # Human/Red
        self.PLAYER_O_VAL = 2  # AI/Yellow
        self.initial_grid = [[self.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

    def take_action(self, state, col, player):
        new_state = [row[:] for row in state]
        val = self.PLAYER_X_VAL if player == "X" else self.PLAYER_O_VAL
        for r in reversed(range(self.rows)):
            if new_state[r][col] == self.EMPTY:
                new_state[r][col] = val
                return new_state
        return new_state

    def available_actions(self, state):
        return [c for c in range(self.cols) if state[0][c] == self.EMPTY]

    @staticmethod
    def current_player(turn_count):
        return "X" if turn_count % 2 == 0 else "O"

    def get_winner(self, state):
        directions = [(1,0),(0,1),(1,1),(-1,1)]
        for r in range(self.rows):
            for c in range(self.cols):
                for dr, dc in directions:
                    line_coords = [(r+i*dr, c+i*dc) for i in range(4)]
                    if all(0<=x<self.rows and 0<=y<self.cols for x,y in line_coords):
                        line = [state[x][y] for x,y in line_coords]
                        if line[0] != self.EMPTY and all(x==line[0] for x in line):
                            winner = "X" if line[0]==self.PLAYER_X_VAL else "O"
                            return winner, line_coords
        return None, []

    def terminal_test(self, state):
        winner,_ = self.get_winner(state)
        if winner:
            return True, winner
        elif all(state[0][c]!=self.EMPTY for c in range(self.cols)):
            return True, None
        else:
            return False, None

    def evaluate(self, state, player):
        opponent = "O" if player=="X" else "X"
        p_val = self.PLAYER_X_VAL if player=="X" else self.PLAYER_O_VAL
        o_val = self.PLAYER_X_VAL if opponent=="X" else self.PLAYER_O_VAL
        score = 0

        def score_group(group):
            s = 0
            if group.count(p_val)==4: s+=100000
            elif group.count(p_val)==3 and group.count(self.EMPTY)==1: s+=50
            elif group.count(p_val)==2 and group.count(self.EMPTY)==2: s+=10
            if group.count(o_val)==3 and group.count(self.EMPTY)==1: s-=70
            elif group.count(o_val)==2 and group.count(self.EMPTY)==2: s-=5
            return s

        center_col = self.cols//2
        for r in range(self.rows):
            if state[r][center_col]==p_val: score+=5
            elif state[r][center_col]==o_val: score-=4

        for r in range(self.rows):
            for c in range(self.cols-3):
                score+=score_group([state[r][c+i] for i in range(4)])
        for r in range(self.rows-3):
            for c in range(self.cols):
                score+=score_group([state[r+i][c] for i in range(4)])
        for r in range(self.rows-3):
            for c in range(self.cols-3):
                score+=score_group([state[r+i][c+i] for i in range(4)])
        for r in range(3,self.rows):
            for c in range(self.cols-3):
                score+=score_group([state[r-i][c+i] for i in range(4)])

        return score

# ------------------- Alpha-Beta AI -------------------
def alpha_beta(game,state,depth,alpha,beta,maximizingPlayer,player):
    terminal,winner=game.terminal_test(state)
    if depth==0 or terminal:
        if terminal:
            if winner==player: return None,1000000000+depth
            elif winner is None: return None,0
            else: return None,-1000000000-depth
        else:
            return None,game.evaluate(state,player)

    actions=game.available_actions(state)
    actions.sort(key=lambda col: abs(col-game.cols//2))

    if maximizingPlayer:
        value=-math.inf
        best_move=random.choice(actions) if actions else None
        for col in actions:
            child=game.take_action(state,col,player)
            _,score=alpha_beta(game,child,depth-1,alpha,beta,False,player)
            if score>value: value,best_move=score,col
            alpha=max(alpha,value)
            if alpha>=beta: break
        return best_move,value
    else:
        value=math.inf
        opponent="O" if player=="X" else "X"
        best_move=random.choice(actions) if actions else None
        for col in actions:
            child=game.take_action(state,col,opponent)
            _,score=alpha_beta(game,child,depth-1,alpha,beta,True,player)
            if score<value: value,best_move=score,col
            beta=min(beta,value)
            if alpha>=beta: break
        return best_move,value


# ----------------------------------------------------
#  GUI HELPER FUNCTIONS SECTION (New Modular Block)
# ----------------------------------------------------

def draw_board(screen, game, state, SQUARESIZE, width, BG_COLOR, BOARD_COLOR, EMPTY_COLOR, RED, YELLOW, TEXT_COLOR, WIN_HIGHLIGHT_COLOR,
               small_font, turn_count, game_over, screen_state, ai_thinking, human_delay_active, hover_col=None, winning_line=[]):
    """Draws the Connect 4 grid, pieces, and current game status."""
    
    # 1. Background and Top/Bottom bars
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, (225, 225, 225), (0, 0, width, SQUARESIZE)) # Top drop area
    pygame.draw.rect(screen, BOARD_COLOR, (0, SQUARESIZE, width, game.rows * SQUARESIZE)) # Main board
    status_y = (game.rows + 1) * SQUARESIZE
    pygame.draw.rect(screen, (225, 225, 225), (0, status_y, width, SQUARESIZE)) # Bottom status area

    # 2. Status text (Bottom Center)
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

        # Current player indicator (Top right)
        indicator_color = RED if current == "X" else YELLOW
        pygame.draw.circle(screen, indicator_color, (width - 30, SQUARESIZE // 2), 15)


    # 3. Draw the cells/circles
    for r in range(game.rows):
        for c in range(game.cols):
            center_x = c * SQUARESIZE + SQUARESIZE // 2
            center_y = r * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2
            radius = SQUARESIZE // 2 - 5 
            
            # Draw the 'hole' first 
            pygame.draw.circle(screen, EMPTY_COLOR, (center_x, center_y), radius)

            piece_color = None
            if state[r][c] == 1:
                piece_color = RED
            elif state[r][c] == 2:
                piece_color = YELLOW

            # Highlight winning pieces
            if piece_color is not None:
                if winning_line and (r, c) in winning_line:
                    piece_color = WIN_HIGHLIGHT_COLOR 

                pygame.draw.circle(screen, piece_color, (center_x, center_y), radius)


    # 4. Hover piece (Human only)
    if hover_col is not None and not game_over:
        if game.current_player(turn_count) == "X" and not ai_thinking and not human_delay_active:
            pygame.draw.circle(
                screen,
                RED,
                (hover_col * SQUARESIZE + SQUARESIZE // 2,
                 SQUARESIZE // 2),
                SQUARESIZE // 2 - 5 
            )

    pygame.display.update()

def animate_drop(screen, game, state, col, player, SQUARESIZE, RED, YELLOW, clock, draw_board_func):
    """Animates the dropping of a piece into a column."""
    color = RED if player == "X" else YELLOW
    
    try:
        row_to_drop = next(
            r for r in reversed(range(game.rows)) if state[r][col] == 0
        )
    except StopIteration:
        return

    start_y = SQUARESIZE // 2
    end_y = row_to_drop * SQUARESIZE + SQUARESIZE + SQUARESIZE // 2
    radius = SQUARESIZE // 2 - 5 
    
    for y in range(start_y, end_y, 20):
        # Pass necessary arguments to the drawing function
        draw_board_func(state, winning_line=[]) 
        pygame.draw.circle(
            screen,
            color,
            (col * SQUARESIZE + SQUARESIZE // 2, y),
            radius
        )
        pygame.display.update()
        clock.tick(60)

def start_screen(screen, width, height, font, small_font, BOARD_COLOR, GREEN, EMPTY_COLOR):
    """Displays the initial start screen."""
    screen.fill((245, 245, 245)) # BG_COLOR local override
    title = font.render("Connect 4", True, BOARD_COLOR)
    screen.blit(title, title.get_rect(center=(width//2, height//3)))

    start_rect = pygame.Rect(width//2 - 100, height//2, 200, 50) 
    pygame.draw.rect(screen, GREEN, start_rect, border_radius=10)

    start_text = small_font.render("Start Game", True, EMPTY_COLOR)
    screen.blit(start_text, start_text.get_rect(center=start_rect.center))

    pygame.display.update()
    return start_rect

def game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR, WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner):
    """Displays the game over screen with Play Again and End Game buttons."""
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

    screen.blit(
        small_font.render("Play Again", True, EMPTY_COLOR),
        small_font.render("Play Again", True, EMPTY_COLOR).get_rect(center=play_rect.center)
    )
    screen.blit(
        small_font.render("End Game", True, EMPTY_COLOR),
        small_font.render("End Game", True, EMPTY_COLOR).get_rect(center=end_rect.center)
    )

    pygame.display.update()
    return play_rect, end_rect


# ----------------------------------------------------
# MAIN GAME LOGIC (play_connect4_gui)
# ----------------------------------------------------

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

    # ---------- Game State Variables ----------
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

    # Wrapper function for draw_board to simplify calling it inside the loop/other helpers
    def draw_board_wrapper(board_state, winning_line=[]):
        return draw_board(
            screen, game, board_state, SQUARESIZE, width, BG_COLOR, BOARD_COLOR, EMPTY_COLOR, RED, YELLOW, TEXT_COLOR, WIN_HIGHLIGHT_COLOR,
            small_font, turn_count, game_over, screen_state, ai_thinking, human_delay_active, hover_col, winning_line
        )
    
    # Wrapper function for animate_drop
    def animate_drop_wrapper(board_state, col, player):
        # We pass the draw_board_wrapper as a dependency
        return animate_drop(screen, game, board_state, col, player, SQUARESIZE, RED, YELLOW, clock, draw_board_wrapper)

    def ai_move():
        nonlocal state, turn_count, ai_thinking, game_over, screen_state
        
        col, _ = alpha_beta(
            game, state, 5, -math.inf, math.inf, True, "O"
        )
        
        if col is not None:
            animate_drop_wrapper(state, col, "O")
            state = game.take_action(state, col, "O")
            turn_count += 1

    # ---------- Main Loop ----------
    start_rect = None
    running = True
    delay_start_time = 0
    winner = None # Initialize winner variable

    while running:
        # Update dynamic variables before drawing/checking state
        current_player = game.current_player(turn_count) if not game_over else None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if screen_state == "START":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect and start_rect.collidepoint(event.pos):
                        screen_state = "GAME"
                        state = copy.deepcopy(game.initial_grid)
                        turn_count = 0
                        game_over = False

            elif screen_state == "GAME" and not game_over and not ai_thinking and not human_delay_active:
                
                if current_player == "X": # Human Player's turn
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
                                play_rect, end_rect = game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR, WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner)
                                screen_state = "GAME_OVER"
                            elif game.current_player(turn_count) == "O":
                                human_delay_active = True
                                delay_start_time = pygame.time.get_ticks()
                                
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
            
        # === Human Move Delay Logic ===
        if screen_state == "GAME" and human_delay_active:
            # Need to redraw board for the 'Wait...' status message
            draw_board_wrapper(state, winning_line=[])
            
            if pygame.time.get_ticks() - delay_start_time > HUMAN_MOVE_DELAY_MS:
                human_delay_active = False
                ai_thinking = True # Start AI turn now

        # AI Turn Logic
        if screen_state == "GAME" and not game_over and ai_thinking and not human_delay_active:
            
            ai_move() 
            ai_thinking = False

            terminal, winner = game.terminal_test(state)
            if terminal:
                _, winning_line_coords = game.get_winner(state)
                draw_board_wrapper(state, winning_line=winning_line_coords) 
                pygame.time.wait(END_SCREEN_DELAY_MS)
                
                game_over = True
                play_rect, end_rect = game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR, WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner)
                screen_state = "GAME_OVER"


        # Drawing Logic
        if screen_state == "GAME":
            # Update hover_col for the draw_board_wrapper state
            hover = hover_col if current_player == "X" and not ai_thinking and not human_delay_active else None
            # Re-bind hover_col for the drawing function call
            temp_hover_col = hover_col
            hover_col = hover 
            draw_board_wrapper(state, winning_line=[])
            hover_col = temp_hover_col # Restore original
            
        elif screen_state == "GAME_OVER":
            # Re-call game_over_screen to update play_rect/end_rect on redraw (in case of window focus changes)
            play_rect, end_rect = game_over_screen(screen, width, height, small_font, BG_COLOR, DRAW_COLOR, WINNER_COLOR, LOSE_COLOR, GREEN, END_RED, EMPTY_COLOR, winner)
        elif screen_state == "START":
            # Re-call start_screen to update start_rect on redraw
            start_rect = start_screen(screen, width, height, font, small_font, BOARD_COLOR, GREEN, EMPTY_COLOR)

        clock.tick(60)

    pygame.quit()
    sys.exit()
if __name__=="__main__":
    play_connect4_gui()
