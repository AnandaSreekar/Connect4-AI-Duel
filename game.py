import pygame
import sys
import numpy as np
import math
import random

# --- AI LOGIC (The "Brain") ---
# --- Constants for AI ---
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

# --- AI Board Logic Functions ---
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0 

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def check_win(board, piece):
    # Check horizontal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True, ((c, r), (c+3, r))
    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True, ((c, r), (c, r+3))
    # Check positive diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True, ((c, r), (c+3, r+3))
    # Check negative diagonal
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True, ((c, r), (c+3, r-3))
    return False, None # No win

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    win_p1, _ = check_win(board, PLAYER_PIECE)
    win_p2, _ = check_win(board, AI_PIECE)
    return win_p1 or win_p2 or len(get_valid_locations(board)) == 0

# --- AI "Brain" Functions (All difficulties return score dict) ---

# LEVEL: EASY
def find_best_move_easy(board):
    valid_locations = get_valid_locations(board)
    col = random.choice(valid_locations)
    return col, {col: 0} # Return a simple score dict for visualization

# LEVEL: MEDIUM (Heuristic)
def find_best_move_medium(board):
    valid_locations = get_valid_locations(board)
    center_col = COLUMN_COUNT // 2
    if center_col in valid_locations:
        return center_col, {center_col: 50}
    else:
        return find_best_move_easy(board)

# LEVEL: HARD (Minimax)
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4:
        score += 1000 
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 80
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+4]
            score += evaluate_window(window, piece)
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)
    return score

def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            win_ai, _ = check_win(board, AI_PIECE)
            win_player, _ = check_win(board, PLAYER_PIECE)
            if win_ai:
                return (None, 10000000)
            elif win_player:
                return (None, -10000000)
            else: # Draw
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def get_all_ai_scores(board, depth):
    scores = {}
    valid_locations = get_valid_locations(board)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, AI_PIECE)
        scores[col] = minimax(temp_board, depth - 1, -math.inf, math.inf, False)[1]
    return scores

def find_best_move(board, depth):
    scores = get_all_ai_scores(board, depth)
    if not scores:
        return 0, {} 
    best_col = max(scores, key=scores.get)
    return best_col, scores

# --- GAME UI (The "Body") ---
# --- Cyber UI COLORS ---
BACKGROUND_COLOR = (10, 20, 40)
BOARD_COLOR = (20, 40, 80)
EMPTY_SLOT_COLOR = (30, 60, 110)
PLAYER_1_COLOR = (255, 100, 100) # Red
PLAYER_2_COLOR = (255, 255, 100) # Yellow
WHITE = (255, 255, 255)
BUTTON_COLOR = (0, 150, 130)
BUTTON_HOVER_COLOR = (0, 200, 180)
WINNING_LINE_COLOR = (0, 255, 120)
AI_CHOICE_HIGHLIGHT = (0, 200, 180, 100)

# --- Constants for UI ---
SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)
AI_DEPTH_HARD = 4
AI_DEPTH_MEDIUM = 2
AI_DEPTH_EASY = 0 # Not used, but good to have

