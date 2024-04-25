import pygame
import sys

# Pygame 초기화
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BOARD_COLOR = (245, 222, 179)  # 바둑판에 가까운 밀색(Wheat)

# 게임 화면 설정
BOARD_SIZE = 15
TILE_SIZE = 40
WIDTH = HEIGHT = TILE_SIZE * (BOARD_SIZE + 1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gomoku Game")

# 오목판 그리기 함수
def draw_board():
    screen.fill(BOARD_COLOR)
    for i in range(1, BOARD_SIZE + 1):
        pygame.draw.line(screen, BLACK, (TILE_SIZE, i * TILE_SIZE), (WIDTH - TILE_SIZE, i * TILE_SIZE))
        pygame.draw.line(screen, BLACK, (i * TILE_SIZE, TILE_SIZE), (i * TILE_SIZE, HEIGHT - TILE_SIZE))
    pygame.display.update()

# 돌 놓기 함수
def place_stone(x, y, stone_color):
    pygame.draw.circle(screen, stone_color, ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE), TILE_SIZE // 2 - 2)
    pygame.display.update()

# 게임 상태 배열 초기화
def initialize_board():
    return [["-" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

# 게임 루프
def game_loop(board):
    turn = 0  # 0: 흑돌, 1: 백돌
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = pygame.mouse.get_pos()
                row = (mouseX + TILE_SIZE // 2) // TILE_SIZE - 1
                col = (mouseY + TILE_SIZE // 2) // TILE_SIZE - 1
                if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[col][row] == "-":
                    stone_color = BLACK if turn % 2 == 0 else WHITE
                    stone_symbol = "O" if turn % 2 == 0 else "X"
                    place_stone(row, col, stone_color)
                    board[col][row] = stone_symbol
                    turn += 1
                    print(f"Board Updated at ({col}, {row}):")
                    for line in board:
                        print(" ".join(line))

        pygame.display.update()

if __name__ == "__main__":
    board = initialize_board()
    draw_board()
    game_loop(board)
