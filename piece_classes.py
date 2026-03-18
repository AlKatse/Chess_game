import tkinter as tk

class Piece:
    def __init__(self, color):
        self.color = color

    def get_moves(self, row, col, board):
        return []


class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.moved = False

    def get_moves(self, row, col, board):
        moves = []
        direction = -1 if self.color == 'w' else 1

        if board[row + direction][col] is None:
            moves.append((row + direction, col))
            if not self.moved and board[row + direction*2][col] is None:
                moves.append((row + direction*2, col))

        if col - 1 >= 0 and board[row + direction][col - 1] is not None and board[row + direction][
            col - 1].color != self.color:
            moves.append((row + direction, col - 1))

        if col + 1 <= 7 and board[row + direction][col + 1] is not None and board[row + direction][
            col + 1].color != self.color:
            moves.append((row + direction, col + 1))

        return moves

    def get_attack_squares(self, row, col, board):
        moves = []
        direction = -1 if self.color == 'w' else 1

        if col - 1 >= 0:
            moves.append((row + direction, col - 1))

        if col + 1 <= 7:
            moves.append((row + direction, col + 1))

        return moves

    def promotion(self, row, col, board, draw_function):
        if (self.color == 'w' and row == 0) or (self.color == 'b' and row == 7):
            top = tk.Toplevel()
            top.title("Choose Piece")
            top.grab_set()  # Prevents clicking the board until chosen

            # This inner function handles the actual swap
            def select(piece_class):
                board[row][col] = piece_class(self.color)
                top.destroy()
                draw_function()  # Refresh the board to show the new piece

            # Define the choices
            choices = [('♕', Queen), ('♖', Rook), ('♗', Bishop), ('♘', Knight)]

            for icon, p_class in choices:
                tk.Button(top, text=icon, font=('Segoe UI Symbol', 40),
                          command=lambda c=p_class: select(c)).pack(side='left')

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.moved = False

    def get_moves(self, row, col, board):

        possible_directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]

        moves = []

        for dir in possible_directions:
            multiplier = 1

            while True:
                new_row = row + dir[0] * multiplier
                new_col = col + dir[1] * multiplier

                if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                    break

                if board[new_row][new_col] is None:
                    # continue until you hit the first piece
                    moves.append((new_row, new_col))
                    multiplier += 1
                elif board[new_row][new_col] is not None and board[new_row][new_col].color != self.color:
                    # capture the found piece once you hit it
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves

    def get_attack_squares(self, row, col, board):
        return self.get_moves(row, col, board)

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.moved = False

    def get_moves(self, row, col, board):

        possible_directions = [(-2,-1), (-2,1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

        moves = []

        for dir in possible_directions:

            new_row = row + dir[0]
            new_col = col + dir[1]

            if not (0 <= new_row <= 7 and 0 <= new_col <= 7):
                continue

            if board[new_row][new_col] is None:
                # continue until you hit the first piece
                moves.append((new_row, new_col))
            elif board[new_row][new_col] is not None and board[new_row][new_col].color != self.color:
                # capture the found piece once you hit it
                moves.append((new_row, new_col))


        return moves

    def get_attack_squares(self, row, col, board):
        return self.get_moves(row, col, board)

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.moved = False

    def get_moves(self, row, col, board):

        possible_directions = [(-1,-1),(-1,1), (1,-1),(1,1)]

        moves = []

        for dir in possible_directions:
            multiplier = 1

            while True:
                new_row = row + dir[0] * multiplier
                new_col = col + dir[1] * multiplier

                if not (0<=new_row<=7 and 0 <=new_col<=7):
                    break

                if board[new_row][new_col] is None:
                    #continue until you hit the first piece
                    moves.append((new_row, new_col))
                    multiplier += 1
                elif board[new_row][new_col] is not None and board[new_row][new_col].color != self.color:
                    #capture the found piece once you hit it
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves

    def get_attack_squares(self, row, col, board):
        return self.get_moves(row, col, board)

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.moved = False

    def get_moves(self, row, col, board):

        '''
        Possible directions here are manually inputed. We could instead do:
        for i in range(-1,2):
            for j in range(-1,2):
                possible_directions.append((i,j))
        '''

        possible_directions = [(-1,-1),(-1,0),(-1,1),(0,-1), (0,1), (1,-1), (1,0),(1,1)]

        moves = []

        for dir in possible_directions:

            new_row = row + dir[0]
            new_col = col + dir[1]

            if (0<=new_row<=7 and 0<=new_col<=7):
                if board[new_row][new_col] is None:
                    moves.append((new_row, new_col))

                elif board[new_row][new_col] is not None and board[new_row][new_col].color != self.color:
                    moves.append((new_row, new_col))
            else:
                continue

        #addition of castling
        #Kingside
        if not self.moved and board[row][col + 1] is None and board[row][col + 2] is None:

            rook = board[row][col + 3]
            if isinstance(rook, Rook) and rook.color == self.color and not rook.moved:
                moves.append((row, col + 2))

        #Queenside
        if (not self.moved and board[row][col - 1] is None
                and board[row][col - 2] is None
                and board[row][col -3] is None):

            rook = board[row][col - 4]
            if isinstance(rook, Rook) and rook.color == self.color and not rook.moved:
                moves.append((row, col - 2))
        return moves

    def get_attack_squares(self, row, col, board):
        return self.get_moves(row, col, board)

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.moved = False

    def get_moves(self, row, col, board, ignore_friendly=False):

        possible_directions = [(-1,-1),(-1,0),(-1,1),(0,-1), (0,1), (1,-1), (1,0),(1,1)]

        moves = []

        for dir in possible_directions:
            multiplier = 1

            while True:
                new_row = row + dir[0] * multiplier
                new_col = col + dir[1] * multiplier

                if not (0<=new_row<=7 and 0 <=new_col<=7):
                    break

                if board[new_row][new_col] is None:
                    #continue until you hit the first piece
                    moves.append((new_row, new_col))
                    multiplier += 1
                elif board[new_row][new_col] is not None and board[new_row][new_col].color != self.color:
                    #capture the found piece once you hit it
                    moves.append((new_row, new_col))
                    break
                else:
                    break

        return moves

    def get_attack_squares(self, row, col, board):
        return self.get_moves(row, col, board)
