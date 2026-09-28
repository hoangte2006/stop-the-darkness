import pygame
import sys
import random

class TileMapRenderer:
    def __init__(self, tile_size=40):
        self.tile_size = tile_size
        self.tiles = {}

    def load_spritesheet(self, filepath):
        try:
            sheet = pygame.image.load(filepath).convert_alpha()
            for i in range(6):
                rect = pygame.Rect(i * self.tile_size, 0, self.tile_size, self.tile_size)
                tile_image = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                tile_image.blit(sheet, (0, 0), rect)
                self.tiles[i] = tile_image
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy {filepath}. Hãy chắc chắn bạn đã chạy code tạo ảnh trước đó!")
            sys.exit()

    def draw(self, surface, grid_matrix):
        for row_idx, row in enumerate(grid_matrix):
            for col_idx, tile_id in enumerate(row):
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size
                if tile_id in self.tiles:
                    surface.blit(self.tiles[tile_id], (x, y))

def get_spiral_coordinates(rows, cols):
    """Hàm trả về danh sách tọa độ (row, col) theo đường xoắn ốc từ ngoài vào trong"""
    coords = []
    top, bottom = 0, rows - 1
    left, right = 0, cols - 1

    while top <= bottom and left <= right:
        # 1. Đi từ trái sang phải (hàng trên cùng)
        for i in range(left, right + 1):
            coords.append((top, i))
        top += 1

        # 2. Đi từ trên xuống dưới (cột ngoài cùng bên phải)
        for i in range(top, bottom + 1):
            coords.append((i, right))
        right -= 1

        # 3. Đi từ phải sang trái (hàng dưới cùng)
        if top <= bottom:
            for i in range(right, left - 1, -1):
                coords.append((bottom, i))
            bottom -= 1

        # 4. Đi từ dưới lên trên (cột ngoài cùng bên trái)
        if left <= right:
            for i in range(bottom, top - 1, -1):
                coords.append((i, left))
            left += 1

    return coords

# ==========================================
# KHỞI TẠO GAME
# ==========================================
pygame.init()
ROWS, COLS = 12, 16 # Bản đồ 16 cột, 12 hàng
TILE_SIZE = 40
screen = pygame.display.set_mode((COLS * TILE_SIZE, ROWS * TILE_SIZE))
pygame.display.set_caption("Bóng tối lấn chiếm xoắn ốc")

# Tải công cụ vẽ và ảnh
renderer = TileMapRenderer(TILE_SIZE)
renderer.load_spritesheet('spritesheet.png')

# 1. Tạo bản đồ hoàn toàn NGẪU NHIÊN (ID từ 0 đến 4, không có 5-Bóng tối)
level_matrix = [[random.randint(0, 4) for _ in range(COLS)] for _ in range(ROWS)]

# 2. Lấy danh sách tọa độ xoắn ốc
spiral_path = get_spiral_coordinates(ROWS, COLS)
current_step = 0 # Biến theo dõi xem bóng tối đã nuốt tới ô thứ mấy

# 3. Cài đặt Event Hẹn giờ (Timer) - Cứ 2000 mili giây (2s) sẽ kích hoạt 1 lần
DARKNESS_SPREAD_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(DARKNESS_SPREAD_EVENT, 2000) # Đổi 2000 thành số nhỏ hơn (ví dụ 100) nếu muốn chạy nhanh để test

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Bắt sự kiện thời gian đếm ngược 2s
        elif event.type == DARKNESS_SPREAD_EVENT:
            if current_step < len(spiral_path):
                # Lấy tọa độ hiện tại ở vòng xoắn ốc
                r, c = spiral_path[current_step]
                
                # Biến ô đó thành Bóng tối (ID = 5)
                level_matrix[r][c] = 5 
                
                current_step += 1 # Tăng chỉ số để lần sau nuốt ô tiếp theo

    # Vẽ mọi thứ
    screen.fill((0, 0, 0))
    renderer.draw(screen, level_matrix)
    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
sys.exit()