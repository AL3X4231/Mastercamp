import math
import time
import copy

# CONSTANTS
ROWS = 6
COLS = 12
MAX_PIECES = 42

IA_PIECE = 1
PLAYER_PIECE = -1
EMPTY = 0

def Terminal_Test(board):
    for piece in [IA_PIECE, PLAYER_PIECE]:
        for c in range(COLS - 3):
            for r in range(ROWS):
                if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                    return True
        
        for c in range(COLS):
            for r in range(ROWS - 3):
                if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                    return True
        
        for c in range(COLS - 3):
            for r in range(ROWS - 3):
                if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                    return True
        
        for c in range(COLS - 3):
            for r in range(3, ROWS):
                if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                    return True

    pieces_played = 0
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != EMPTY:
                pieces_played += 1
                
    if pieces_played >= MAX_PIECES:
        return True

    board_full = True
    for c in range(COLS):
        if board[0][c] == EMPTY:
            board_full = False
            break
            
    if board_full:
        return True

    return False

def IA_Decision(board):
    depth = 4 
    col, score = minimax(board, depth, -math.inf, math.inf, True)
    
    if col is None:
        valid_cols = get_valid_locations(board)
        if len(valid_cols) > 0:
            col = valid_cols[0]
        else:
            col = 0
        
    return col

# MINIMAX ET HEURISTIC

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLS):
        if board[0][col] == EMPTY:
            valid_locations.append(col)
    return valid_locations

def drop_piece(board, col, piece):
    new_board = copy.deepcopy(board)
    for r in range(ROWS-1, -1, -1):
        if new_board[r][col] == EMPTY:
            new_board[r][col] = piece
            break
    return new_board

def evaluate_window(window, piece):
    score = 0
    if piece == IA_PIECE:
        opp_piece = PLAYER_PIECE
    else:
        opp_piece = IA_PIECE

    if window.count(piece) == 4:
        score += 10000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 50
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 10

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80

    return score

def heuristic_score(board, piece):
    score = 0
    
    center_count = 0
    for r in range(ROWS):
        if board[r][COLS//2] == piece:
            center_count += 1
    score += center_count * 20

    for r in range(ROWS):
        for c in range(COLS - 3):
            window = []
            for i in range(4):
                window.append(board[r][c+i])
            score += evaluate_window(window, piece)

    for c in range(COLS):
        for r in range(ROWS - 3):
            window = []
            for i in range(4):
                window.append(board[r+i][c])
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = []
            for i in range(4):
                window.append(board[r+i][c+i])
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = []
            for i in range(4):
                window.append(board[r+3-i][c+i])
            score += evaluate_window(window, piece)

    return score

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = Terminal_Test(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if heuristic_score(board, IA_PIECE) > 5000:
                return (None, 100000000000000)
            elif heuristic_score(board, PLAYER_PIECE) > 5000:
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, heuristic_score(board, IA_PIECE))
            
    if maximizingPlayer:
        value = -math.inf
        middle_index = len(valid_locations) // 2
        best_col = valid_locations[middle_index] 
        
        for col in valid_locations:
            b_copy = drop_piece(board, col, IA_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
        
    else:
        value = math.inf
        middle_index = len(valid_locations) // 2
        best_col = valid_locations[middle_index]
        
        for col in valid_locations:
            b_copy = drop_piece(board, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


# LOOP

def print_board(board):
    print("\n")
    for r in range(ROWS):
        row_str = "|"
        for c in range(COLS):
            if board[r][c] == IA_PIECE:
                row_str += " \033[91mX\033[0m |" 
            elif board[r][c] == PLAYER_PIECE:
                row_str += " \033[94mO\033[0m |" 
            else:
                row_str += "   |"
        print(row_str)
        
    dash_str = ""
    for _ in range(COLS * 4 + 1):
        dash_str += "-"
    print(dash_str)
    
    bottom_str = "|"
    for i in range(COLS):
        if i < 10:
            bottom_str += " " + str(i) + " |"
        else:
            bottom_str += " " + str(i) + "|"
    print(bottom_str)
    print("\n")

def create_board():
    board = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(EMPTY)
        board.append(row)
    return board

def play_game():
    board = create_board()
    print("--- PUISSANCE 4 (12x6) ---")
    print("Vous jouez avec les 'O', l'IA joue avec les 'X'.")
    
    first = input("Qui commence ? Tapez '1' pour vous, '2' pour l'IA : ")
    if first == '1':
        turn = PLAYER_PIECE
    else:
        turn = IA_PIECE
    
    print_board(board)
    
    while not Terminal_Test(board):
        if turn == PLAYER_PIECE:
            valid = False
            while not valid:
                try:
                    col_str = input("Votre tour (0-11) : ")
                    col = int(col_str)
                    if col >= 0 and col <= 11 and board[0][col] == EMPTY:
                        valid = True
                        board = drop_piece(board, col, PLAYER_PIECE)
                    else:
                        print("Colonne invalide ou pleine.")
                except ValueError:
                    print("Veuillez entrer un chiffre.")
            turn = IA_PIECE
            
        else:
            print("L'IA réfléchit...")
            start_time = time.time()
            col = IA_Decision(board)
            end_time = time.time()
            
            diff_time = end_time - start_time
            print("L'IA a joué dans la colonne " + str(col) + " (Temps de réflexion : " + str(round(diff_time, 2)) + "s)")
            board = drop_piece(board, col, IA_PIECE)
            turn = PLAYER_PIECE
            
        print_board(board)
        
    pieces_played = 0
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != EMPTY:
                pieces_played += 1
                
    if heuristic_score(board, IA_PIECE) > 5000:
        print("L'IA A GAGNÉ")
    elif heuristic_score(board, PLAYER_PIECE) > 5000:
        print("VOUS AVEZ GAGNÉ")
    elif pieces_played >= MAX_PIECES:
        print("MATCH NUL (Limite des " + str(MAX_PIECES) + " pièces atteinte)")
    else:
        print("MATCH NUL (Grille pleine)")

if __name__ == "__main__":
    play_game()