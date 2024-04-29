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
    def __init__(self, prior):
        self.visited = 0
        self.prior = prior
        self.value_sum = 0
        self.children = {}
        

class MCTS:
    def __init__(self, state, network, temperator, simulation, C):
        self.state = state
        self.networks = network
        self.temperator = temperator
        self.simulations = simulation
        self.prob_c = C
    
    