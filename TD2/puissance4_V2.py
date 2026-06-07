import math
import time

# --- Constantes du jeu ---
ROWS = 6
COLS = 12
MAX_PIECE_COUNT = 42
EMPTY = 0
IA_PLAYER = 1
HUMAN_PLAYER = -1

# --- Fonctions Requises (Combat d'IA) ---

def Terminal_Test(board):
    """
    Vérifie si l'état actuel du plateau est terminal.
    Retourne True si un joueur a gagné ou si la limite de pions/plateau plein est atteinte.
    """
    # 1. Vérification des lignes horizontales
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r][c+1] == board[r][c+2] == board[r][c+3]:
                return True
                
    # 2. Vérification des colonnes verticales
    for c in range(COLS):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c] == board[r+2][c] == board[r+3][c]:
                return True
                
    # 3. Vérification des diagonales (pente positive)
    for c in range(COLS - 3):
        for r in range(ROWS - 3):
            if board[r][c] != EMPTY and board[r][c] == board[r+1][c+1] == board[r+2][c+2] == board[r+3][c+3]:
                return True
                
    # 4. Vérification des diagonales (pente négative)
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if board[r][c] != EMPTY and board[r][c] == board[r-1][c+1] == board[r-2][c+2] == board[r-3][c+3]:
                return True
                
    # 5. Vérification du nombre limite de pièces jouées (42 max) ou plateau plein
    piece_count = sum(1 for r in range(ROWS) for c in range(COLS) if board[r][c] != EMPTY)
    if piece_count >= MAX_PIECE_COUNT:
        return True

    # 6. Vérification si plus aucune colonne n'est jouable (haut de la grille plein)
    if all(board[0][c] != EMPTY for c in range(COLS)):
        return True

    return False

def IA_Decision(board):
    """
    Prend en paramètre une matrice 6x12 et retourne l'action à jouer (numéro de colonne).
    IA = 1, Adversaire = -1.
    """
    # Profondeur fixée à 5 pour garantir une réponse < 10 secondes en Python pur.
    # Cette profondeur permet d'anticiper suffisamment sans exploser le temps de calcul.
    max_depth = 5 
    
    # On lance l'algorithme Minimax pour le joueur IA (Maximizing = True)
    best_col, minimax_score = alpha_beta_search(board, max_depth, -math.inf, math.inf, True)
    
    # Sécurité : si aucun coup n'est retourné (ex: situation de blocage rare), jouer la première dispo
    if best_col is None:
        valid_cols = get_valid_locations(board)
        best_col = valid_cols[0] if valid_cols else 0
        
    return best_col

# --- Fonctions Utilitaires & Heuristique ---

def get_winner(board):
    """
    Identique à Terminal_Test mais retourne l'ID du joueur gagnant (1 ou -1), ou 0 si match nul.
    """
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
    """
    Évalue l'intérêt d'une fenêtre de 4 cases pour un joueur donné.
    """
    score = 0
    opp_piece = HUMAN_PLAYER if piece == IA_PLAYER else IA_PLAYER

    if window.count(piece) == 4:
        score += 100000
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    # L'adversaire menace de faire un Puissance 4 : il faut absolument bloquer
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80

    return score

