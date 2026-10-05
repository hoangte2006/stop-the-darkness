"""
File: core/map_generator.py
Nhiệm vụ (TV6): Sinh ma trận địa hình ngẫu nhiên theo chuẩn 4 ảnh mẫu.

Cấu trúc địa hình:
- grass    (Cỏ)
- forest   (Rừng / Cây - Sinh theo cụm)
- water    (Nước / Sông hồ - Sinh theo dải liền)
- rock     (Đá / Núi - RẢI ĐỀU từng ô đơn lẻ khắp map)
- mushroom (Nấm - Đốm nhỏ 1-2 ô)
- ruins    (Phế tích / Vòng đá - Luôn ở ĐÚNG CHÍNH GIỮA map)

Chế độ độ khó (difficulty):
- 1: Chuẩn tỷ lệ theo 4 ảnh mẫu.
- 2: Giảm tỷ lệ chướng ngại vật, tăng diện tích Cỏ.
- 3: Giảm thêm chướng ngại vật, Cỏ chiếm đa số.
"""

import random

try:
    from core.constants import GRID_COLS, GRID_ROWS
except ImportError:
    GRID_ROWS = 12
    GRID_COLS = 12


DIFFICULTY_RATIOS = {
    1: {  # Độ khó 1: Chuẩn theo 4 ảnh mẫu
        "forest": 0.28,
        "water": 0.18,
        "rock": 0.12,
        "mushroom": 0.03,
        "ruins": 0.01,
    },
    2: {  # Độ khó 2: Giảm chướng ngại
        "forest": 0.20,
        "water": 0.13,
        "rock": 0.08,
        "mushroom": 0.02,
        "ruins": 0.01,
    },
    3: {  # Độ khó 3: Giảm thêm chướng ngại
        "forest": 0.12,
        "water": 0.08,
        "rock": 0.05,
        "mushroom": 0.015,
        "ruins": 0.01,
    },
}


def _place_ruins_exact_center(
    grid: list[list[str]],
    ruins_count: int,
    available_cells: set[tuple[int, int]],
    rows: int,
    cols: int,
):
    """Đặt ô Vòng đá / Phế tích (ruins) TẠI ĐÚNG CHÍNH GIỮA TUYỆT ĐỐI BẢN ĐỒ."""
    center_r, center_c = rows // 2, cols // 2

    # Danh sách ưu tiên bắt đầu từ đúng tâm bản đồ, sau đó lan ra 8 ô lân cận nếu ruins_count > 1
    center_candidates = [(center_r, center_c)]
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            center_candidates.append((center_r + dr, center_c + dc))

    placed = 0
    for r, c in center_candidates:
        if placed >= ruins_count:
            break
        if (r, c) in available_cells:
            grid[r][c] = "ruins"
            available_cells.remove((r, c))
            placed += 1


def _scatter_tiles(
    grid: list[list[str]],
    terrain_type: str,
    target_count: int,
    available_cells: set[tuple[int, int]],
):
    """Rải đều địa hình từng ô đơn lẻ ngẫu nhiên khắp map (không tụ cụm)."""
    if target_count <= 0 or not available_cells:
        return

    chosen_cells = random.sample(list(available_cells), min(target_count, len(available_cells)))
    for r, c in chosen_cells:
        grid[r][c] = terrain_type
        available_cells.remove((r, c))


