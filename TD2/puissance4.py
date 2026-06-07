import time

# --- Constantes ---
ROWS = 6
COLS = 12
MAX_PIECE_COUNT = 42
EMPTY = 0
IA_PLAYER = 1
HUMAN_PLAYER = -1

# --- Fonctions Requises (Livrables) ---

def Terminal_Test(board):
    # Lignes
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return True
                
    # Colonnes
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return True
                
    # Diagonales montantes
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return True
                
    # Diagonales descendantes
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return True
                
    # Limite de pions (42) ou plateau plein
    piece_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] != EMPTY)
    if piece_count >= MAX_PIECE_COUNT:
        return True

    if all(board[0][c] != EMPTY for c in range(COLS)):
        return True

    return False

def IA_Decision(board):
    # Profondeur de 5 pour rester sous les 10 secondes de calcul
    max_depth = 5 
    
    best_col, score = alpha_beta_search(board, max_depth, float('-inf'), float('inf'), True)
    
    # Sécurité anti-crash
    if best_col is None:
        valid_cols = get_valid_locations(board)
        best_col = valid_cols[0] if valid_cols else 0
        
    return best_col

# --- Fonctions Utilitaires ---

def get_winner(board):
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return board[r][c]
                
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return board[r][c]
                
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return board[r][c]
                
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return board[r][c]
                
    return 0

def evaluate_window(window, piece):
    score = 0
    opp_piece = HUMAN_PLAYER if piece == IA_PLAYER else IA_PLAYER

    if window.count(piece) == 4:
        score += 100000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    # Malus fort si l'adversaire peut gagner
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80

    return score

def heuristic(board, piece):
    score = 0

    # Poids pour la colonne centrale
    center_col = COLS // 2
    center_array = [board[r][center_col] for r in range(ROWS)]
    score += center_array.count(piece) * 4

    # Horizon
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # Verti
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # Diagonales
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLS):
        if board[0][col] == EMPTY:
            valid_locations.append(col)
    return valid_locations

def get_next_open_row(board, col):
    # La ligne 5 est le bas du tableau
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def copy_board(board):
    return [row[:] for row in board]

# --- Minimax & Alpha-Beta ---

def alpha_beta_search(board, depth, alpha, beta, is_max):
    valid_locations = get_valid_locations(board)
    is_terminal = Terminal_Test(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            winner = get_winner(board)
            if winner == IA_PLAYER:
                return (None, 10000000000 + depth) # Bonus victoire rapide
            elif winner == HUMAN_PLAYER:
                return (None, -10000000000 - depth)
            else:
                return (None, 0)
        else:
            return (None, heuristic(board, IA_PLAYER))
            
    # Tri des coups pour optimiser l'élagage (on teste le milieu d'abord)
    valid_locations.sort(key=lambda x: abs(x - COLS//2))

    if is_max:
        value = float('-inf')
        best_col = valid_locations[0]
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy_board(board)
            drop_piece(b_copy, row, col, IA_PLAYER)
            
            new_score = alpha_beta_search(b_copy, depth-1, alpha, beta, False)[1]
            
            if new_score > value:
                value = new_score
                best_col = col
                
            alpha = max(alpha, value)
            if alpha >= beta:
                break 
                
        return best_col, value
        
    else:
        value = float('inf')
        best_col = valid_locations[0]
        
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = copy_board(board)
            drop_piece(b_copy, row, col, HUMAN_PLAYER)
            
            new_score = alpha_beta_search(b_copy, depth-1, alpha, beta, True)[1]
            
            if new_score < value:
                value = new_score
                best_col = col
                
            beta = min(beta, value)
            if alpha >= beta:
                break 
                
        return best_col, value

# --- Interface et Jeu ---

def create_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board):
    print("")
    for r in range(ROWS):
        row_str = "|"
        for c in range(COLS):
            if board[r][c] == IA_PLAYER:
                row_str += "X|"
            elif board[r][c] == HUMAN_PLAYER:
                row_str += "O|"
            else:
                row_str += " |"
        print(row_str)
        
    print("-" * (COLS * 2 + 1))
    # Affichage exact demandé par le PDF (0 à 9 puis 0, 1)
    header = "|" + "|".join(str(c % 10) for c in range(COLS)) + "|"
    print(header)
    print("")

def main_loop():
    print("========================================")
    print("      PUISSANCE 4 (12x6) - IA vs P1     ")
    print("========================================")
    print("IA : X  |  Joueur Humain : O")
    
    board = create_board()
    
    turn_choice = ""
    while turn_choice not in ["1", "2"]:
        turn_choice = input("Qui commence ? (1 pour Joueur, 2 pour IA) : ")
    
    turn = 0 if turn_choice == "1" else 1
    game_over = False
    
    print_board(board)
    
    while not game_over:
        if turn == 0:
            col = -1
            valid_cols = get_valid_locations(board)
            while col not in valid_cols:
                try:
                    col = int(input(f"Votre tour (0-11) : "))
                    if col not in valid_cols:
                        print("Colonne invalide. Réessayez.")
                except ValueError:
                    print("Entrez un nombre.")
            
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, HUMAN_PLAYER)

        else:
            print("L'IA réfléchit...")
            start_time = time.time()
            
            col = IA_Decision(board)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, IA_PLAYER)
            
            end_time = time.time()
            print(f"> L'IA a joué en colonne {col} ({end_time - start_time:.2f}s)")

        print_board(board)
        
        if Terminal_Test(board):
            game_over = True
            winner = get_winner(board)
            if winner == IA_PLAYER:
                print("L'IA GAGNE !")
            elif winner == HUMAN_PLAYER:
                print("VOUS AVEZ GAGNÉ !")
            else:
                print("MATCH NUL ! (Limite atteinte ou plateau plein)")
                
        turn += 1
        turn = turn % 2

if __name__ == "__main__":
    main_loop()