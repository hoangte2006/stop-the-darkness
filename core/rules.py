"""Game rules: darkness propagation and adjacency checks.

TODO (TV1): thay spread_darkness() dưới đây (lan ngẫu nhiên 1 ô/nhịp) bằng
BFS thật (loang đều theo từng lớp quanh mọi ô tối, có thể bị chặn hẳn bởi
Tháp Ánh Sáng) và bổ sung luật xây dựng theo ô kề (is_adjacent_to) cho
Woodcutter cạnh rừng, Quarry cạnh đá...
"""

import random

from entities.building import TowerOfLight


def spread_darkness(grid):
    """Lan bóng tối thêm 1 ô (thuật toán tạm, sẽ thay bằng BFS thật)."""
    dark_tiles = [tile for row in grid for tile in row if tile.is_dark]
    if not dark_tiles:
        return

    rows, cols = len(grid), len(grid[0])
    source = random.choice(dark_tiles)
    neighbors = [
        (source.row - 1, source.col),
        (source.row + 1, source.col),
        (source.row, source.col - 1),
        (source.row, source.col + 1),
    ]
    for nr, nc in neighbors:
        if 0 <= nr < rows and 0 <= nc < cols:
            target = grid[nr][nc]
            if not target.is_dark and not isinstance(target.building, TowerOfLight):
                target.is_dark = True
                break


def is_adjacent_to(grid, row, col, terrain):
    """Kiểm tra 4 ô kề (row, col) có ô nào thuộc loại địa hình `terrain` không."""
    rows, cols = len(grid), len(grid[0])
    for nr, nc in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc].terrain == terrain:
            return True
    return False
