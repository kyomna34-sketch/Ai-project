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