def _grow_cluster(
    grid: list[list[str]],
    terrain_type: str,
    target_count: int,
    available_cells: set[tuple[int, int]],
    min_cluster_size: int = 3,
    max_cluster_size: int = 10,
):
    """Phát triển cụm địa hình dải liền dựa trên Cellular Automata có trọng số."""
    if target_count <= 0 or not available_cells:
        return

    rows, cols = len(grid), len(grid[0])
    placed_count = 0

    while placed_count < target_count and available_cells:
        seed = random.choice(list(available_cells))
        frontier = {seed}
        cluster_placed = 0

        cluster_limit = min(
            target_count - placed_count,
            random.randint(min_cluster_size, max_cluster_size),
        )

        while frontier and cluster_placed < cluster_limit:
            candidates = list(frontier)
            weights = []

            for r, c in candidates:
                same_neighbors = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == terrain_type:
                            same_neighbors += 1

                weights.append((same_neighbors ** 2) + 1)

            chosen = random.choices(candidates, weights=weights, k=1)[0]
            r_chosen, c_chosen = chosen

            grid[r_chosen][c_chosen] = terrain_type
            available_cells.remove(chosen)
            frontier.remove(chosen)

            placed_count += 1
            cluster_placed += 1

            if placed_count >= target_count:
                break

            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r_chosen + dr, c_chosen + dc
                    if (nr, nc) in available_cells:
                        frontier.add((nr, nc))


def generate_map(
    rows: int = GRID_ROWS,
    cols: int = GRID_COLS,
    difficulty: int = 1,
) -> list[list[str]]:
    """
    Sinh ma trận địa hình ngẫu nhiên với tỷ lệ và kiểu phân bổ chuẩn theo 4 ảnh mẫu.
    """
    if difficulty not in DIFFICULTY_RATIOS:
        difficulty = 1

    total_tiles = rows * cols
    ratios = DIFFICULTY_RATIOS[difficulty]

    water_count = max(1, round(total_tiles * ratios["water"]))
    forest_count = max(1, round(total_tiles * ratios["forest"]))
    rock_count = max(1, round(total_tiles * ratios["rock"]))
    mushroom_count = max(1, round(total_tiles * ratios["mushroom"]))
    ruins_count = max(1, round(total_tiles * ratios["ruins"]))

    grid = [["grass" for _ in range(cols)] for _ in range(rows)]
    available_cells = {(r, c) for r in range(rows) for c in range(cols)}

    # 1. Đặt Vòng đá TẠI ĐÚNG CHÍNH GIỮA MAP
    _place_ruins_exact_center(grid, ruins_count, available_cells, rows, cols)

    # 2. Sinh Sông / Nước (Cụm dải liền 8-20 ô)
    _grow_cluster(grid, "water", water_count, available_cells, min_cluster_size=8, max_cluster_size=20)

    # 3. Sinh Rừng / Cây (Cụm dải vừa 3-8 ô)
    _grow_cluster(grid, "forest", forest_count, available_cells, min_cluster_size=3, max_cluster_size=8)

    # 4. Sinh Đá (RẢI ĐỀU ĐƠN LẺ KHẮP MAP - KHÔNG CỤM)
    _scatter_tiles(grid, "rock", rock_count, available_cells)

    # 5. Sinh Nấm (Rải đốm nhỏ 1-2 ô)
    _grow_cluster(grid, "mushroom", mushroom_count, available_cells, min_cluster_size=1, max_cluster_size=2)

    return grid


if __name__ == "__main__":
    SYMBOL_MAP = {
        "grass": " . ",
        "forest": " T ",
        "water": " ~ ",
        "rock": " # ",
        "mushroom": " M ",
        "ruins": " O ",
    }

    rows, cols = 12, 12
    test_map = generate_map(rows, cols, difficulty=1)

    print("=== BẢN ĐỒ KÝ TỰ MA TRẬN 12x12 (DEMO TV6) ===")
    counts = {k: 0 for k in SYMBOL_MAP.keys()}

    # In bản đồ và thống kê đếm số lượng từng ô
    for row in test_map:
        print("".join(SYMBOL_MAP[tile] for tile in row))
        for tile in row:
            if tile in counts:
                counts[tile] += 1

    total_tiles = rows * cols
    print("\n--- THỐNG KÊ TỶ LỆ PHÂN BỔ ĐỊA HÌNH ---")
    for terrain_name, count in counts.items():
        percentage = (count / total_tiles) * 100
        print(f"- {terrain_name.capitalize():<10}: {count:>2} ô ({percentage:.1f}%)")