import numpy as np

class Node:
    def __init__(self, parent=None, prior_prob=0):
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value_sum = 0
        self.prior_prob = prior_prob
        self.player = 1

    def is_leaf(self):
        return len(self.children) == 0

    def value(self):
        if self.visits == 0:
            return 0
        return self.value_sum / self.visits

class MCTS:
    def __init__(self, state, network, temperator, simulation, C):
        self.state = state  # 현재 MCTS를 진행할 board
        self.size = state.size
        self.network = network  # 예측 및 훈련에 사용할 Neural Network
        self.temperator = temperator  # Temperator (랜덤 선택 시)
        self.simulations = simulation  # 시뮬레이션 횟수
        self.prob_c = C  # 밸런스 조정 상수
        self.player = 1  # 현재 플레이어

    def run(self):
        root = Node()
        for _ in range(self.simulations):
            node = root
            state = self.state.copy()
            search_path = [node]

            # Selection
            while not node.is_leaf():
                action, node = self.select_child(node, state)
                state.play(action)
                search_path.append(node)

            # Expansion
            if not state.is_game_over():
                action_probs, _ = self.network.predict(state)
                for action, prob in enumerate(action_probs):
                    if action not in node.children:
                        child_node = Node(parent=node, prior_prob=prob)
                        node.children[action] = child_node

            # Simulation
            value = self.simulate(state)

            # Backpropagation
            for node in reversed(search_path):
                node.visits += 1
                node.value_sum += value if node.player == self.player else -value
                value = -value

        return self.get_action_probs(root)

    def select_child(self, node, state):
        best_score = -float('inf')
        best_action = None
        best_child = None

        for action, child in node.children.items():
            if not state.is_valid_move(action):
                continue
            score = self.ucb_score(node, child)
            if score > best_score:
                best_score = score
                best_action = action
                best_child = child

        if best_child is None:
            action_probs, _ = self.network.predict(state)
            best_action = np.random.choice(state.get_legal_actions(), p=action_probs)
            best_child = node.children.get(best_action)
            if best_child is None:
                best_child = Node(parent=node, prior_prob=action_probs[best_action])
                node.children[best_action] = best_child

        return best_action, best_child

    def ucb_score(self, parent, child):
        pb_c = np.log((parent.visits + self.prob_c + 1) / self.prob_c) + self.prob_c
        pb_c *= np.sqrt(parent.visits) / (child.visits + 1)

        prior_score = pb_c * child.prior_prob
        value_score = child.value()

        return prior_score + value_score

    def simulate(self, state):
        while not state.is_game_over():
            action_probs, _ = self.network.predict(state)
            action = np.random.choice(state.get_legal_actions(), p=action_probs)
            state.play(action)
        return state.get_winner()

    def get_action_probs(self, root):
        visits = np.array([child.visits for child in root.children.values()])
        if self.temperator == 0:
            best_action = np.argmax(visits)
            action_probs = np.zeros_like(visits)
            action_probs[best_action] = 1
        else:
            visits_temp = visits ** (1 / self.temperator)
            action_probs = visits_temp / np.sum(visits_temp)
        return action_probs
    
if __name__ == 'main':
    import numpy as np

class TicTacToeState:
    def __init__(self):
        self.board = np.zeros((3, 3), dtype=int)
        self.player = 1

    def get_legal_actions(self):
        return list(zip(*np.where(self.board == 0)))

    def is_valid_move(self, action):
        return self.board[action] == 0

    def play(self, action):
        self.board[action] = self.player
        self.player = 3 - self.player

    def is_game_over(self):
        for row in self.board:
            if abs(sum(row)) == 3:
                return True
        for col in self.board.T:
            if abs(sum(col)) == 3:
                return True
        if abs(sum(np.diag(self.board))) == 3:
            return True
        if abs(sum(np.diag(np.fliplr(self.board)))) == 3:
            return True
        return np.all(self.board != 0)

    def get_winner(self):
        for row in self.board:
            if abs(sum(row)) == 3:
                return sum(row) // 3
        for col in self.board.T:
            if abs(sum(col)) == 3:
                return sum(col) // 3
        if abs(sum(np.diag(self.board))) == 3:
            return sum(np.diag(self.board)) // 3
        if abs(sum(np.diag(np.fliplr(self.board)))) == 3:
            return sum(np.diag(np.fliplr(self.board))) // 3
        return 0

    def copy(self):
        new_state = TicTacToeState()
        new_state.board = self.board.copy()
        new_state.player = self.player
        return new_state

class DummyNetwork:
    def predict(self, state):
        legal_actions = state.get_legal_actions()
        probs = np.ones(len(legal_actions)) / len(legal_actions)
        return dict(zip(legal_actions, probs)), 0

def test_mcts():
    state = TicTacToeState()
    network = DummyNetwork()
    mcts = MCTS(state, network, temperator=1, simulation=100, C=1)

    while not state.is_game_over():
        action_probs = mcts.run()
        action = np.random.choice(len(action_probs), p=action_probs)
        state.play(action)
        print(f"Player {3 - state.player} plays: {action}")
        print(state.board)
        print()

    winner = state.get_winner()
    if winner != 0:
        print(f"Player {winner} wins!")
    else:
        print("It's a draw!")

if __name__ == "__main__":
    test_mcts()