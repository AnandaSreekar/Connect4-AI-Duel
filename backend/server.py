import numpy as np
import math
import random
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- Initialize Flask App ---
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# --- AI LOGIC (Exactly as before) ---
ROW_COUNT = 6
COLUMN_COUNT = 7
PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))
# ... (all the helper functions: drop_piece, is_valid_location, get_next_open_row, etc.) ...
def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def check_win(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_terminal_node(board):
    return check_win(board, PLAYER_PIECE) or check_win(board, AI_PIECE) or len(get_valid_locations(board)) == 0

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
            if check_win(board, AI_PIECE):
                return (None, 10000000)
            elif check_win(board, PLAYER_PIECE):
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

# --- NEW: Function to get all scores ---
def get_all_ai_scores(board, depth):
    scores = {}
    valid_locations = get_valid_locations(board)

    for col in valid_locations:
        # For each valid move, calculate the score
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, AI_PIECE)
        # We call minimax for the *opponent's* turn (minimizing player)
        # This tells us the "worst-case" score after we make this move.
        scores[col] = minimax(temp_board, depth - 1, -math.inf, math.inf, False)[1]

    return scores

# --- AI "Find Best Move" Functions ---
def find_best_move(board, depth):
    # This now returns the best col AND the dictionary of all scores
    scores = get_all_ai_scores(board, depth)
    if not scores: # If no valid moves
        return 0, {}

    best_col = max(scores, key=scores.get)
    return best_col, scores

def find_best_move_easy(board):
    col = random.choice(get_valid_locations(board))
    return col, {col: 0} # Return a simple score dict

def find_best_move_medium(board):
    valid_locations = get_valid_locations(board)
    center_col = COLUMN_COUNT // 2
    if center_col in valid_locations:
        return center_col, {center_col: 50}
    else:
        return find_best_move_easy(board)

# --- THE NEW API ENDPOINT ---
@app.route('/api/move', methods=['POST'])
def handle_move():
    try:
        data = request.json
        board = np.array(data['board'])
        difficulty = data['difficulty']

        # --- Run the correct AI logic ---
        if difficulty == 'Easy':
            col, scores = find_best_move_easy(board)
        elif difficulty == 'Medium':
            col, scores = find_best_move_medium(board)
        else: # Hard
            # --- THIS IS THE SPEED FIX ---
            # Changed from 4 to 3. This will be MUCH faster.
            col, scores = find_best_move(board, 3) # Depth 3
            # --- END OF SPEED FIX ---

        # --- NEW: Return the best column AND all the scores ---
        # Convert numpy types to standard int/float for JSON
        serializable_scores = {int(k): float(v) for k, v in scores.items()}
        return jsonify({'column': int(col), 'scores': serializable_scores})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# --- Run the Server ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
    