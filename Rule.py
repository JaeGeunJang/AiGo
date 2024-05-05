# V  기보 파일 저장
# V  수 순서 저장
# V  AI용 legal moving 적용 
#    3X3, 4X4, 장목 금수 적용
# V  입력은 따로 받지 않음

class Board:
    def __init__(self, size=15):
        # 기본 세팅 (보드 사이즈, 기보 저장 배열)
        self.size = size
        self.board = [[0 for _ in range (self.size)] for _ in range (self.size)]
        self.gibo = []

        # 돌 놓는 순서
        self.turn_num = 1
        self.player = 1 # 1 : black, 2 : white

        self.board = [[0 for _ in range(size)] for _ in range(size)]
    
    def clone(self):
        # 새 Board 객체 생성
        clone_board = Board(size=self.size)
        # 2차원 리스트의 깊은 복사
        clone_board.board = [row[:] for row in self.board]  
        # 기보 기록 복사 (CNN 구조 생성 시 필요)
        clone_board.gibo = self.gibo[:]  
        # 턴 번호 복사
        clone_board.turn_num = self.turn_num  
        # 현재 플레이어 복사
        clone_board.player = self.player  
        
        return clone_board


    def is_valid_move(self, x, y, player):
        # 돌 위치가 정당한지 확인
        if 0 <= x < self.size and 0 <= y < self.size and self.board[y][x] == 0:
            # 흑돌일 경우 렌주룰 적용
            if player == 1:
                if self.check_samsam(x, y) and self.check_sasa(x, y) and self.check_sixmok(x, y):
                    return True
            # 백색일 경우 렌주룰 적용 X (금수 없음)
            if player == 2:
                return True
        
        # 위 조건을 만족하지 못 할 경우 패스
        return False
    
    # 돌 놓는 위치
    def place_stone(self, x, y):
        if self.turn_num == 1:
            self.board[self.size//2][self.size//2] = self.player
            self.gibo.append([self.size//2, self.size//2, self.player])
            self.player = 3 - self.player
            self.turn_num += 1
            return True

        elif self.is_valid_move(x, y, self.player):
            self.board[y][x] = self.player
            self.gibo.append([y, x, self.player])
            self.player = 3 - self.player
            self.turn_num += 1
            return True
        
        return False
    
    def is_game_over(self, x, y):
        if self.board[y][x] == 0 :
            return False
        player = self.board[y][x]

        directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    
        for dx, dy in directions:
            count = 0
            for n in range(-4, 5):
                nx, ny = x + dx*n, y + dy*n
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if self.board[ny][nx] == player:
                        count += 1
                        if count == 5 :
                            return player
                    else :
                        count = 0
                else :
                    break
        return False

    def get_winner(self):
        # 무승부 조건 처리
        if not any(0 in row for row in self.board):
            return -1
        
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] != 0:
                    player = self.board[y][x]
                    if self.is_game_over(x, y):
                        return player
        return 0

    # 금수 설정 (추후 작성 필요)
    def check_samsam(self, x, y):
        return True

    def check_sasa(self, x, y):
        return True

    def check_sixmok(self, x, y):
        return True
    
    # 신경망에서 legal move 받을 시 생성되는 리스트 
    def get_valid_moves(self, player):
        legal_move = list()

        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == 0:
                    if player == 1:
                        if self.check_samsam(x, y) and self.check_sasa(x, y) and self.check_sixmok(x, y):
                            legal_move.append((x, y))
                    if player == 2:
                        legal_move.append((x, y))
        return legal_move