# --- UI Functions ---
def draw_board(board, screen, scores_to_show=None, ai_choice=None):
    screen.fill(BACKGROUND_COLOR)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BOARD_COLOR, (c * SQUARESIZE, (r + 1) * SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, EMPTY_SLOT_COLOR, (int(c * SQUARESIZE + SQUARESIZE / 2), int((r + 1) * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(screen, PLAYER_1_COLOR, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, PLAYER_2_COLOR, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    if scores_to_show:
        small_font = pygame.font.SysFont("monospace", 30)
        for col, score in scores_to_show.items():
            if col == ai_choice:
                s = pygame.Surface((SQUARESIZE, SQUARESIZE * ROW_COUNT))
                s.set_alpha(100) 
                s.fill(AI_CHOICE_HIGHLIGHT)
                screen.blit(s, (col * SQUARESIZE, SQUARESIZE))
            
            score_text = f"{score}"
            if score >= 1000000: score_text = "WIN!"
            if score <= -1000000: score_text = "LOSE!"
            
            text = small_font.render(score_text, 1, WHITE)
            text_rect = text.get_rect(center=(int(c * SQUARESIZE + SQUARESIZE / 2), int(SQUARESIZE / 2)))
            screen.blit(text, text_rect)

def draw_winning_line(screen, line_coords):
    if line_coords is None:
        return
    start_col, start_row = line_coords[0]
    end_col, end_row = line_coords[1]
    start_x = int(start_col * SQUARESIZE + SQUARESIZE / 2)
    start_y = height - int(start_row * SQUARESIZE + SQUARESIZE / 2)
    end_x = int(end_col * SQUARESIZE + SQUARESIZE / 2)
    end_y = height - int(end_row * SQUARESIZE + SQUARESIZE / 2)
    pygame.draw.line(screen, WINNING_LINE_COLOR, (start_x, start_y), (end_x, end_y), 15)

def draw_menu(screen, title, buttons):
    screen.fill(BACKGROUND_COLOR)
    title_font = pygame.font.SysFont("monospace", 50, bold=True)
    title_label = title_font.render(title, 1, WHITE)
    screen.blit(title_label, (width/2 - title_label.get_width()/2, height/2 - 200))

    mouse_pos = pygame.mouse.get_pos()
    for button_text, button_rect in buttons.items():
        color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        
        button_font = pygame.font.SysFont("monospace", 40)
        label = button_font.render(button_text, 1, WHITE)
        screen.blit(label, (button_rect.centerx - label.get_width()/2, button_rect.centery - label.get_height()/2))
    
    pygame.display.update()

# --- NEW: Game Loop Function ---
# This is now *just* for playing the game, not menus
def game_loop(screen, game_mode, ai_difficulty):
    board = create_board()
    game_over = False
    turn = 0 # Player 1 always starts (0)
    ai_scores = None
    ai_choice = None
    message = ""
    winning_line = None
    
    title_font = pygame.font.SysFont("monospace", 75)
    
    draw_board(board, screen)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- MOUSE HOVER ---
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, width, SQUARESIZE))
                if ai_scores and not (game_mode == 'PvA' and turn == 0):
                    draw_board(board, screen, ai_scores, ai_choice)
                
                posx = event.pos[0]
                # Show hover piece only for human players
                if (game_mode == 'PvA' and turn == 0) or game_mode == 'PvP':
                    color = PLAYER_1_COLOR if turn == 0 else PLAYER_2_COLOR
                    pygame.draw.circle(screen, color, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            # --- MOUSE CLICK (Human Player's Turn) ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, width, SQUARESIZE))
                col = int(event.pos[0] // SQUARESIZE)
                
                # --- Player vs. AI Mode ---
                if game_mode == 'PvA' and turn == 0:
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)
                        ai_scores = None # Clear old scores
                        
                        has_won, winning_line = check_win(board, PLAYER_PIECE)
                        if has_won:
                            message = "Player 1 Wins!!"
                            game_over = True
                        turn = 1
                
                # --- Player vs. Player Mode ---
                elif game_mode == 'PvP':
                    if is_valid_location(board, col):
                        if turn == 0: # Player 1's turn
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, PLAYER_PIECE)
                            has_won, winning_line = check_win(board, PLAYER_PIECE)
                            if has_won:
                                message = "Player 1 (Red) Wins!!"
                                game_over = True
                        else: # Player 2's turn
                            row = get_next_open_row(board, col)
                            drop_piece(board, row, col, AI_PIECE) # Use AI_PIECE for P2
                            has_won, winning_line = check_win(board, AI_PIECE)
                            if has_won:
                                message = "Player 2 (Yellow) Wins!!"
                                game_over = True
                        turn = (turn + 1) % 2 # Flip turn
                
                if not game_over and len(get_valid_locations(board)) == 0:
                    message = "It's a TIE!!"
                    game_over = True
                
                draw_board(board, screen)

        # --- AI's Turn (Handles both PvA and AvA) ---
        if not game_over:
            # --- AI 1's Turn (in AI vs AI mode) ---
            if game_mode == 'AvA' and turn == 0:
                col, ai_scores = find_best_move(board, AI_DEPTH_HARD) # Smart AI
                ai_choice = col
                draw_board(board, screen, ai_scores, ai_choice)
                pygame.time.wait(1000)
                
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    has_won, winning_line = check_win(board, PLAYER_PIECE)
                    if has_won:
                        message = "AI 1 (Red) Wins!!"
                        game_over = True
                    turn = 1
                    draw_board(board, screen)
            
            # --- AI 2's Turn (in PvA or AvA mode) ---
            elif (game_mode == 'PvA' and turn == 1) or (game_mode == 'AvA' and turn == 1):
                
                # --- This is where we use the chosen difficulty! ---
                if game_mode == 'PvA':
                    if ai_difficulty == 'Easy':
                        col, ai_scores = find_best_move_easy(board)
                    elif ai_difficulty == 'Medium':
                        col, ai_scores = find_best_move_medium(board)
                    else: # Hard
                        col, ai_scores = find_best_move(board, AI_DEPTH_HARD)
                else: # AI vs AI mode, make P2 slightly dumber
                    col, ai_scores = find_best_move(board, AI_DEPTH_MEDIUM)
                
                ai_choice = col
                draw_board(board, screen, ai_scores, ai_choice)
                pygame.time.wait(1000) # Pause to show the "thinking"

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, AI_PIECE)
                    has_won, winning_line = check_win(board, AI_PIECE)
                    if has_won:
                        message = "AI (Yellow) Wins!!"
                        game_over = True
                    turn = 0
                    draw_board(board, screen)

            if not game_over and len(get_valid_locations(board)) == 0:
                message = "It's a TIE!!"
                game_over = True

        # --- Game Over Screen ---
        if game_over:
            draw_winning_line(screen, winning_line)
            pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, width, SQUARESIZE))
            label = title_font.render(message, 1, WHITE)
            label_rect = label.get_rect(center=(width / 2, SQUARESIZE / 2))
            screen.blit(label, label_rect)
            pygame.display.update()
            
            pygame.time.wait(5000) # Wait 5 seconds
            return # Exit game_loop and return to main_app

