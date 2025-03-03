import random

class Board:
    SIZE = 4  # Define the size of the grid as 4x4

    def __init__(self):
        self.score=0
        self.grid = [[0] * self.SIZE for _ in range(self.SIZE)]
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        empty_cells = [(i, j) for i in range(self.SIZE) for j in range(self.SIZE) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def slide_left(self):
        moved = False
        for row in self.grid:
            compacted_row = [tile for tile in row if tile != 0]
            merged_row = []
            skip = False
            for i in range(len(compacted_row)):
                if skip:
                    skip = False
                    continue
                if i + 1 < len(compacted_row) and compacted_row[i] == compacted_row[i + 1]:
                    merged_value = compacted_row[i] * 2
                    merged_row.append(merged_value)
                    self.score += merged_value  # Update score on merge
                    print(f"Score updated: {self.score}")  # Print score after merge
                    skip = True
                    moved = True
                else:
                    merged_row.append(compacted_row[i])
            merged_row.extend([0] * (self.SIZE - len(merged_row)))
            if row != merged_row:
                moved = True
            row[:] = merged_row
        return moved, self.score

    def rotate_clockwise(self):
        """Rotate the board clockwise, for moving in other directions."""
        self.grid = [list(row) for row in zip(*self.grid[::-1])]

    def move(self, direction):
        """0=left, 1=right, 2=up, 3=down"""
        moved = False
        score=0
        if direction == 0:  # Left
            moved, score = self.slide_left()
        elif direction == 1:  # Right
            self.rotate_clockwise()
            self.rotate_clockwise()
            moved, score = self.slide_left()
            self.rotate_clockwise()
            self.rotate_clockwise()
        elif direction == 2:  # Up
            self.rotate_clockwise()
            self.rotate_clockwise()
            self.rotate_clockwise()
            moved, score = self.slide_left()
            self.rotate_clockwise()
        elif direction == 3:  # Down
            self.rotate_clockwise()
            moved, score = self.slide_left()
            self.rotate_clockwise()
            self.rotate_clockwise()
            self.rotate_clockwise()
        return moved, score

    def is_full(self):
        return all(tile != 0 for row in self.grid for tile in row)

    def can_merge(self):
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if i + 1 < self.SIZE and self.grid[i][j] == self.grid[i + 1][j]:
                    return True
                if j + 1 < self.SIZE and self.grid[i][j] == self.grid[i][j + 1]:
                    return True
        return False

    def is_game_over(self):
        return self.is_full() and not self.can_merge()

    def print_board(self):
        for row in self.grid:
            print('\t'.join(str(tile).rjust(4) if tile != 0 else '    ' for tile in row))
        print()

class Game:

    _instance = None

    def __init__(self):
        if Game._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Game._instance = self
            self.board = Board()

    @staticmethod
    def get_instance():
        if Game._instance is None:
            Game()
        return Game._instance
        

    def play(self):
        self.board.print_board()
        while True:
            move = input("Enter move (0=left, 1=right, 2=up, 3=down): ")
            if move not in {'0', '1', '2', '3'}:
                print("Invalid move. Please enter 0, 1, 2, or 3.")
                continue
            move = int(move)
            moved, score = self.board.move(move)
            if moved:
                self.board.add_random_tile()
                self.board.print_board()
                if any(2048 in row for row in self.board.grid):
                    print(f"Congratulations! You've reached 2048! Your score is: {score}")
                    break
                else:
                    print(f"Your score is {score}")
                if self.board.is_game_over():
                    print("Game over! No moves left.")
                    break
            else:
                print("No tiles moved. Try a different direction.")

if __name__ == "__main__":
    game = Game()
    game.play()
