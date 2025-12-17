import math
import random
from connect4 import Connect4


def alpha_beta(game, state, depth, alpha, beta, maximizing_player, player):
    """
    Alpha-Beta Pruning algorithm for Connect 4.
    Returns: (best_move_column, score)
    """
    terminal, winner = game.terminal_test(state)
    
    # Terminal node or depth limit reached
    if depth == 0 or terminal:
        if terminal:
            if winner == player:
                return None, 1000000 + depth  # Prefer faster wins
            elif winner is None:
                return None, 0  # Draw
            else:
                return None, -1000000 - depth  # Prefer slower losses
        else:
            # Non-terminal node, use heuristic evaluation
            return None, game.evaluate(state, player)
    
    actions = game.available_actions(state)
    
    # Move ordering: try center columns first (better for pruning)
    actions.sort(key=lambda col: abs(col - game.cols // 2))
    
    if maximizing_player:
        value = -math.inf
        best_move = random.choice(actions) if actions else None
        
        for col in actions:
            child = game.take_action(state, col, player)
            _, score = alpha_beta(game, child, depth - 1, alpha, beta, False, player)
            
            if score > value:
                value = score
                best_move = col
            
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff
        
        return best_move, value
    else:
        value = math.inf
        opponent = "O" if player == "X" else "X"
        best_move = random.choice(actions) if actions else None
        
        for col in actions:
            child = game.take_action(state, col, opponent)
            _, score = alpha_beta(game, child, depth - 1, alpha, beta, True, player)
            
            if score < value:
                value = score
                best_move = col
            
            beta = min(beta, value)
            if alpha >= beta:
                break  # Alpha cutoff
        
        return best_move, value


def get_ai_move(game, state, depth, player="O"):
    """
    Wrapper function to get AI move with Alpha-Beta pruning.
    """
    move, _ = alpha_beta(game, state, depth, -math.inf, math.inf, True, player)
    return move