"""Central game state: resources, grid of tiles, buildings, and game clock.

File này là "hợp đồng giao tiếp" (interface) dùng chung cho cả team — xem
docs/interfaces.md để biết chi tiết chữ ký từng hàm. Không sửa file này nếu
không phải Leader; báo Leader nếu cần thêm dữ liệu/hàm mới.
"""

from core import rules
from core.constants import GRID_COLS, GRID_ROWS
from core.map_generator import generate_map
from entities.building import BUILDING_TYPES
from entities.tile import Tile


class GameState:
    def __init__(self):
        # 1. Kho tài nguyên người chơi
        self.resources = {"wood": 12, "stone": 0, "tech": 0, "light": 0}

        # 2. Trạng thái UI dùng chung
        self.is_paused = False
        self.game_over = False
        self.selected_tile = None

        # 3. Sinh bản đồ địa hình (TV6 đã thay code)
        terrain_map = generate_map(GRID_ROWS, GRID_COLS)
        self.grid = []
        for r in range(GRID_ROWS):
            row_tiles = []
            for c in range(GRID_COLS):
                terrain = terrain_map[r][c]
                row_tiles.append(Tile(r, c, terrain))
            self.grid.append(row_tiles)

        # 4. Góc bóng tối khởi điểm (dưới-trái)
        self.grid[GRID_ROWS - 1][0].is_dark = True
        self.grid[GRID_ROWS - 2][0].is_dark = True
        self.grid[GRID_ROWS - 1][1].is_dark = True

    # get_tile làm 
    def get_tile(self, row, col):
        """Trả về Tile tại (row, col), hoặc None nếu ngoài bàn cờ."""
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return self.grid[row][col]
        return None

    def add_building(self, row, col, building_key):
        """Đặt công trình `building_key` (vd "woodcutter") tại (row, col).

        Trả về True nếu đặt thành công, False nếu ô không hợp lệ, đã có công
        trình, đang bị bóng tối, hoặc không đủ tài nguyên.
        """
        tile = self.get_tile(row, col)
        building_cls = BUILDING_TYPES.get(building_key)
        if tile is None or building_cls is None:
            return False
        if tile.is_dark or tile.building is not None:
            return False

        enough = True
        for res, amount in building_cls.base_cost.items():
            have = self.resources.get(res, 0)
            if have < amount:
                enough = False
                break
        if not enough:
            return False

        for res, amount in building_cls.base_cost.items():
            self.resources[res] -= amount

        tile.building = building_cls(row, col)
        return True

    def upgrade_building(self, row, col):
        """Nâng cấp công trình tại (row, col). Trả về True nếu thành công."""
        tile = self.get_tile(row, col)
        if tile is None or tile.building is None:
            return False
        return tile.building.upgrade(self.resources)

    def update_light(self):
        """Cập nhật trạng thái is_lighted của các ô dựa trên Tháp Ánh Sáng."""
        rules.update_light(self.grid)
        
    def tick_resources(self):
        """Cộng tài nguyên mỗi giây dựa trên các công trình đang hoạt động (chưa bị bóng tối)."""
        if self.is_paused:
            return
        for row in self.grid:
            for tile in row:
                if tile.building is not None and not tile.is_dark: 
                    for res, amount in tile.building.produces.items():
                        self.resources[res] = self.resources.get(res, 0) + amount

    def spread_darkness(self):
        """Lan bóng tối thêm 1 nhịp. trong core/rules.py."""
        if self.is_paused:
            return
        rules.spread_darkness(self.grid)
        self._check_game_over()

    def _check_game_over(self):
        """Kiểm tra thua: bóng tối đã lan hết mức có thể (đã duyệt hết bản đồ)."""
        if rules.is_darkness_finished():
            self.game_over = True


    def to_dict(self):
        """Chuyển toàn bộ trạng thái game thành dict thuần (JSON-serializable) cho TV4 lưu file."""
        grid_data = []
        for row in self.grid:
            row_data = []
            for tile in row:
                row_data.append(tile.to_dict())
            grid_data.append(row_data)

        return {
            "resources": dict(self.resources),
            "grid": grid_data,
            "game_over": self.game_over,
        }

    def load_from_dict(self, data):
        """Nạp lại trạng thái game từ dict do TV4 đọc từ file JSON (đảo ngược của to_dict)."""
        self.resources = dict(data["resources"])
        for r, row in enumerate(data["grid"]):
            for c, tile_data in enumerate(row):
                tile = self.grid[r][c]
                tile.terrain = tile_data["terrain"]
                tile.is_dark = tile_data["is_dark"]
                tile.is_lighted = tile_data["is_lighted"]
                building_key = tile_data["building"]
                tile.building = BUILDING_TYPES[building_key](r, c) if building_key else None
