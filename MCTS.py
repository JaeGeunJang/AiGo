import random, math
import numpy as np

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
        self.visited = 0
        self.player = 0
        self.prior = prior
        self.value_sum = 0
        self.children = {}

# Player는 1(흑)과 2(백)으로 설정되어 있음.
class MCTS:
    def __init__(self, state, network, temperator, simulation, C):
        self.state = state # 현재 MCTS를 진행할 board
        self.network = network # 예측 및 훈련에 사용할 Neural Network
        self.temperator = temperator # Temperator (랜덤 선택 시)
        self.simulations = simulation # 시뮬레이션 횟수
        self.prob_c = C # 밸런스 조정 상수
        self.player = 0 # 현재 플레이어
    
    def run(self, state, player):
        root = Node(0) # 현재 상태의 기본 노드 설정
        root.player = player # 현재 상태의 플레이어

        for _ in range(self.simulations):
            node = root
            search_path = [node]
            current_state = state.clone()

            while node.children:
                action, node = self.select_child(node)
                current_state.place_stone(action)
                search_path.append(node)
        
        parent = search_path[-2]
        network_output = self.networks.predict(current_state)
        prob, value = network_output[0], network_output[1]
        

    
    def UCB1(self):
        pass

    def backpropagate(self):
        pass

    # 시뮬레이션에서 차일드 선택 하는 방법?
    def select_child(self):
        pass

    # 시뮬레이션 이후 최종 선택 하는 방법?
    def select_action(self, node):
        if self.temperator == 0:
            action = action
        else:
            counts = np.array(counts)**(1/self.temperator)
            probs = counts / np.sum(counts)
            action = np.random.choice(actions, p = probs)
            