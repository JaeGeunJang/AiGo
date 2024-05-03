import random, math
import numpy as np
import torch

'''
# 기본적인 MCTS 구조. 변형 필요
class MCTSNode:
    def __init__(self, state, player=1, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_move = state.ai_valid_move(player)

    def add_child(self, move, state):
        child = MCTSNode(state=state, parent=self, move=move)
        self.untried_moves.remove(move)
        self.children.append(child)
        return child
    
    def update(self, result):
        self.visits += 1
        self.wins += result

    def UCB(self, mean_value, percentage, parents, child, explore = 2**0.5):
        return mean_value + explore * percentage * (parents**0.5) / (1+child)


각 트리들은 수가 선택 된 이후 다음 스텝에도 사용되기 때문에 남아 있어야함.
머리 아프네... 
Parents Node에 Dictionary 형식 저장 후 선택되면 나머지 삭제
N(s, a), Q(s, a), Temperator, Prior 필요
MCTS 코드 내에서 직접 RNN을 시행하지는 않도록 작성
'''
# Player는 1(흑)과 2(백)으로 설정되어 있음.
class Node:
    def __init__(self, prior):
        self.visit_count = 0
        self.player = 0
        self.prior = prior
        self.value_sum = 0
        self.children = {}
        self.state = None

# Player는 1(흑)과 2(백)으로 설정되어 있음.
class MCTS:
    def __init__(self, player, state, network, temperator, simulation, C):
        self.state = state  # 현재 MCTS를 진행할 board
        self.size = state.size
        self.network = network  # 예측 및 훈련에 사용할 Neural Network
        self.temperator = temperator  # Temperator (랜덤 선택 시)
        self.simulations = simulation  # 시뮬레이션 횟수
        self.prob_c = C  # 밸런스 조정 상수
        self.player = player  # 현재 플레이어

    def run(self, state, player):
        root = Node(0)  # 현재 상태의 기본 노드 설정
        root.player = player  # 현재 상태의 플레이어
        root.state = state.clone()

        for _ in range(self.simulations):
            node = root
            search_path = [node]
            current_state = state.clone()

            while node.children:
                action, node = self.select_child(node)
                current_state.place_stone(action)
                search_path.append(node)

            parent = search_path[-2]
            network_output = self.network.predict(current_state)
            prob, value = network_output[0], network_output[1]
            actions = [(i // self.size, i % self.size) for i in range(len(prob))]
            policy = prob

            valid_actions = [action for action in actions if current_state.is_valid_move(action[0], action[1], player)]
            policy = torch.tensor([policy[actions.index(action)] for action in valid_actions])

            for valid_action in valid_actions:
                if valid_action not in parent.children:
                    child_node = Node(policy[valid_actions.index(valid_action)])
                    child_node.player = 3 - player
                    child_node.state = current_state.clone()
                    child_node.state.place_stone(valid_action)
                    parent.children[valid_action] = child_node

            value = self.simulate(current_state, player)
            self.backpropagate(search_path, value, player)

        return self.select_action(root, temperator=self.temperator)

    def select_child(self, node):
        total_visits = sum(child.visit_count for child in node.children.values())
        best_score = -1
        best_action = None
        best_child = None

        for action, child in node.children.items():
            score = self.UCB1(total_visits, child.visit_count, child.prior)
            if score > best_score:
                best_score = score
                best_action = action
                best_child = child

        return best_action, best_child

    def UCB1(self, total_visits, child_visits, prior):
        return prior + np.sqrt(2 * np.log(total_visits) / (child_visits + 1))

    def simulate(self, state, player):
        while not state.is_game_over():
            valid_actions = state.get_valid_moves(player)
            if not valid_actions:
                player = 3 - player
                valid_actions = state.get_valid_moves(player)
            action = np.random.choice(valid_actions)
            state.place_stone(action)
            player = 3 - player

        winner = state.get_winner()
        if winner == 0:
            return 0
        else:
            return 1 if winner == player else -1

    def backpropagate(self, search_path, value, player):
        for node in reversed(search_path):
            node.visit_count += 1
            node.value_sum += value if node.player == player else -value
            value = -value

    def select_action(self, root, temperator):
        visit_counts = np.array([child.visit_count for child in root.children.values()])
        if temperator == 0:
            best_child = root.children[max(root.children, key=lambda action: root.children[action].visit_count)]
            return best_child.state.get_last_action()
        else:
            visit_counts = visit_counts ** (1 / temperator)
            visit_probs = visit_counts / visit_counts.sum()
            action_idx = np.random.choice(len(visit_probs), p=visit_probs)
            return list(root.children.keys())[action_idx]