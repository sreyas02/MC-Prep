from abc import ABC, abstractmethod
from enum import Enum

class Color(Enum):
    WHITE = 1
    BLACK = 2

class Piece(ABC):
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col

    @abstractmethod
    def can_move(self, board, dest_row, dest_col):
        pass


class King(Piece):
    def can_move(self, board, dest_row, dest_col):
        row_diff = abs(dest_row - self.row)
        col_diff = abs(dest_col - self.col)
        return row_diff <= 1 and col_diff <= 1
    

class Queen(Piece):
    def can_move(self, board, dest_row, dest_col):
        row_diff = abs(dest_row - self.row)
        col_diff = abs(dest_col - self.col)
        return (row_diff == col_diff) or (self.row == dest_row or self.col == dest_col)
    

class Knight(Piece):
    def can_move(self, board, dest_row, dest_col):
        row_diff = abs(dest_row - self.row)
        col_diff = abs(dest_col - self.col)
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    

class Rook(Piece):
    def can_move(self, board, dest_row, dest_col):
        return self.row == dest_row or self.col == dest_col
    

class Bishop(Piece):
    def can_move(self, board, dest_row, dest_col):
        row_diff = abs(dest_row - self.row)
        col_diff = abs(dest_col - self.col)
        return row_diff == col_diff
    

class Pawn(Piece):
    def can_move(self, board, dest_row, dest_col):
        row_diff = dest_row - self.row
        col_diff = abs(dest_col - self.col)

        if self.color == Color.WHITE:
            return (row_diff == 1 and col_diff == 0) or \
                   (self.row == 1 and row_diff == 2 and col_diff == 0) or \
                   (row_diff == 1 and col_diff == 1 and board.get_piece(dest_row, dest_col) is not None)
        else:
            return (row_diff == -1 and col_diff == 0) or \
                   (self.row == 6 and row_diff == -2 and col_diff == 0) or \
                   (row_diff == -1 and col_diff == 1 and board.get_piece(dest_row, dest_col) is not None)

class Board:
    def __init__(self):
        self.board = [[None] * 8 for _ in range(8)]
        self._initialize_board()

    def _initialize_board(self):
        # Initialize white pieces
        self.board[0][0] = Rook(Color.WHITE, 0, 0)
        self.board[0][1] = Knight(Color.WHITE, 0, 1)
        self.board[0][2] = Bishop(Color.WHITE, 0, 2)
        self.board[0][3] = Queen(Color.WHITE, 0, 3)
        self.board[0][4] = King(Color.WHITE, 0, 4)
        self.board[0][5] = Bishop(Color.WHITE, 0, 5)
        self.board[0][6] = Knight(Color.WHITE, 0, 6)
        self.board[0][7] = Rook(Color.WHITE, 0, 7)
        for i in range(8):
            self.board[1][i] = Pawn(Color.WHITE, 1, i)

        # Initialize black pieces
        self.board[7][0] = Rook(Color.BLACK, 7, 0)
        self.board[7][1] = Knight(Color.BLACK, 7, 1)
        self.board[7][2] = Bishop(Color.BLACK, 7, 2)
        self.board[7][3] = Queen(Color.BLACK, 7, 3)
        self.board[7][4] = King(Color.BLACK, 7, 4)
        self.board[7][5] = Bishop(Color.BLACK, 7, 5)
        self.board[7][6] = Knight(Color.BLACK, 7, 6)
        self.board[7][7] = Rook(Color.BLACK, 7, 7)
        for i in range(8):
            self.board[6][i] = Pawn(Color.BLACK, 6, i)

    def get_piece(self, row, col):
        return self.board[row][col]

    def set_piece(self, row, col, piece):
        self.board[row][col] = piece

    def is_valid_move(self, piece, dest_row, dest_col):
        if piece is None or dest_row < 0 or dest_row > 7 or dest_col < 0 or dest_col > 7:
            return False
        dest_piece = self.board[dest_row][dest_col]
        return (dest_piece is None or dest_piece.color != piece.color) and \
               piece.can_move(self, dest_row, dest_col)

    def is_checkmate(self, color):
        # Check if the king of the given color is in check
        king = None
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if isinstance(piece, King) and piece.color == color:
                    king = piece
                    break
        if king is None or not self.is_in_check(color):
            return False

        # Check if there are any valid moves for the player
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    for r in range(8):
                        for c in range(8):
                            if self.is_valid_move(piece, r, c):
                                # Temporarily make the move
                                original_piece = self.get_piece(r, c)
                                self.set_piece(r, c, piece)
                                self.set_piece(row, col, None)
                                if not self.is_in_check(color):
                                    # Undo the move
                                    self.set_piece(row, col, piece)
                                    self.set_piece(r, c, original_piece)
                                    return False
                                # Undo the move
                                self.set_piece(row, col, piece)
                                self.set_piece(r, c, original_piece)
        return True

    def is_stalemate(self, color):
        # If the player is not in check, check for valid moves
        if not self.is_in_check(color):
            for row in range(8):
                for col in range(8):
                    piece = self.get_piece(row, col)
                    if piece and piece.color == color:
                        for r in range(8):
                            for c in range(8):
                                if self.is_valid_move(piece, r, c):
                                    return False
            return True
        return False

    def is_in_check(self, color):
        # Check if the king of the given color is in check
        king = None
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if isinstance(piece, King) and piece.color == color:
                    king = piece
                    break
        if king is None:
            return False

        # Check if any opponent's piece can attack the king
        for row in range(8):
            for col in range(8):
                piece = self.get_piece(row, col)
                if piece and piece.color != color and piece.can_move(self, king.row, king.col):
                    return True
        return False


