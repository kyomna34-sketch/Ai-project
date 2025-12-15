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
        self.initial_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]  # 0 = empty, 1 = X, 2 = O

    # ------------------ Display Board ------------------
    def display(self, state):
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
        for c in range(self.cols):
            print(c + 1, end=" ")
        print("\n")

    # ------------------ Take Action ------------------
    def take_action(self, state, col, player):
        new_state = [row[:] for row in state]
        player_val = 1 if player == "X" else 2
        
        for r in reversed(range(self.rows)):
            if new_state[r][col] == 0:
                new_state[r][col] = player_val
                return new_state
        return new_state

    # ------------------ Current Player ------------------
    @staticmethod
    def current_player(turn_count):
        return "X" if turn_count % 2 == 0 else "O"

    # ------------------ Available Actions ------------------
    def available_actions(self, state):
        actions =[]
        for col in range(self.cols):
            if state[0][col]== 0:
                actions.append(col)
        return actions
    
    # ------------------ Get Winner ------------------ (UPDATED)
    # الآن تُرجع tuple (الفائز, قائمة بإحداثيات القطع الفائزة)
    def get_winner(self, state):
        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                line = [state[r][c+i] for i in range(4)]
                if line[0] != 0 and all(x == line[0] for x in line):
                    winner = "X" if line[0] == 1 else "O"
                    line_coords = [(r, c+i) for i in range(4)]
                    return winner, line_coords
        # Vertical
        for r in range(self.rows - 3):
            for c in range(self.cols):
                line = [state[r+i][c] for i in range(4)]
                if line[0] != 0 and all(x == line[0] for x in line):
                    winner = "X" if line[0] == 1 else "O"
                    line_coords = [(r+i, c) for i in range(4)]
                    return winner, line_coords
        # Diagonal \
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                line = [state[r+i][c+i] for i in range(4)]
                if line[0] != 0 and all(x == line[0] for x in line):
                    winner = "X" if line[0] == 1 else "O"
                    line_coords = [(r+i, c+i) for i in range(4)]
                    return winner, line_coords
        # Diagonal /
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                line = [state[r-i][c+i] for i in range(4)]
                if line[0] != 0 and all(x == line[0] for x in line):
                    winner = "X" if line[0] == 1 else "O"
                    line_coords = [(r-i, c+i) for i in range(4)]
                    return winner, line_coords
        return None, [] # لا يوجد فائز، قائمة إحداثيات فارغة

    # ------------------ Terminal Test ------------------ (UPDATED)
    def terminal_test(self, state):
        winner, _ = self.get_winner(state) # نستخدم فقط الفائز من الدالة المحدثة
        if winner is not None:
            return True, winner
        elif all(state[0][c] != 0 for c in range(self.cols)):
            return True, None
        else:
            return False, None

    # ------------------ Evaluate Board for AI ------------------
    def evaluate(self, state, player):
        opponent = "O" if player == "X" else "X"
        score = 0
        # ... (بقية كود evaluate كما هو)
        def score_group(group):
            s = 0
            p_val = 1 if player == "X" else 2
            o_val = 1 if opponent == "X" else 2
            
            # Winning condition check
            if group.count(p_val) == 4:
                s += 100000 
            elif group.count(p_val) == 3 and group.count(0) == 1:
                s += 50 
            elif group.count(p_val) == 2 and group.count(0) == 2:
                s += 10
                
            # Blocking/Opponent threat check
            if group.count(o_val) == 3 and group.count(0) == 1:
                s -= 70 
            elif group.count(o_val) == 2 and group.count(0) == 2:
                s -= 5
            return s

        # Center column preference (usually the most strategic)
        center_col = self.cols // 2
        for r in range(self.rows):
            if state[r][center_col] == (1 if player == "X" else 2):
                score += 5
            elif state[r][center_col] == (1 if opponent == "X" else 2):
                score -= 4

        # Evaluate all 4-in-a-row segments
        # Horizontal
        for r in range(self.rows):
            for c in range(self.cols - 3):
                score += score_group([state[r][c+i] for i in range(4)])
        # Vertical
        for r in range(self.rows - 3):
            for c in range(self.cols):
                score += score_group([state[r+i][c] for i in range(4)])
        # Diagonal / (top-left to bottom-right)
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                score += score_group([state[r+i][c+i] for i in range(4)])
        # Diagonal \ (bottom-left to top-right)
        for r in range(3, self.rows):
            for c in range(self.cols - 3):
                score += score_group([state[r-i][c+i] for i in range(4)])

        return score
