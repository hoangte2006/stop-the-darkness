"""
File: core/map_generator.py
Nhiệm vụ (TV6): Sinh ma trận địa hình 12x12 ngẫu nhiên dạng cụm liền dải.

Tỷ lệ phân bổ cố định:
- 50% Cỏ (grass)   = 72 ô
- 25% Rừng (forest) = 36 ô
- 15% Nước (water)  = 22 ô
- 10% Đá (rock)    = 14 ô
"""

import random

try:
    from core.constants import GRID_COLS, GRID_ROWS
except ImportError:
    GRID_ROWS = 12
    GRID_COLS = 12


def _grow_cluster(
    grid: list[list[str]],
    terrain_type: str,
    target_count: int,
    available_cells: set[tuple[int, int]],
):
    """
    HÀM HỖ TRỢ: Phát triển cụm địa hình theo quy tắc lân cận của Cellular Automata.

    ===========================================================================
    GIẢI THÍCH THUẬT TOÁN GOM CỤM ĐẠT TỶ LỆ CHÍNH XÁC (DÙNG CHO BÁO CÁO TV6):
    ---------------------------------------------------------------------------
    1. Khởi tạo Hạt giống (Seed):
       - Chọn ngẫu nhiên 1 ô trống ban đầu làm tâm cho cụm địa hình.

    2. Mở rộng biên theo Trọng số Lân cận (CA Weighted Region Growing):
       - Duyệt các ô biên xung quanh cụm địa hình hiện tại (Frontier).
       - Đếm số ô cùng loại địa hình xung quanh mỗi ô biên (8-Moore Neighborhood).
       - Ô biên nào có NÊN NHIỀU Ô CÙNG LOẠI XUNG QUANH sẽ có xác suất được chọn
         cao hơn (Trọng số w = (neighbors)^2 + 1).

    3. Đảm bảo Quota tỷ lệ:
       - Thuật toán dừng lại ngay khi số ô đặt được đạt ĐÚNG target_count.
       - Vừa đảm bảo mảng liền dải tự nhiên vừa đạt chính xác 100% tỷ lệ.
    ===========================================================================
    """
    if target_count <= 0 or not available_cells:
        return

    rows, cols = len(grid), len(grid[0])
    placed_count = 0

    while placed_count < target_count and available_cells:
        # Chọn hạt giống ngẫu nhiên để bắt đầu cụm mới
        seed = random.choice(list(available_cells))
        frontier = {seed}
        cluster_placed = 0

        # Kích thước cụm tối đa mỗi lần loang (để tạo nhiều cụm nhỏ tự nhiên thay vì 1 cụm khổng lồ)
        max_cluster_size = min(target_count - placed_count, random.randint(8, 18))

        while frontier and cluster_placed < max_cluster_size:
            candidates = list(frontier)
            weights = []

            # Tính trọng số Cellular Automata cho từng ô biên
            for r, c in candidates:
                same_neighbors = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == terrain_type:
                            same_neighbors += 1
                # Ô càng có nhiều lân cận cùng loại thì xác suất được chọn càng cao
                weights.append((same_neighbors ** 2) + 1)

            # Chọn ô tiếp theo theo trọng số
            chosen = random.choices(candidates, weights=weights, k=1)[0]

            # Đặt loại địa hình
            r_chosen, c_chosen = chosen
            grid[r_chosen][c_chosen] = terrain_type
            available_cells.remove(chosen)
            frontier.remove(chosen)

            placed_count += 1
            cluster_placed += 1

            if placed_count >= target_count:
                break

            # Cập nhật ô lân cận mới vào Frontier
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r_chosen + dr, c_chosen + dc
                    if (nr, nc) in available_cells:
                        frontier.add((nr, nc))


def generate_map(rows: int = GRID_ROWS, cols: int = GRID_COLS) -> list[list[str]]:
    """
    Sinh ma trận địa hình ngẫu nhiên dạng cụm với tỷ lệ chuẩn cố định.

    Trả về: list[list[str]] chứa các ô "grass" | "forest" | "water" | "rock".
    """
    total_tiles = rows * cols

    # Tính toán chính xác số ô cho từng loại địa hình theo tỷ lệ yêu cầu
    forest_count = round(total_tiles * 0.25)  # 25%
    water_count = round(total_tiles * 0.15)   # 15%
    rock_count = round(total_tiles * 0.10)    # 10%

    # Khởi tạo ma trận mặc định toàn Cỏ (grass chiếm ~50% phần còn lại)
    grid = [["grass" for _ in range(cols)] for _ in range(rows)]
    available_cells = {(r, c) for r in range(rows) for c in range(cols)}

    # Lần lượt phát triển các cụm Rừng, Nước, Đá
    _grow_cluster(grid, "forest", forest_count, available_cells)
    _grow_cluster(grid, "water", water_count, available_cells)
    _grow_cluster(grid, "rock", rock_count, available_cells)

    return grid


if __name__ == "__main__":
    # Demo chạy trực tiếp kiểm tra bản đồ và tỷ lệ
    SYMBOL_MAP = {
        "grass": " . ",
        "forest": " T ",
        "water": " ~ ",
        "rock": " # ",
    }

    test_map = generate_map(12, 12)

    print("=== BẢN ĐỒ KÝ TỰ MA TRẬN 12x12 (DEMO TV6) ===")
    counts = {"grass": 0, "forest": 0, "water": 0, "rock": 0}

    for row in test_map:
        print("".join(SYMBOL_MAP[tile] for tile in row))
        for tile in row:
            counts[tile] += 1

    total_tiles = 12 * 12
    print("\n--- THỐNG KÊ TỶ LỆ PHÂN BỔ ĐỊA HÌNH ---")
    for terrain_name, count in counts.items():
        percentage = (count / total_tiles) * 100
        print(f"- {terrain_name.capitalize():<8}: {count:>2} ô ({percentage:.1f}%)")