import math
import copy
from Ai import alpha_beta
from main import Connect4

# ------------------ Display Board ------------------
def display_board(game, state):
    print("\nCurrent Board:\n")
    for row in state:
        print("|", end=" ")
        for cell in row:
            if cell == 0:
                print(".", end=" ")
            elif cell == 1:
                print("X", end=" ")
            else:
                print("O", end=" ")
        print("|")
    print("  ", end="")
    for c in range(game.cols):
        print(c + 1, end=" ")
    print("\n")

# ------------------- Human Play -------------------
def human_play(game, state, turn_count):
    player = game.current_player(turn_count)
    print(f"Your turn, Player {player}")
    valid_columns = game.available_actions(state)
    col = -1
    while col not in valid_columns:
        try:
            col = int(input("Choose a column (1-7): ")) - 1
            if col not in valid_columns:
                print("Invalid move, try again.")
        except:
            print("Please enter a number.")
    return game.take_action(state, col, player)

# ------------------- AI Play -------------------
def AI_play(game, state, turn_count, depth=5):
    player = game.current_player(turn_count)
    print("AI is thinking...")
    col, _ = alpha_beta(game, state, depth, -math.inf, math.inf, True, player)
    print(f"AI chooses column {col + 1}")
    return game.take_action(state, col, player)

# ------------------- CLI Game Loop -------------------
def play_connect4_cli():
    print("=== Connect 4 CLI (Human vs AI) ===")
    game = Connect4()
    state = copy.deepcopy(game.initial_grid)
    turn_count = 0

    while True:
        display_board(game, state)
        terminal, winner = game.terminal_test(state)
        if terminal:
            if winner is None:
                print("Game Over: Draw!")
            elif winner == "O": 
                print("Game Over: You Lose!") 
            else:
                print(f"Game Over: Winner is {winner}!")
            break

        player = game.current_player(turn_count)

        if player == "X":    # Human
            state = human_play(game, state, turn_count)
        else:                # AI
            state = AI_play(game, state, turn_count)

        turn_count += 1

if __name__ == "__main__":
    play_connect4_cli()
