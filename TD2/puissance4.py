import time

# --- Constantes ---
ROWS = 6
COLS = 12
MAX_PIECE_COUNT = 42
EMPTY = 0
IA_PLAYER = 1
HUMAN_PLAYER = -1

# Ordre d'exploration statique pour le Move Ordering (optimise drastiquement Alpha-Beta)
CENTER_ORDER = [5, 6, 4, 7, 3, 8, 2, 9, 1, 10, 0, 11]

# --- Fonctions Requises (Livrables) ---

def Terminal_Test(board):
    """Requis par le PDF : retourne True si le jeu est terminé, False sinon."""
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
                
    # Diagonales
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return True
        for r in range(3, ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return True
                
    # Limite de pions ou plateau plein
    piece_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] != EMPTY)
    if piece_count >= MAX_PIECE_COUNT:
        return True

    if all(board[0][c] != EMPTY for c in range(COLS)):
        return True

    return False

def IA_Decision(board):
    """Requis par le PDF : retourne la colonne (0-11) à jouer."""
    valid_cols = get_valid_locations(board)
    if not valid_cols:
        return 0

    # 1. Vérification Insta-Win (Profondeur 1)
    for col in valid_cols:
        row = get_next_open_row(board, col)
        b_copy = copy_board(board)
        drop_piece(b_copy, row, col, IA_PLAYER)
        if get_winner(b_copy) == IA_PLAYER:
            return col

    # 2. Vérification Insta-Block (Profondeur 1)
    for col in valid_cols:
        row = get_next_open_row(board, col)
        b_copy = copy_board(board)
        drop_piece(b_copy, row, col, HUMAN_PLAYER)
        if get_winner(b_copy) == HUMAN_PLAYER:
            return col

    # 3. Minimax Profond
    # Grâce aux optimisations, on peut tenter une profondeur de 5 ou 6 en gardant t < 10s
    max_depth = 5 
    
    best_col, score = alpha_beta_search(board, max_depth, float('-inf'), float('inf'), True)
    
    if best_col is None:
        return valid_cols[0]
        
    return best_col

# --- Fonctions Utilitaires & Heuristique ---

def get_winner(board):
    """Optimisation : retourne le gagnant sans refaire la vérification des pions pleins."""
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
        for r in range(3, ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return board[r][c]
                
    return 0

def evaluate_window(window, piece):
    """Évaluation ultra-agressive pour maximiser les points du tournoi."""
    score = 0
    opp_piece = -piece 
    
    p_count = window.count(piece)
    opp_count = window.count(opp_piece)
    e_count = 4 - p_count - opp_count

    if p_count == 4:
        score += 100000
    elif p_count == 3 and e_count == 1:
        score += 100  # Bonus agressif fort pour créer des menaces
    elif p_count == 2 and e_count == 2:
        score += 10
        
    # Défense absolue sur les menaces imminentes
    if opp_count == 3 and e_count == 1:
        score -= 150 

    return score

def heuristic(board, piece):
    score = 0

    # Poids lourd pour les deux colonnes centrales
    center_col_1 = COLS // 2
    center_col_2 = (COLS // 2) - 1
    
    score += sum(1 for r in range(ROWS) if board[r][center_col_1] == piece) * 6
    score += sum(1 for r in range(ROWS) if board[r][center_col_2] == piece) * 6

    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            score += evaluate_window(row_array[c:c+4], piece)

    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            score += evaluate_window(col_array[r:r+4], piece)

    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            score += evaluate_window([board[r+i][c+i] for i in range(4)], piece)
            score += evaluate_window([board[r+3-i][c+i] for i in range(4)], piece)

    return score

def get_valid_locations(board):
    # Move ordering statique instantané basé sur CENTER_ORDER
    return [c for c in CENTER_ORDER if board[0][c] == EMPTY]

def get_next_open_row(board, col):
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def copy_board(board):
    return [row[:] for row in board]

def is_full(board):
    piece_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] != EMPTY)
    return piece_count >= MAX_PIECE_COUNT or all(board[0][c] != EMPTY for c in range(COLS))

# --- Minimax avec Élagage Alpha-Beta ---

def alpha_beta_search(board, depth, alpha, beta, is_max):
    valid_locations = get_valid_locations(board)
    winner = get_winner(board)
    
    # Conditions terminales optimisées
    if depth == 0 or winner != 0 or is_full(board):
        if winner == IA_PLAYER:
            return (None, 10000000000 + depth) # Victoire rapide favorisée
        elif winner == HUMAN_PLAYER:
            return (None, -10000000000 - depth) # Repousser la défaite
        elif winner == 0 and (depth == 0 and not is_full(board)):
            return (None, heuristic(board, IA_PLAYER))
        else:
            return (None, 0) # Nul

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

# --- Interface et Boucle de Jeu ---

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
            # Trie par ordre numérique pour un affichage plus propre à l'utilisateur
            valid_cols_sorted = sorted(valid_cols)
            
            while col not in valid_cols_sorted:
                try:
                    col = int(input(f"Votre tour (0-11) : "))
                    if col not in valid_cols_sorted:
                        print("Colonne invalide ou pleine. Réessayez.")
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