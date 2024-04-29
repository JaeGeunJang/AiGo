import random, math

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

'''
각 트리들은 수가 선택 된 이후 다음 스텝에도 사용되기 때문에 남아 있어야함.
머리 아프네... 
Parents Node에 Dictionary 형식 저장 후 선택되면 나머지 삭제
N(s, a), Q(s, a), Temperator, Prior 필요
MCTS 코드 내에서 직접 RNN을 시행하지는 않도록 작성
'''

class Node:
    def __init__(self):
        self.parents = None
        self.child = None

# 코파일럿 코드
import torch
import numpy as np

class Node:
    def __init__(self, prior: float):
        self.visit_count = 0
        self.to_play = -1
        self.prior = prior
        self.value_sum = 0
        self.children = {}

class MCTS:
    def __init__(self, game, network, args):
        self.game = game
        self.network = network
        self.args = args

    def run(self, state, to_play):
        root = Node(0)
        root.to_play = to_play
        for _ in range(self.args.num_simulations):
            node = root
            search_path = [node]
            current_state = state.clone()

            while node.children:
                action, node = self.select_child(node)
                current_state.step(action)
                search_path.append(node)

            parent = search_path[-2]
            network_output = self.network.predict(current_state)
            action_probs, value = network_output["policy_logits"], network_output["value"]
            actions, policy = zip(*action_probs.items())
            mask = torch.tensor([self.game.is_valid_action(a) for a in actions])
            policy = torch.softmax(policy[mask], dim=0)

            node = Node(policy)
            node.to_play = -parent.to_play
            parent.children[action] = node
            search_path.append(node)

            self.backpropagate(search_path, value, to_play)

        return self.select_action(root, temperature=self.args.temperature)

    def select_child(self, node):
        _, action, child = max((self.ucb_score(node, child), action, child) for action, child in node.children.items())
        return action, child

    def ucb_score(self, parent, child):
        pb_c = np.log((parent.visit_count + self.args.pb_c_base + 1) / self.args.pb_c_base) + self.args.pb_c_init
        pb_c *= np.sqrt(parent.visit_count) / (child.visit_count + 1)

        prior_score = pb_c * child.prior
        value_score = child.value()
        return prior_score + value_score

    def backpropagate(self, search_path, value, to_play):
        for node in search_path[::-1]:
            node.value_sum += value if node.to_play == to_play else -value
            node.visit_count += 1
            value = -value

    def select_action(self, node, temperature):
        visit_counts = [(child.visit_count, action) for action, child in node.children.items()]
        actions, counts = zip(*visit_counts)
        if temperature == 0:
            action = actions[np.argmax(counts)]
        else:
            counts = np.array(counts)**(1/temperature)
            probs = counts / np.sum(counts)
            action = np.random.choice(actions, p=probs)
        return action
