class Board:
    def __init__(self, size=15):
        self.size = size
        self.board = [['.' for _ in range(size)] for _ in range(size)]

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def place_stone(self, row, col, stone):
        if self.is_valid_move(row, col):
            self.board[row][col] = stone
            return True
        return False

    def is_valid_move(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == '.'

    def check_winner(self, row, col, stone):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                nr, nc = row + dr*i, col + dc*i
                if not (0 <= nr < self.size and 0 <= nc < self.size) or self.board[nr][nc] != stone:
                    break
                count += 1
            for i in range(1, 5):
                nr, nc = row - dr*i, col - dc*i
                if not (0 <= nr < self.size and 0 <= nc < self.size) or self.board[nr][nc] != stone:
                    break
                count += 1
            if count >= 5:
                return True
        return False


class Player:
    def __init__(self, stone):
        self.stone = stone


class Gomoku:
    def __init__(self):
        self.board = Board()
        self.players = [Player('O'), Player('X')]
        self.current_player = 0

    def play(self, row, col):
        if self.board.place_stone(row, col, self.players[self.current_player].stone):
            if self.board.check_winner(row, col, self.players[self.current_player].stone):
                print(f"Player {self.current_player + 1} ({self.players[self.current_player].stone}) wins!")
                self.board.print_board()
                return True
            self.current_player = 1 - self.current_player
        else:
            print("Invalid move. Try again.")
        return False

    def start_game(self):
        game_over = False
        while not game_over:
            self.board.print_board()
            print(f"Player {self.current_player + 1}'s turn ({self.players[self.current_player].stone}):")
            row = int(input("Enter row: "))
            col = int(input("Enter column: "))
            game_over = self.play(row, col)


if __name__ == "__main__":
    game = Gomoku()
    game.start_game()