class Player:
    def __init__(self, color):
        self.color = color

    def make_move(self, board, move):
        piece = move.piece
        dest_row = move.dest_row
        dest_col = move.dest_col

        if board.is_valid_move(piece, dest_row, dest_col):
            source_row = piece.row
            source_col = piece.col
            board.set_piece(source_row, source_col, None)
            board.set_piece(dest_row, dest_col, piece)
            piece.row = dest_row
            piece.col = dest_col
        else:
            raise ValueError("Invalid move!")

        
class Move:
    def __init__(self, piece, dest_row, dest_col):
        self.piece = piece
        self.dest_row = dest_row
        self.dest_col = dest_col


class Game:
    def __init__(self):
        self.board = Board()
        self.players = [Player(Color.WHITE), Player(Color.BLACK)]
        self.current_player = 0

    def start(self):
        # Game loop
        while not self._is_game_over():
            player = self.players[self.current_player]
            print(f"{player.color.name}'s turn.")

            # Get move from the player
            move = self._get_player_move(player)

            # Make the move on the board
            player.make_move(self.board, move)

            # Switch to the next player
            self.current_player = (self.current_player + 1) % 2

        # Display game result
        self._display_result()

    def _is_game_over(self):
        return self.board.is_checkmate(Color.WHITE) or self.board.is_checkmate(Color.BLACK) or \
               self.board.is_stalemate(Color.WHITE) or self.board.is_stalemate(Color.BLACK)

    def _get_player_move(self, player):
        while True:  # Loop until a valid move is made
            try:
                source_row = int(input("Enter source row: "))
                source_col = int(input("Enter source column: "))
                dest_row = int(input("Enter destination row: "))
                dest_col = int(input("Enter destination column: "))

                piece = self.board.get_piece(source_row, source_col)
                if piece is None or piece.color != player.color:
                    raise ValueError("Invalid piece selection!")

                move = Move(piece, dest_row, dest_col)
                if not self.board.is_valid_move(piece, dest_row, dest_col):
                    raise ValueError("Invalid move!")

                return move  # Return the valid move
            except ValueError as e:
                print(e)  # Print the error message and prompt again

    def _display_result(self):
        if self.board.is_checkmate(Color.WHITE):
            print("Black wins by checkmate!")
        elif self.board.is_checkmate(Color.BLACK):
            print("White wins by checkmate!")
        elif self.board.is_stalemate(Color.WHITE) or self.board.is_stalemate(Color.BLACK):
            print("The game ends in a stalemate!")


class ChessGameDemo:
    @staticmethod
    def run():
        game = Game()
        game.start()

if __name__ == "__main__":
    ChessGameDemo.run()