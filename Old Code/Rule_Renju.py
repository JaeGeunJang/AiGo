class Board:
    def __init__(self, size=15):
        self.size = size
        self.board = [['.' for _ in range(size)] for _ in range(size)]

    def print_board(self):
        for row in self.board:
            print(' '.join(row))
        print()

    def is_valid_move(self, row, col, stone):
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == '.':
            if stone == 'O':  # 'O'를 흑돌로 가정
                return not (self.is_three_three(row, col, stone) or self.is_long_line(row, col, stone))
            return True
        return False

    def place_stone(self, row, col, stone):
        if self.is_valid_move(row, col, stone):
            self.board[row][col] = stone
            return True
        return False

    def check_line(self, row, col, dr, dc, stone, target_len):
        count = 0
        for _ in range(1, target_len):
            nr, nc = row + dr, col + dc
            if not (0 <= nr < self.size and 0 <= nc < self.size and self.board[nr][nc] == stone):
                break
            count += 1
            row, col = nr, nc
        return count

    def is_open_three(self, row, col, stone):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        open_threes = 0
        for dr, dc in directions:
            pre_count = self.check_line(row-dr, col-dc, -dr, -dc, stone, 3)
            post_count = self.check_line(row, col, dr, dc, stone, 3)
            if pre_count + post_count == 2:
                if self.is_empty(row-(pre_count+1)*dr, col-(pre_count+1)*dc) and self.is_empty(row+(post_count+1)*dr, col+(post_count+1)*dc):
                    open_threes += 1
        return open_threes >= 2

    def is_long_line(self, row, col, stone):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1 + self.check_line(row-dr, col-dc, -dr, -dc, stone, 5) + self.check_line(row, col, dr, dc, stone, 5)
            if count >= 6:
                return True
        return False

    def is_empty(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] == '.'

    def is_three_three(self, row, col, stone):
        if stone != 'O':  # 'O'가 흑돌로 가정
            return False
        self.board[row][col] = stone  # 가상으로 돌을 두고 체크
        if self.is_open_three(row, col, stone):
            self.board[row][col] = '.'  # 원상태로 복구
            return True
        self.board[row][col] = '.'  # 원상태로 복구
        return False

class Player:
    def __init__(self, stone):
        self.stone = stone

class Gomoku:
    def __init__(self):
        self.board = Board()
        self.players = [Player('O'), Player('X')]  # 'O'를 흑돌, 'X'를 백돌로 가정
        self.current_player = 0  # 게임 시작 플레이어

    def play(self, row, col):
        if self.board.place_stone(row, col, self.players[self.current_player].stone):
            if self.check_winner(row, col, self.players[self.current_player].stone):
                print(f"Player {self.current_player + 1} ({self.players[self.current_player].stone}) wins!")
                self.board.print_board()
                return True
            self.current_player = 1 - self.current_player  # 플레이어 교체
        else:
            print("Invalid move. Try again.")
        return False

    def start_game(self):
        game_over = False
        while not game_over:
            self.board.print_board()
            print(f"Player {self.current_player + 1}'s turn ({self.players[self.current_player].stone}):")
            try:
                row = int(input("Enter row: "))
                col = int(input("Enter column: "))
                game_over = self.play(row, col)
            except ValueError:
                print("Invalid input. Please enter a valid row and column.")

    def check_winner(self, row, col, stone):
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                if self.board.is_empty(row + i*dr, col + i*dc) and self.board.board[row + i*dr][col + i*dc] == stone:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                if self.board.is_empty(row - i*dr, col - i*dc) and self.board.board[row - i*dr][col - i*dc] == stone:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

if __name__ == "__main__":
    game = Gomoku()
    game.start_game()
