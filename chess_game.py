from piece_classes import King, Queen, Rook, Knight, Bishop, Pawn
import tkinter as tk
PIECES = {
    'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
    'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟',
}

move_hints = []
pawn_moved = set()

CLASS_MAP = {'R': Rook, 'N': Knight, 'B': Bishop, 'Q': Queen, 'K': King}


def start_board():
    order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']

    board = [[None] * 8 for _ in range(8)]

    for i in range(8):
        board[7][i] = CLASS_MAP[order[i]]('w')
        board[6][i] = Pawn('w')
        board[1][i] = Pawn('b')
        board[0][i] = CLASS_MAP[order[i]]('b')

    return board

starting_board = start_board()

square_size = 100
white_square_col = '#F0D9B5'
black_square_col  = '#B58863'
selected_square = '#7FC97F'


selected = None  # tracks which square is selected
current_player = 'w'
en_passant_flag = None

def draw():

    CODES = {Pawn: 'P', Rook: 'R', Knight: 'N', Bishop: 'B', Queen: 'Q', King: 'K'}

    canvas.delete('all')
    for row in range(8):
        for col in range(8):
            x1, y1 = col*square_size, row*square_size

            if selected == (row, col):
                color = selected_square
            else:
                color = white_square_col if (row+col) % 2 == 0 else black_square_col

            canvas.create_rectangle(x1, y1, x1+square_size, y1+square_size, fill=color, outline='')

            piece = starting_board[row][col]

            if piece:
                key = piece.color + CODES[type(piece)]
                canvas.create_text(x1+square_size//2, y1+square_size//2, text=PIECES[key],
                                   font=('Segoe UI Symbol', 74))

    for (r, c) in move_hints:
        x, y = c*square_size + square_size//2, r*square_size + square_size//2
        canvas.create_oval(x-10, y-10, x+10, y+10, fill='#6F3096')


def is_in_check(color, board):
    #find position of king in the board
    king_pos = None
    for row_num in range(8):
        for col_num in range(8):
            piece = board[row_num][col_num]
            #Very important to remember --> Use __class__.__name__ to identify the King
            #other way to do it is with the command:
            #isinstance(piece, King)
            if piece.__class__.__name__ == 'King' and piece.color == color:
                king_pos = (row_num, col_num)
                break

    if not king_pos:
        return False

    #can enemy piece reach my kings position?
    enemy_color = 'b' if color == 'w' else 'w'
    for row_num in range(8):
        for col_num in range(8):
            piece = board[row_num][col_num]
            if piece and piece.color == enemy_color:
                #call for the attack squares to get back the list of the squares that are attacked by each
                #enemy piece on the board. If they are then return True in order to remove this move from
                #the list of eligible ones
                if king_pos in piece.get_attack_squares(row_num, col_num, board):
                    return True
    return False


def show_checkmate_screen(message):
    top = tk.Toplevel(root)
    top.title("Game Over")
    top.grab_set()

    tk.Label(top, text=message, font=('Arial', 20), padx=20, pady=20).pack()
    tk.Button(top, text="Close", command=top.destroy, font=('Arial', 14)).pack(pady=10)


def check_game_over():
    """Check if current player is in checkmate or stalemate"""
    has_valid_move = False

    for row in range(8):
        for col in range(8):
            piece = starting_board[row][col]
            if piece and piece.color == current_player:
                raw_moves = piece.get_moves(row, col, starting_board)
                for move in raw_moves:
                    tr, tc = move
                    saved = starting_board[tr][tc]
                    starting_board[tr][tc] = piece
                    starting_board[row][col] = None

                    if not is_in_check(current_player, starting_board):
                        has_valid_move = True

                    starting_board[row][col] = piece
                    starting_board[tr][tc] = saved

                    if has_valid_move:
                        return
        if has_valid_move:
            return

    # No valid moves found
    if is_in_check(current_player, starting_board):
        show_checkmate_screen("Checkmate! " + ('Black' if current_player == 'w' else 'White') + " wins!")
    else:
        show_checkmate_screen("Stalemate! Game is a draw.")