# --- NEW: Main Application Controller ---
# This loop controls the "screens" of our application
def main_app():
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Connect-4 AI Duel")

    app_state = 'main_menu'
    game_mode = None
    ai_difficulty = None
    
    # --- Main Menu Button Rects ---
    pvp_rect = pygame.Rect(width/2 - 200, height/2 - 50, 400, 80)
    pva_rect = pygame.Rect(width/2 - 200, height/2 + 50, 400, 80)
    ava_rect = pygame.Rect(width/2 - 200, height/2 + 150, 400, 80)
    main_menu_buttons = {
        "Player vs. Player": pvp_rect,
        "Player vs. AI": pva_rect,
        "AI vs. AI": ava_rect
    }
    
    # --- Difficulty Menu Button Rects ---
    easy_rect = pygame.Rect(width/2 - 150, height/2 - 50, 300, 80)
    medium_rect = pygame.Rect(width/2 - 150, height/2 + 50, 300, 80)
    hard_rect = pygame.Rect(width/2 - 150, height/2 + 150, 300, 80)
    difficulty_menu_buttons = {
        "Easy": easy_rect,
        "Medium": medium_rect,
        "Hard": hard_rect
    }

    while True:
        if app_state == 'main_menu':
            draw_menu(screen, "Connect-4: AI Duel", main_menu_buttons)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pvp_rect.collidepoint(event.pos):
                        game_mode = 'PvP'
                        app_state = 'game_play'
                    elif pva_rect.collidepoint(event.pos):
                        game_mode = 'PvA'
                        app_state = 'difficulty_menu' # Go to difficulty select
                    elif ava_rect.collidepoint(event.pos):
                        game_mode = 'AvA'
                        app_state = 'game_play'
        
        elif app_state == 'difficulty_menu':
            draw_menu(screen, "Select AI Difficulty", difficulty_menu_buttons)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if easy_rect.collidepoint(event.pos):
                        ai_difficulty = 'Easy'
                        app_state = 'game_play'
                    elif medium_rect.collidepoint(event.pos):
                        ai_difficulty = 'Medium'
                        app_state = 'game_play'
                    elif hard_rect.collidepoint(event.pos):
                        ai_difficulty = 'Hard'
                        app_state = 'game_play'

        elif app_state == 'game_play':
            game_loop(screen, game_mode, ai_difficulty)
            app_state = 'main_menu' # After game ends, return to main menu

# --- Run the App ---
if __name__ == "__main__":
    main_app()