def heuristic(board, piece):
    """
    Fonction heuristique globale calculant le score d'un état du plateau.
    """
    score = 0

    # 1. Préférence pour les colonnes centrales (stratégiquement plus fortes)
    center_col = COLS // 2
    center_array = [board[r][center_col] for r in range(ROWS)]
    center_count = center_array.count(piece)
    score += center_count * 4

    # 2. Score Horizontal
    for r in range(ROWS):
        row_array = board[r]
        for c in range(COLS - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)

    # 3. Score Vertical
    for c in range(COLS):
        col_array = [board[r][c] for r in range(ROWS)]
        for r in range(ROWS - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    # 4. Score Diagonale (pente positive)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    # 5. Score Diagonale (pente négative)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def get_valid_locations(board):
    """Retourne la liste des colonnes non pleines."""
    valid_locations = []
    for col in range(COLS):
        if board[0][col] == EMPTY:
            valid_locations.append(col)
    return valid_locations

def get_next_open_row(board, col):
    """Trouve la ligne la plus basse disponible dans une colonne donnée."""
    # On parcourt du bas (ROWS-1) vers le haut (0)
    for r in range(ROWS-1, -1, -1):
        if board[r][col] == EMPTY:
            return r
    return None

def drop_piece(board, row, col, piece):
    """Place un pion sur le plateau."""
    board[row][col] = piece

def copy_board(board):
    """Création rapide d'une copie du plateau pour l'exploration de l'arbre."""
    return [row[:] for row in board]

# --- Algorithme Minimax avec Élagage Alpha-Beta ---

def alpha_beta_search(board, depth, alpha, beta, maximizingPlayer):
    """
    Implémentation de l'algorithme Minimax avec élagage Alpha-Beta.
    """
    valid_locations = get_valid_locations(board)
    is_terminal = Terminal_Test(board)
    
    # Condition d'arrêt : profondeur max atteinte ou état terminal
    if depth == 0 or is_terminal:
        if is_terminal:
            winner = get_winner(board)
            if winner == IA_PLAYER:
                # Bonus lié à la profondeur pour privilégier les victoires rapides
                return (None, 10000000000 + depth)
            elif winner == HUMAN_PLAYER:
                # Malus allégé par la profondeur pour repousser la défaite le plus tard possible
                return (None, -10000000000 - depth)
            else:
                return (None, 0) # Match Nul
        else:
            # On évalue toujours le plateau du point de vue de l'IA (1)
            return (None, heuristic(board, IA_PLAYER))
            
    # Optimisation cruciale : explorer les colonnes centrales en premier permet 
    # de déclencher l'élagage Alpha-Beta beaucoup plus tôt dans la boucle.
    valid_locations.sort(key=lambda x: abs(x - COLS//2))

    if maximizingPlayer:
        value = -math.inf
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
                break # Élagage Beta
                
        return best_col, value
        
    else: # Minimizing player
        value = math.inf
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
                break # Élagage Alpha
                
        return best_col, value

# --- Interface Utilisateur et Boucle de Jeu ---

def create_board():
    """Initialise un plateau de jeu vide (6x12)."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def print_board(board):
    """Affichage console propre et lisible."""
    print("\n")
    for r in range(ROWS):
        row_str = "|"
        for c in range(COLS):
            if board[r][c] == IA_PLAYER:
                row_str += " X |"
            elif board[r][c] == HUMAN_PLAYER:
                row_str += " O |"
            else:
                row_str += "   |"
        print(row_str)
        print("-" * (COLS * 4 + 1))
        
    # Affichage de la numérotation des colonnes
    header = "|"
    for c in range(COLS):
        # Formatage pour aligner correctement les nombres à deux chiffres
        header += f" {c:2d}|" 
    print(header)
    print("\n")

def main_loop():
    """Gère le mode de jeu Joueur contre IA."""
    print("========================================")
    print("      PUISSANCE 4 (12x6) - IA vs P1      ")
    print("========================================")
    print("IA : X  |  Joueur Humain : O")
    
    board = create_board()
    
    # Choix du premier joueur
    turn_choice = ""
    while turn_choice not in ["1", "2"]:
        turn_choice = input("Qui commence ? (1 pour Joueur, 2 pour IA) : ")
    
    # IA_PLAYER = 1, HUMAN_PLAYER = -1
    # On définit "turn" pour la boucle logique :
    # 0 = Joueur humain, 1 = IA
    turn = 0 if turn_choice == "1" else 1
    
    game_over = False
    print_board(board)
    
    while not game_over:
        
        # --- TOUR DU JOUEUR HUMAIN ---
        if turn == 0:
            col = -1
            valid_cols = get_valid_locations(board)
            while col not in valid_cols:
                try:
                    col = int(input(f"Votre tour (0-11) : "))
                    if col not in valid_cols:
                        print("Colonne invalide ou pleine. Réessayez.")
                except ValueError:
                    print("Veuillez entrer un nombre entier valide.")
            
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, HUMAN_PLAYER)
            print(f"> Vous avez joué dans la colonne {col}")

        # --- TOUR DE L'IA ---
        else:
            print("\nL'IA réfléchit (Minimax en cours)...")
            start_time = time.time()
            
            col = IA_Decision(board)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, IA_PLAYER)
            
            end_time = time.time()
            print(f"> L'IA a joué dans la colonne {col} (temps de calcul : {end_time - start_time:.2f}s)")

        print_board(board)
        
        # --- VÉRIFICATION DE FIN DE PARTIE ---
        if Terminal_Test(board):
            game_over = True
            winner = get_winner(board)
            if winner == IA_PLAYER:
                print("===============================")
                print("L'IA GAGNE LA PARTIE ! MAT ! ")
                print("===============================")
            elif winner == HUMAN_PLAYER:
                print("===============================")
                print("VOUS AVEZ GAGNÉ ! FÉLICITATIONS !")
                print("===============================")
            else:
                print("===============================")
                print("MATCH NUL ! Plus de coups possibles ou limite de pièces atteinte.")
                print("===============================")
                
        # Alternance des tours
        turn += 1
        turn = turn % 2

if __name__ == "__main__":
    main_loop()