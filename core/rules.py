"""Game rules: darkness propagation and adjacency checks.

TODO (TV1): thay spread_darkness() dưới đây (lan ngẫu nhiên 1 ô/nhịp) bằng
BFS thật (loang đều theo từng lớp quanh mọi ô tối, có thể bị chặn hẳn bởi
Tháp Ánh Sáng) và bổ sung luật xây dựng theo ô kề (is_adjacent_to) cho
Woodcutter cạnh rừng, Quarry cạnh đá...
"""

import random

from entities.building import TowerOfLight
from core.constants import GRID_ROWS, GRID_COLS


def build_spiral_order(rows, cols):
    """Tính thứ tự 144 ô: tu goc duoi-trai, vong het mep ngoai, roi thu dan vao tam."""
    order = []
    top = 0
    bottom = rows - 1
    left = 0
    right = cols - 1

    while top <= bottom and left <= right:
        # canh duoi: tu (bottom, left) sang phai toi (bottom, right)
        for c in range(left, right + 1):
            order.append((bottom, c))

        # canh phai: tu duoi len tren toi (top, right)
        for r in range(bottom - 1, top - 1, -1):
            order.append((r, right))

        if top < bottom:
            # canh tren: tu phai sang trai toi (top, left)
            for c in range(right - 1, left - 1, -1):
                order.append((top, c))

        if left < right:
            # canh trai: tu tren xuong duoi, khong lay lai 2 goc da di qua
            for r in range(top + 1, bottom):
                order.append((r, left))

        top += 1
        bottom -= 1
        left += 1
        right -= 1

    return order

_SPIRAL_ORDER = build_spiral_order(GRID_ROWS, GRID_COLS)   # tinh 1 lan, dung mai
_progress = 0   # da di toi o thu bao nhieu trong _SPIRAL_ORDER


def spread_darkness(grid):
    """Toi dan 1 o theo dung thu tu vong xoay da tinh san trong _SPIRAL_ORDER."""
    global _progress

    if _progress >= len(_SPIRAL_ORDER):
        return   # da toi het toan bo ban do, khong con o nao de toi nua

    row, col = _SPIRAL_ORDER[_progress]
    tile = grid[row][col] 
    if not tile.is_lighted:
        tile.is_dark = True

    _progress += 1

def get_darkness_progress():
    """Lấy tiến trình lan bóng tối hiện tại."""
    return _progress


def set_darkness_progress(progress):
    """Khôi phục tiến trình lan bóng tối."""
    global _progress

    if not isinstance(progress, int) or not 0 <= progress <= len(_SPIRAL_ORDER):
        raise ValueError("Tiến trình bóng tối không hợp lệ")

    _progress = progress


def is_adjacent_to(grid, row, col, terrain):
    """Kiểm tra 4 ô kề (row, col) có ô nào thuộc loại địa hình `terrain` không."""
    rows, cols = len(grid), len(grid[0])
    for nr, nc in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc].terrain == terrain:
            return True
    return False


def count_adjacent_terrain(grid, row, col, terrain):
    """Đếm trong 4 ô kề (row, col) có bao nhiêu ô thuộc địa hình `terrain`."""
    rows, cols = len(grid), len(grid[0])
    count = 0
    for nr, nc in ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)):
        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc].terrain == terrain:
            count += 1
    return count


# hàm update_light() được chuyển sang core/rules.py để tách riêng luật game khỏi trạng thái game.
# nhiệm vụ của hàm này là cập nhật trạng thái is_lighted của các ô dựa trên Tháp Ánh Sáng.
def update_light(grid):
    """Cập nhật trạng thái is_lighted của các ô dựa trên Tháp Ánh Sáng."""
    rows, cols = len(grid), len(grid[0]) 
    for r in range(rows):
        for c in range(cols):
            tile = grid[r][c]

            tile.is_lighted = isinstance(tile.building, TowerOfLight) 
            if not tile.is_lighted:
            
                for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)): 
                    if 0 <= nr < rows and 0 <= nc < cols:
                        neighbor_tile = grid[nr][nc]
                        if isinstance(neighbor_tile.building, TowerOfLight):
                            tile.is_lighted = True
                            break


def is_darkness_finished():
    """Bong toi da lan het toan bo vong xoay (khong con o nao de lan tiep)."""
    global _progress
    return _progress >= len(_SPIRAL_ORDER)
