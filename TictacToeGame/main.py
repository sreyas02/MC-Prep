class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def get_name(self):
        return self.name

    def get_symbol(self):
        return self.symbol
    
class Board:
    def __init__(self):
        self.grid = [['-' for _ in range(3)] for _ in range(3)]
        self.moves_count = 0

    def make_move(self, row, col, symbol):
        if not (0 <= row < 3 and 0 <= col < 3) or self.grid[row][col] != '-':
            raise ValueError("Invalid move!")
        self.grid[row][col] = symbol
        self.moves_count += 1

    def is_full(self):
        return self.moves_count == 9

    def has_winner(self):
        # Check rows
        for row in range(3):
            if self.grid[row][0] != '-' and self.grid[row][0] == self.grid[row][1] == self.grid[row][2]:
                return True

        # Check columns
        for col in range(3):
            if self.grid[0][col] != '-' and self.grid[0][col] == self.grid[1][col] == self.grid[2][col]:
                return True

        # Check diagonals
        if self.grid[0][0] != '-' and self.grid[0][0] == self.grid[1][1] == self.grid[2][2]:
            return True
        return self.grid[0][2] != '-' and self.grid[0][2] == self.grid[1][1] == self.grid[2][0]

    def print_board(self):
        for row in range(3):
            print(" ".join(self.grid[row]))
        print()


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.board = Board()
        self.current_player = player1

    def play(self):
        self.board.print_board()
        while not self.board.is_full() and not self.board.has_winner():
            print(f"{self.current_player.get_name()}'s turn.")
            row = self.get_valid_input("Enter row (0-2): ")
            col = self.get_valid_input("Enter column (0-2): ")
            try:
                self.board.make_move(row, col, self.current_player.get_symbol())
                self.board.print_board()
                self.switch_player()
            except ValueError as e:
                print(str(e))

        if self.board.has_winner():
            self.switch_player()
            print(f"{self.current_player.get_name()} wins!")
        else:
            print("It's a draw!")

    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def get_valid_input(self, message):
        while True:
            try:
                user_input = int(input(message))
                if 0 <= user_input <= 2:
                    return user_input
                else:
                    print("Invalid input! Please enter a number between 0 and 2.")
            except ValueError:
                print("Invalid input! Please enter a number between 0 and 2.")


class TicTacToeDemo:
    @staticmethod
    def run():
        player1 = Player("Player 1", 'X')
        player2 = Player("Player 2", 'O')
        game = Game(player1, player2)
        game.play()

if __name__ == "__main__":
    TicTacToeDemo.run()