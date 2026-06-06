import math

# Constants for players
MAX_PLAYER = 'X'
MIN_PLAYER = 'O'
EMPTY = ' '

# State of the Tic-Tac-Toe game
class TicTacToeState:
    def __init__(self, board=None):
        if board is None:
            self.board = []
            for _ in range(9):
                self.board.append(EMPTY)
        else:
            self.board = board

    def display(self):
        print(" " + str(self.board[0]) + " | " + str(self.board[1]) + " | " + str(self.board[2]) + " ")
        print("---+---+---")
        print(" " + str(self.board[3]) + " | " + str(self.board[4]) + " | " + str(self.board[5]) + " ")
        print("---+---+---")
        print(" " + str(self.board[6]) + " | " + str(self.board[7]) + " | " + str(self.board[8]) + " ")
        print()

def actions(state):
    # Return empty cells
    possible_actions = []
    for i in range(len(state.board)):
        if state.board[i] == EMPTY:
            possible_actions.append(i)
    return possible_actions

def result(state, action, player):
    # Return new state after action
    new_board = []
    for cell in state.board:
        new_board.append(cell)
    new_board[action] = player
    return TicTacToeState(new_board)

def terminal_test(state):
    # Check if game is over
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Lines
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columns
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for condition in win_conditions:
        if state.board[condition[0]] != EMPTY and state.board[condition[0]] == state.board[condition[1]] and state.board[condition[1]] == state.board[condition[2]]:
            return True
    
    # Check draw
    is_full = True
    for cell in state.board:
        if cell == EMPTY:
            is_full = False
            
    if is_full:
        return True 
        
    return False

def utility(state):
    # Return score for a state
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for condition in win_conditions:
        if state.board[condition[0]] != EMPTY and state.board[condition[0]] == state.board[condition[1]] and state.board[condition[1]] == state.board[condition[2]]:
            if state.board[condition[0]] == MAX_PLAYER:
                return 1   # MAX wins
            else:
                return -1  # MIN wins
    return 0 # Draw

def heuristic(state):
    # Estimate state value
    if terminal_test(state):
        return utility(state)
    
    # Center control
    score = 0
    if state.board[4] == MAX_PLAYER:
        score = score + 0.5
    elif state.board[4] == MIN_PLAYER:
        score = score - 0.5
    return score

# --- Alpha-Beta Algorithm ---

def alpha_beta_search(state, max_depth=9):
    # Initialize search
    v, best_action = max_value(state, -math.inf, math.inf, 0, max_depth)
    return best_action

def max_value(state, alpha, beta, depth, max_depth):
    # MAX function
    if terminal_test(state):
        return utility(state), None
    if depth >= max_depth:
        return heuristic(state), None 
        
    v = -math.inf
    best_action = None
    
    for a in actions(state): 
        min_val, _ = min_value(result(state, a, MAX_PLAYER), alpha, beta, depth + 1, max_depth)
        
        if min_val > v:
            v = min_val
            best_action = a
            
        if v >= beta: 
            return v, best_action
            
        if v > alpha:
            alpha = v
            
    return v, best_action

def min_value(state, alpha, beta, depth, max_depth):
    # MIN function
    if terminal_test(state):
        return utility(state), None
    if depth >= max_depth:
        return heuristic(state), None
        
    v = math.inf
    best_action = None
    
    for a in actions(state): 
        max_val, _ = max_value(result(state, a, MIN_PLAYER), alpha, beta, depth + 1, max_depth)
        
        if max_val < v:
            v = max_val
            best_action = a
            
        if v <= alpha: 
            return v, best_action
            
        if v < beta:
            beta = v
            
    return v, best_action

# Main entry point
if __name__ == "__main__":
    game = TicTacToeState()
    game.display()
    
    best_move = alpha_beta_search(game, max_depth=5)
    print("Best move for " + str(MAX_PLAYER) + " is index: " + str(best_move))