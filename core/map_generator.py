"""
File: core/map_generator.py
Nhiệm vụ (TV6): Sinh ma trận địa hình ngẫu nhiên theo chuẩn 4 ảnh mẫu và các ràng buộc độ khó.

Cấu trúc địa hình:
- grass    (Cỏ / Đất bằng để xây tháp)
- forest   (Rừng / Cây - Sinh theo cụm, tối thiểu 6 ô)
- water    (Nước / Sông hồ - Sinh theo dải liền chắn đường, tối thiểu 6 ô)
- rock     (Đá / Núi - Rải đều, ở độ khó cao có xu hướng xuất hiện ở vùng xa tâm nhiều hơn, tối thiểu 12 ô)
- mushroom (Nấm - Đốm nhỏ 1-2 ô, tối thiểu 4 ô nguồn mana)
- ruins    (Phế tích / Vòng đá - Luôn ở ĐÚNG CHÍNH GIỮA map)

Chế độ độ khó (difficulty):
- 1: Chuẩn tỷ lệ mẫu, bố cục cân bằng.
- 2 & 3: Tăng tỷ lệ xuất hiện tài nguyên/chướng ngại vật ở xa tâm bằng trọng số xác suất thay vì gom hết ra biên.
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
    2: {  # Độ khó 2
        "forest": 0.22,
        "water": 0.15,
        "rock": 0.10,
        "mushroom": 0.025,
        "ruins": 0.01,
    },
    3: {  # Độ khó 3
        "forest": 0.18,
        "water": 0.12,
        "rock": 0.09,
        "mushroom": 0.02,
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
    difficulty: int = 1,
):
    """Rải đều địa hình dựa trên trọng số khoảng cách (ở độ khó cao, ô xa tâm có xác suất cao hơn nhưng không bị dồn hết ra biên)."""
    if target_count <= 0 or not available_cells:
        return

    cells_list = list(available_cells)
    
    if difficulty == 1:
        # Độ khó 1: Chọn ngẫu nhiên đều khắp map
        chosen_cells = random.sample(cells_list, min(target_count, len(cells_list)))
    else:
        # Độ khó 2 & 3: Dùng trọng số xác suất theo khoảng cách từ tâm
        center_r, center_c = len(grid) // 2, len(grid[0]) // 2
        temp_cells = list(cells_list)
        
        # Mũ lũy thừa điều chỉnh độ ưu tiên vùng xa tâm (difficulty 2 vừa phải, difficulty 3 cao hơn)
        power = 1.5 if difficulty == 2 else 2.5
        temp_weights = [(abs(r - center_r) + abs(c - center_c) + 1.0) ** power for r, c in temp_cells]
        
        chosen_cells = []
        for _ in range(min(target_count, len(temp_cells))):
            chosen = random.choices(temp_cells, weights=temp_weights, k=1)[0]
            idx = temp_cells.index(chosen)
            chosen_cells.append(chosen)
            temp_cells.pop(idx)
            temp_weights.pop(idx)

    for r, c in chosen_cells:
        grid[r][c] = terrain_type
        if (r, c) in available_cells:
            available_cells.remove((r, c))


def _grow_cluster(
    grid: list[list[str]],
    terrain_type: str,
    target_count: int,
    available_cells: set[tuple[int, int]],
    min_cluster_size: int = 3,
    max_cluster_size: int = 10,
    difficulty: int = 1,
):
    """Phát triển cụm địa hình (Cellular Automata)."""
    if target_count <= 0 or not available_cells:
        return

    rows, cols = len(grid), len(grid[0])
    placed_count = 0

    if difficulty >= 2 and terrain_type == "water":
        min_cluster_size += 2
        max_cluster_size += 4

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
    Sinh ma trận địa hình ngẫu nhiên với các ràng buộc tối thiểu và phân bổ theo độ khó.
    """
    if difficulty not in DIFFICULTY_RATIOS:
        difficulty = 1

    total_tiles = rows * cols
    ratios = DIFFICULTY_RATIOS[difficulty]

    water_count = max(6, round(total_tiles * ratios["water"]))
    forest_count = max(6, round(total_tiles * ratios["forest"]))
    rock_count = max(12, round(total_tiles * ratios["rock"]))
    mushroom_count = max(4, round(total_tiles * ratios["mushroom"]))
    ruins_count = 1

    grid = [["grass" for _ in range(cols)] for _ in range(rows)]
    available_cells = {(r, c) for r in range(rows) for c in range(cols)}

    # 1. Đặt Vòng đá TẠI ĐÚNG CHÍNH GIỮA MAP
    _place_ruins_exact_center(grid, ruins_count, available_cells, rows, cols)

    # 2. Sinh Sông / Nước (Cụm dải liền)
    _grow_cluster(grid, "water", water_count, available_cells, min_cluster_size=8, max_cluster_size=20, difficulty=difficulty)

    # 3. Sinh Rừng / Cây (Cụm dải vừa)
    _grow_cluster(grid, "forest", forest_count, available_cells, min_cluster_size=3, max_cluster_size=8, difficulty=difficulty)

    # 4. Sinh Đá (Rải đều theo xác suất khoảng cách tâm)
    _scatter_tiles(grid, "rock", rock_count, available_cells, difficulty=difficulty)

    # 5. Sinh Nấm (Đốm nhỏ 1-2 ô)
    _grow_cluster(grid, "mushroom", mushroom_count, available_cells, min_cluster_size=1, max_cluster_size=2, difficulty=difficulty)

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
    for diff in [1, 2, 3]:
        print(f"\n=== DEMO BẢN ĐỒ ĐỘ KHÓ {diff} (TV6) ===")
        test_map = generate_map(rows, cols, difficulty=diff)
        counts = {k: 0 for k in SYMBOL_MAP.keys()}

        for row in test_map:
            print("".join(SYMBOL_MAP[tile] for tile in row))
            for tile in row:
                if tile in counts:
                    counts[tile] += 1

        total_tiles = rows * cols
        print(f"--- THỐNG KÊ TỶ LỆ (Độ khó {diff}) ---")
        for terrain_name, count in counts.items():
            percentage = (count / total_tiles) * 100
            print(f"- {terrain_name.capitalize():<10}: {count:>2} ô ({percentage:.1f}%)")