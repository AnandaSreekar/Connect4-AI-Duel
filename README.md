## 🧠 How It Works

The application operates on a client-server architecture. The entire game flow is handled by passing messages between the frontend and the backend.

### 🖥️ 1. Frontend (React)

* **Role:** The frontend is the user's "window" into the game.
* **Function:** It displays the 7x6 Connect Four board. When the user clicks on a column, it sends an API request to the backend with the chosen move (e.g., "Player chose column 3").
* **Update:** It waits for a response from the backend. When it receives the new game state, it re-renders the board to show both the player's move and the AI's counter-move.

### ⚙️ 2. Backend (Python - `server.py`)

* **Role:** The backend is the "referee" and the "matchmaker."
* **Function:**
    1.  It listens for API requests from the React frontend.
    2.  When it receives the player's move, it passes this move to the `game.py` module.
    3.  It then asks the AI in `game.py` to calculate its own move (based on the selected difficulty).
    4.  It packages the complete new board state and any win/loss messages into a JSON response and sends it back to the frontend.

### 🤖 3. AI Engine (`game.py`)

* **Role:** This is the "brain" of the entire operation.
* **Function:** This Python file contains all the core logic:
    * **Board Representation:** A data structure (like a 2D array) that holds the state of the game.
    * **Game Rules:** Functions to check if a move is valid, check for a 4-in-a-row (horizontal, vertical, diagonal), and check for a draw.
    * **The AI (Minimax):** The algorithm that "thinks" several moves ahead. It explores thousands of possible game futures and chooses the move that gives it the highest chance of winning.

---
