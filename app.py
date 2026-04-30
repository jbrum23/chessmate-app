import streamlit as st
import chess
import chess.svg
import chess.engine
import base64
import time

# -----------------------------------------------
# PAGE CONFIG
# -----------------------------------------------
st.set_page_config(page_title="ChessMate", page_icon="♟️", layout="centered")

# -----------------------------------------------
# SESSION STATE SETUP
# -----------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "board" not in st.session_state:
    st.session_state.board = None
if "player_name" not in st.session_state:
    st.session_state.player_name = ""
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"
if "player_color" not in st.session_state:
    st.session_state.player_color = "White"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "last_move" not in st.session_state:
    st.session_state.last_move = None
if "hint" not in st.session_state:
    st.session_state.hint = ""

# -----------------------------------------------
# DIFFICULTY SETTINGS
# -----------------------------------------------
DIFFICULTY_SETTINGS = {
    "Easy":   {"skill_level": 2,  "depth": 4},
    "Medium": {"skill_level": 10, "depth": 10},
    "Hard":   {"skill_level": 20, "depth": 15},
}

# -----------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------

def get_engine():
    paths = [
    "stockfish",
    "/usr/local/bin/stockfish",
    "/opt/homebrew/bin/stockfish",
    "/usr/bin/stockfish",
    "/usr/games/stockfish",
]
    for path in paths:
        try:
            return chess.engine.SimpleEngine.popen_uci(path)
        except Exception:
            continue
    return None

def render_board(board, flipped, last_move):
    svg = chess.svg.board(
        board,
        flipped=flipped,
        size=450,
        lastmove=last_move,
    )
    b64 = base64.b64encode(svg.encode()).decode()
    return f'<div style="text-align:center;"><img src="data:image/svg+xml;base64,{b64}" style="width:100%;max-width:460px;"/></div>'

def get_captured_pieces(board):
    # Start with full set of pieces
    full = {
        chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2,
        chess.ROOK: 2, chess.QUEEN: 1
    }
    white_captured = []
    black_captured = []

    for piece_type, count in full.items():
        # Count how many are still on the board
        white_on_board = len(board.pieces(piece_type, chess.WHITE))
        black_on_board = len(board.pieces(piece_type, chess.BLACK))

        # Captured = started with - still on board
        white_lost = count - white_on_board
        black_lost = count - black_on_board

        symbol = chess.Piece(piece_type, chess.WHITE).unicode_symbol()
        black_captured.extend([symbol] * white_lost)

        symbol = chess.Piece(piece_type, chess.BLACK).unicode_symbol()
        white_captured.extend([symbol] * black_lost)

    return white_captured, black_captured

def make_ai_move(board, difficulty):
    engine = get_engine()
    if engine is None:
        return None, "Stockfish not found. Please install it to play against the AI."
    settings = DIFFICULTY_SETTINGS[difficulty]
    try:
        engine.configure({"Skill Level": settings["skill_level"]})
        result = engine.play(board, chess.engine.Limit(depth=settings["depth"]))
        engine.quit()
        return result.move, None
    except Exception as e:
        try:
            engine.quit()
        except Exception:
            pass
        return None, str(e)

def get_hint(board, difficulty):
    engine = get_engine()
    if engine is None:
        return "Stockfish not found. Install it to use hints."
    settings = DIFFICULTY_SETTINGS[difficulty]
    try:
        engine.configure({"Skill Level": settings["skill_level"]})
        result = engine.play(board, chess.engine.Limit(depth=settings["depth"]))
        engine.quit()
        return f"Best move: {result.move.uci()}"
    except Exception as e:
        try:
            engine.quit()
        except Exception:
            pass
        return str(e)

