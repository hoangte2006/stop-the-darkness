"""Terrain and board map generation.

TODO (TV6): thay thuật toán random đơn giản dưới đây bằng Cellular Automata
hoặc Perlin Noise để tạo các cụm rừng/đá/nước tự nhiên (liền mảng) hơn.
Chữ ký hàm generate_map(rows, cols) phải giữ nguyên vì game_state.py gọi thẳng vào đó.
"""

import random

from core.constants import GRID_COLS, GRID_ROWS

TERRAIN_WEIGHTS = [
    ("forest", 0.15),
    ("rock", 0.10),
    ("water", 0.07),
]


def generate_map(rows=GRID_ROWS, cols=GRID_COLS):
    """Sinh ma trận địa hình rows x cols.

    Trả về: list[list[str]], mỗi phần tử là "grass" | "forest" | "water" | "rock".
    """
    grid = []
    for _r in range(rows):
        row_terrain = []
        for _c in range(cols):
            roll = random.random()
            terrain = "grass"
            threshold = 0.0
            for name, weight in TERRAIN_WEIGHTS:
                threshold += weight
                if roll < threshold:
                    terrain = name
                    break
            row_terrain.append(terrain)
        grid.append(row_terrain)
    return grid
