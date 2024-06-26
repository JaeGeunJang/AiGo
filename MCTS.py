import random, math
import numpy as np
import torch

# 우선 코드 완성 
# 이제 기보 또는 state를 가지고 15X15X17의 Convolusion 생성 후 신경망에 넣어주는 작업 실시

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

    # CNN 학습을 위한 피쳐 생성
    def make_feature(self, state):
        current_state = state
        size = state.size
        current_player = state.player

        feature_map = np.zeros((size, size, 17), dtype=np.float32)
        tmp_state = [[0 for _ in range (size)] for _ in range(size)]

        gibo = current_state.gibo
        for g in gibo[:-8] :
            x, y, player = g
            tmp_state[y][x] = player
        
        tmp_gibo = gibo[-8:]

        for i in range (8):
            x, y, player = tmp_gibo[i]
            tmp_state[y][x] = player

            for y in range (size):
                for x in range (size):
                    if tmp_state[y][x] == current_player:
                        feature_map[y][x][16-(i+1)*2] = 1
                    elif tmp_state[y][x] == 3 - current_player:
                        feature_map[y][x][17-(i+1)*2] = 1
        
        for i in range (size):
            for j in range (size):
                feature_map[i][j] = current_player
        
        return feature_map

    def run(self, state, player):
        root = Node(0)  # 현재 상태의 기본 노드 설정
        root.player = player  # 현재 상태의 플레이어
        root.state = state.clone() # Root state 복사 

        for _ in range(self.simulations):
            node = root 
            search_path = [node] # 루트 노드를 첫 노드로 추가
            current_state = state.clone() # 시뮬레이션 시작 할 상태 복사

            while node.children:
                action, node = self.select_child(node) # 현재 상태에서의 node에서 가장 유망한 child 선택
                x, y = action
                current_state.place_stone(x, y) # action 선택 후 플레이
                search_path.append(node) # 선택된 node를 search path에 추가

            # parent 노드 찾기
            if len(search_path) < 2: #error 
                raise ValueError("검색 경로가 너무 짧습니다. 자식 노드가 부족합니다.")
            parent = search_path[-2]

            current_feature = self.make_feature(current_state)

            network_output = self.network.predict(current_feature) # current state를 이용하여 network를 통한 prob, value값 도출
            prob, value = network_output[0], network_output[1] 
            actions = [(i // self.size, i % self.size) for i in range(len(prob))]
            policy = prob

            valid_actions = [action for action in actions if current_state.is_valid_move(action[0], action[1], player)] # 가능한 액션들 다 고르기
            policy = torch.tensor([policy[actions.index(action)] for action in valid_actions]) # 유효한 액션들에 대한 policy 확률 업데이트

            for valid_action in valid_actions: # 가능한 액션들 중에서 선택 후 진행
                if valid_action not in parent.children: #아직 시행하지 않은 시뮬레이션의 경우
                    x, y = valid_action
                    child_node = Node(policy[valid_actions.index(valid_action)]) # 노드 추가
                    child_node.player = 3 - player # 플레이어 교체
                    child_node.state = current_state.clone() # state 복사
                    child_node.state.place_stone(valid_action) # 복사된 스테이트에 돌 놓기
                    parent.children[valid_action] = child_node 

            value = self.simulate(current_state, player) # 시뮬레이션 시작 
            self.backpropagate(search_path, value, player) #시뮬레이션 결과 백프로파게이션

        return self.select_action(root, temperator=self.temperator) #최종 선택된 결과 도출

    # 현재 노드들 중 가장 유망한 노드 선택 알고리즘 
    def select_child(self, node):
        total_visits = sum(child.visit_count for child in node.children.values()) # 해당 노드에서 방문한 횟수의 총합
        best_score = -1 # 가장 높은 점수를 저장할 변수
        best_action = None # 가장 높은 점수를 가진 액션 저장 변수
        best_child = None # 최고 점수를 갖는 자식 노드를 저장하는 변수

        for action, child in node.children.items(): # child를 하나씩 탐색하면서 UBC1 계산, 선택
            score = self.UCB1(total_visits, child.visit_count, child.prior) # 스코어 계산
            if score > best_score: # 점수가 높을 경우, 결과값 저장
                best_score = score
                best_action = action
                best_child = child

        return best_action, best_child # 최종 저장된 action, child 리턴

    def UCB1(self, total_visits, child_visits, prior): # UBC1 계산 알고리즘
        return prior + np.sqrt(2 * np.log(total_visits) / (child_visits + 1))

    def simulate(self, state, player):
        while state.get_winner() == 0: # 게임 오버가 되지 않는 동안, 시뮬레이션 실행
            valid_actions = state.get_valid_moves(player) # 해당 플레이어가 놓을 수 있는 액션 리스트 정리
            if not valid_actions:
                player = 3 - player # 플레이어 교체
                valid_actions = state.get_valid_moves(player) # 교체된 플레이어가 놓을 수 있는 액션 리스트 
            action = np.random.choice(valid_actions) # 랜덤하게 선택
            x, y = action
            state.place_stone(x, y) # 돌을 놓아본다
            player = 3 - player # 플레이어 교체
        
        # 게임이 끝날 경우
        winner = state.get_winner() # 승자의 정보 저장
        if winner == -1: #무승부라면, 0 반환
            return 0
        else: # 승자가 나라면 1, 아니라면 -1 (패배) 리턴
            return 1 if winner == player else -1

    def backpropagate(self, search_path, value, player):
        for node in reversed(search_path):
            node.visit_count += 1
            if node.player == player:
                node.value_sum += value
            else:
                node.value_sum -= value
            value = -value

    def select_action(self, root, temperator):
        visit_counts = np.array([child.visit_count for child in root.children.values()])
        if temperator == 0:
            best_child = root.children[max(root.children, key=lambda action: root.children[action].visit_count)]
            return best_child.state.gibo[-1][:2]
        else:
            visit_counts = visit_counts ** (1 / temperator)
            visit_probs = visit_counts / visit_counts.sum()
            action_idx = np.random.choice(len(visit_probs), p=visit_probs)
            # 수정: 선택된 action을 반환
            return list(root.children.keys())[action_idx]
            return list(root.children.keys())[action_idx]