# -----------------------------------------------
# HOME PAGE
# -----------------------------------------------
def home_page():
    st.title("♟️ ChessMate")
    st.write("Play chess against an AI opponent. Set up your game below and click Play when you're ready.")

    st.divider()

    # Widget 1 - Player name
    st.subheader("Player Setup")
    player_name = st.text_input("Enter your name:")

    # Widget 2 - Difficulty
    difficulty = st.radio(
        "Select difficulty:",
        ["Easy", "Medium", "Hard"],
        index=1,
        horizontal=True,
    )

    if difficulty == "Easy":
        st.success("Easy — great for beginners learning the game.")
    elif difficulty == "Medium":
        st.info("Medium — a solid challenge that will test your skills.")
    elif difficulty == "Hard":
        st.error("Hard — extremely difficult. Good luck.")

    # Widget 3 - Color
    st.write("")
    color = st.radio(
        "Play as:",
        ["♔  White", "♚  Black"],
        horizontal=True,
    )

    st.divider()

    # Play button
    if st.button("▶  Play", use_container_width=True):
        if not player_name.strip():
            st.error("Please enter your name before playing.")
        else:
            st.session_state.player_name  = player_name.strip()
            st.session_state.difficulty   = difficulty
            st.session_state.player_color = "White" if "White" in color else "Black"
            st.session_state.board        = chess.Board()
            st.session_state.game_over    = False
            st.session_state.last_move    = None
            st.session_state.hint         = ""
            st.session_state.page         = "game"
            st.rerun()

# -----------------------------------------------
# GAME PAGE
# -----------------------------------------------
def game_page():
    board           = st.session_state.board
    difficulty      = st.session_state.difficulty
    player_color    = st.session_state.player_color
    player_is_white = player_color == "White"
    player_turn     = chess.WHITE if player_is_white else chess.BLACK
    flipped         = not player_is_white

    # Top bar
    col1, col2, col3 = st.columns([3, 4, 3])
    with col1:
        st.write(f"👤 **{st.session_state.player_name}**")
    with col2:
        icon = "♔" if player_is_white else "♚"
        st.write(f"{icon} {player_color} · {difficulty}")
    with col3:
        if st.button("← Menu"):
            st.session_state.page = "home"
            st.rerun()

    st.divider()

    # Board
    st.markdown(
        render_board(board, flipped=flipped, last_move=st.session_state.last_move),
        unsafe_allow_html=True,
    )

    st.write("")

    # Captured pieces display
    white_captured, black_captured = get_captured_pieces(board)
    cap1, cap2 = st.columns(2)
    with cap1:
        st.write("**You captured:**")
        st.write(" ".join(white_captured) if white_captured else "None yet")
    with cap2:
        st.write("**AI captured:**")
        st.write(" ".join(black_captured) if black_captured else "None yet")

    st.divider()

    # Game state messages
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        if winner == player_color:
            st.success(f"Checkmate! You win, {st.session_state.player_name}!")
        else:
            st.error("Checkmate! The AI wins. Better luck next time.")
        st.session_state.game_over = True

    elif board.is_stalemate():
        st.warning("Stalemate — it's a draw!")
        st.session_state.game_over = True

    elif board.is_check():
        st.warning("⚠️ Check!")

    # Player move input
    if not st.session_state.game_over and board.turn == player_turn:
        st.write("**Your move** — enter in UCI format (e.g. e2e4, g1f3)")
        move_col, btn_col = st.columns([4, 1])
        with move_col:
            move_input = st.text_input("Move:", label_visibility="collapsed", key="move_input")
        with btn_col:
            submit = st.button("Move ›", use_container_width=True)

        if submit and move_input.strip():
            try:
                move = chess.Move.from_uci(move_input.strip().lower())
                if move in board.legal_moves:
                    board.push(move)
                    st.session_state.last_move = move
                    st.session_state.hint = ""
                    st.rerun()
                else:
                    st.error("That is not a legal move. Try again.")
            except ValueError:
                st.error("Invalid format. Use UCI notation like e2e4 or g1f3.")

        # Hint button
        if st.button("💡 Get Hint"):
            st.session_state.hint = get_hint(board, difficulty)

        if st.session_state.hint:
            st.info(f"💡 {st.session_state.hint}")

    # AI move
    elif not st.session_state.game_over and board.turn != player_turn:
        with st.spinner("AI is thinking..."):
            time.sleep(3)
            ai_move, error = make_ai_move(board, difficulty)
        if error:
            st.error(error)
        elif ai_move:
            board.push(ai_move)
            st.session_state.last_move = ai_move
            st.rerun()

    # Play again buttons
    if st.session_state.game_over:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Play Again", use_container_width=True):
                st.session_state.board     = chess.Board()
                st.session_state.game_over = False
                st.session_state.last_move = None
                st.session_state.hint      = ""
                st.rerun()
        with c2:
            if st.button("← Main Menu", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()

# -----------------------------------------------
# PAGE ROUTER
# -----------------------------------------------
if st.session_state.page == "home":
    home_page()
else:
    game_page()