def on_click(event):
    global selected, move_hints, current_player, en_passant_flag
    col = event.x // square_size
    row = event.y // square_size

    if selected is None:
        piece = starting_board[row][col]

        if piece and piece.color == current_player:
            selected = (row, col)

            raw_moves = piece.get_moves(row, col, starting_board)

            valid_moves = []
            for move in raw_moves:
                # filter moves to remove the ones that expose the king to danger

                tr, tc = move  #row and column to move the new piece in each potential move

                # --- START SIMULATION ---
                saved_piece = starting_board[tr][tc]  #keep the original piece of the square in this position
                starting_board[tr][tc] = piece  #move piece to new position
                starting_board[row][col] = None  #empty old square

                #The is_in_check(current_player, starting_board) takes the
                if not is_in_check(current_player, starting_board):
                    valid_moves.append(move)

                if piece.__class__.__name__ == 'Pawn' and en_passant_flag:
                    enemy_pawn_row, enemy_pawn_col = en_passant_flag[0:2]
                    player = en_passant_flag[2]
                    if (((row, tc) == (enemy_pawn_row, enemy_pawn_col + 1)
                         or (row, tc) == (enemy_pawn_row, enemy_pawn_col - 1))):

                        if player == 'w':
                            valid_moves.append((enemy_pawn_row - 1, enemy_pawn_col))
                        else:
                            valid_moves.append((enemy_pawn_row + 1, enemy_pawn_col))

                # --- UNDO SIMULATION ---
                starting_board[row][col] = piece
                starting_board[tr][tc] = saved_piece

            if piece.__class__.__name__ == 'King':
                if (row, col + 2) in valid_moves and (row, col + 1) not in valid_moves:
                    valid_moves.remove((row, col + 2))

                if (row, col - 2) in valid_moves and (row, col - 1) not in valid_moves:
                    valid_moves.remove((row, col - 2))

            move_hints = valid_moves

    else:
        if (row, col) in move_hints:
            current_player = 'b' if current_player=='w' else 'w'

            from_row, from_col = selected
            piece = starting_board[from_row][from_col]

            starting_board[row][col] = starting_board[from_row][from_col]
            starting_board[row][col].moved = True
            starting_board[from_row][from_col] = None

            if isinstance(piece, King) and abs(col - from_col) == 2:

                #kingside castling -> column after is greater than column before
                if col > from_col:
                    rook = starting_board[row][7]
                    starting_board[row][5] = rook #transfer the rook to the new square
                    starting_board[row][7] = None #make the previous square blank, now occupied by nobody
                    rook.moved = True

                #queenside castling -> column after is lower in value than column before
                else:
                    rook = starting_board[row][0]
                    starting_board[row][3] = rook #transfer the rook to the new square
                    starting_board[row][0] = None #make the previous square blank, now occupied by nobody
                    rook.moved = True

            if isinstance(piece, Pawn):
                piece.promotion(row, col, starting_board, draw)  # Pass 'draw' without ()

                if en_passant_flag:
                    enemy_pawn_row, enemy_pawn_col = en_passant_flag[0:2]
                    enemy_color = en_passant_flag[2]

                    if piece.color == enemy_color:
                        if abs(from_col - col) == 1:
                            starting_board[enemy_pawn_row][enemy_pawn_col] = None

                if abs(row - from_row) == 2:
                    en_passant_flag = (row, col, current_player)
                else:
                    en_passant_flag = None

            check_game_over()


        selected = None
        move_hints = []

    draw()


root = tk.Tk()
root.title('Chess Board')

canvas = tk.Canvas(root, width=square_size*8, height=square_size*8)
canvas.pack()
canvas.bind('<Button-1>', on_click)

draw()
root.mainloop()
