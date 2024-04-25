import random
import math

class MCTSNode:
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = state.get_legal_moves()

    def select_child(self):
        return sorted(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))[-1]

    def add_child(self, move, state):
        child = MCTSNode(state=state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child

    def update(self, result):
        self.visits += 1
        self.wins += result

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

            if self.current_player == 1:  # AI의 턴
                print("AI's turn:")
                move = self.mcts_search(self.board)
                self.play(move[0], move[1])
            else:  # 인간 플레이어의 턴
                print(f"Player {self.current_player + 1}'s turn ({self.players[self.current_player].stone}):")
                row = int(input("Enter row: "))
                col = int(input("Enter column: "))
                game_over = self.play(row, col)


    def simulate(self, node):
        current_state = node.state.clone()
        while current_state.get_legal_moves():
            current_state.do_move(random.choice(current_state.get_legal_moves()))
        return current_state.get_result(self.current_player)

    def mcts_search(self, state, iterations=1000):
        root = MCTSNode(state=state)

        for _ in range(iterations):
            node = root
            simulation_state = state.clone()

            # Selection
            while node.untried_moves == [] and node.children != []:
                node = node.select_child()
                simulation_state.do_move(node.move)

            # Expansion
            if node.untried_moves != []:
                move = random.choice(node.untried_moves)
                simulation_state.do_move(move)
                node = node.add_child(move, simulation_state)

            # Simulation
            result = self.simulate(node)

            # Backpropagation
            while node is not None:
                node.update(result)
                node = node.parent

        return sorted(root.children, key=lambda c: c.visits)[-1].move
