import pygame
import sys

# Pygame 초기화
pygame.init()

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# 게임 화면 설정
BOARD_SIZE = 15
TILE_SIZE = 40
WIDTH = HEIGHT = TILE_SIZE * (BOARD_SIZE + 1)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gomoku Game")

# 오목판 그리기 함수
def draw_board():
    screen.fill(WHITE)
    for i in range(1, BOARD_SIZE + 1):
        pygame.draw.line(screen, BLACK, (TILE_SIZE, i * TILE_SIZE), (WIDTH - TILE_SIZE, i * TILE_SIZE))
        pygame.draw.line(screen, BLACK, (i * TILE_SIZE, TILE_SIZE), (i * TILE_SIZE, HEIGHT - TILE_SIZE))
    pygame.display.update()

# 돌 놓기 함수
def place_stone(x, y, stone_color):
    pygame.draw.circle(screen, stone_color, (x * TILE_SIZE, y * TILE_SIZE), TILE_SIZE // 2 - 2)
    pygame.display.update()

# 게임 루프
def game_loop():
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
                row = mouseX // TILE_SIZE
                col = mouseY // TILE_SIZE
                if 1 <= row <= BOARD_SIZE and 1 <= col <= BOARD_SIZE:
                    stone_color = BLACK if turn % 2 == 0 else WHITE
                    place_stone(row, col, stone_color)
                    turn += 1

        pygame.display.update()

if __name__ == "__main__":
    draw_board()
    game_loop()
