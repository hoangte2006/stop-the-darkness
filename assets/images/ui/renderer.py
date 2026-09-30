import pygame
import sys
import random


class TileMapRenderer:
    def __init__(self, tile_size=40):
        self.tile_size = tile_size
        self.tiles = {}

    def load_sprites(self):
        """
        Mỗi tile ID tương ứng với 1 ảnh riêng.
        """

        sprite_paths = {
            0: "sprites/trees/tree-3.png",
            1: "sprites/ground/ground.png",
            2: "sprites/water/water.png",
            3: "sprites/stone/stone-3.png",
            4: "sprites/structure/building-3.png",
            5: "sprites/darkness/darkness.png",
        }

        for tile_id, filepath in sprite_paths.items():
            try:
                image = pygame.image.load(filepath).convert_alpha()

                # Scale ảnh về đúng TILE_SIZE x TILE_SIZE
                image = pygame.transform.scale(
                    image,
                    (self.tile_size, self.tile_size)
                )

                self.tiles[tile_id] = image

            except FileNotFoundError:
                print(f"Lỗi: Không tìm thấy ảnh {filepath}")
                sys.exit()

    def draw(self, surface, grid_matrix):
        for row_idx, row in enumerate(grid_matrix):
            for col_idx, tile_id in enumerate(row):

                x = col_idx * self.tile_size
                y = row_idx * self.tile_size

                if tile_id in self.tiles:
                    surface.blit(
                        self.tiles[tile_id],
                        (x, y)
                    )


def get_spiral_coordinates(rows, cols):
    """
    Trả về danh sách tọa độ (row, col)
    theo đường xoắn ốc từ ngoài vào trong.
    """

    coords = []

    top = 0
    bottom = rows - 1
    left = 0
    right = cols - 1

    while top <= bottom and left <= right:

        # 1. Trái -> phải
        for i in range(left, right + 1):
            coords.append((top, i))

        top += 1

        # 2. Trên -> dưới
        for i in range(top, bottom + 1):
            coords.append((i, right))

        right -= 1

        # 3. Phải -> trái
        if top <= bottom:
            for i in range(right, left - 1, -1):
                coords.append((bottom, i))

            bottom -= 1

        # 4. Dưới -> trên
        if left <= right:
            for i in range(bottom, top - 1, -1):
                coords.append((i, left))

            left += 1

    return coords


# ==========================================
# KHỞI TẠO GAME
# ==========================================

pygame.init()

ROWS = 12
COLS = 16
TILE_SIZE = 40

screen = pygame.display.set_mode(
    (
        COLS * TILE_SIZE,
        ROWS * TILE_SIZE
    )
)

pygame.display.set_caption(
    "Bóng tối lấn chiếm xoắn ốc"
)


# ==========================================
# LOAD SPRITE
# ==========================================

renderer = TileMapRenderer(TILE_SIZE)

renderer.load_sprites()


# ==========================================
# SINH MAP NGẪU NHIÊN
# ==========================================

# Chỉ random 0 -> 4
# ID 5 dành cho bóng tối

level_matrix = [
    [
        random.randint(0, 4)
        for _ in range(COLS)
    ]
    for _ in range(ROWS)
]


# ==========================================
# TẠO ĐƯỜNG XOẮN ỐC
# ==========================================

spiral_path = get_spiral_coordinates(
    ROWS,
    COLS
)

current_step = 0


# ==========================================
# TIMER BÓNG TỐI
# ==========================================

DARKNESS_SPREAD_EVENT = pygame.USEREVENT + 1

pygame.time.set_timer(
    DARKNESS_SPREAD_EVENT,
    2000
)


# ==========================================
# GAME LOOP
# ==========================================

running = True

clock = pygame.time.Clock()

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == DARKNESS_SPREAD_EVENT:

            if current_step < len(spiral_path):

                r, c = spiral_path[current_step]

                # Đổi tile hiện tại thành sprite bóng tối
                level_matrix[r][c] = 5

                current_step += 1


    # ======================================
    # DRAW
    # ======================================

    screen.fill((0, 0, 0))

    renderer.draw(
        screen,
        level_matrix
    )

    pygame.display.flip()

    clock.tick(60)


pygame.quit()
sys.exit()