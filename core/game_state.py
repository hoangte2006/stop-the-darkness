"""Central game state: resources, grid of tiles, buildings, and game clock.

File này là "hợp đồng giao tiếp" (interface) dùng chung cho cả team — xem
docs/interfaces.md để biết chi tiết chữ ký từng hàm. Không sửa file này nếu
không phải Leader; báo Leader nếu cần thêm dữ liệu/hàm mới.
"""

from core import rules
from core.constants import GRID_COLS, GRID_ROWS
from core.map_generator import generate_map
from entities.building import BUILDING_TYPES, StoneCircle, TowerOfLight
from entities.tile import Tile


class GameState:
    def __init__(self):
        rules.reset_darkness()

        # 1. Kho tài nguyên người chơi
        self.resources = {"wood": 20, "stone": 0, "tech": 0, "light": 0}
        self._carry = {}   # phần lẻ chưa đủ 1 đơn vị của từng tài nguyên
        self._dark_charge = 0.0   # "sức chứa" bóng tối: đủ 1 thì lan thêm 1 ô, tháp làm nó đầy chậm lại

        # 2. Trạng thái UI dùng chung
        self.is_paused = False
        self.game_over = False
        self.game_won = False

        self.selected_tile = None
        self.speed_multiplier = 1  # 1x/2x/3x, đổi qua set_speed()

        # 3. Sinh bản đồ địa hình (TV6 đã thay code)
        while True:
            terrain_map = generate_map(GRID_ROWS, GRID_COLS)
            flat = [t for row in terrain_map for t in row]
            if all(flat.count(t) >= 6 for t in ("forest", "rock", "water")):
                break

        mid_r, mid_c = GRID_ROWS // 2, GRID_COLS // 2
        terrain_map[mid_r][mid_c] = "grass"
        self.grid = []

        for r in range(GRID_ROWS):
            row_tiles = []
            for c in range(GRID_COLS):
                terrain = terrain_map[r][c]
                row_tiles.append(Tile(r, c, terrain))
            self.grid.append(row_tiles)

        self.grid[mid_r][mid_c].building = StoneCircle(mid_r, mid_c)

        # Không tự gán is_dark ở đây nữa — spread_darkness() tự tối dần từ góc
        # dưới-trái theo _SPIRAL_ORDER ngay từ nhịp gọi đầu tiên (core/rules.py).

    # get_tile làm
    def get_tile(self, row, col):
        """Trả về Tile tại (row, col), hoặc None nếu ngoài bàn cờ."""
        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return self.grid[row][col]
        return None

    def build_cost(self, building_key):
        building_cls = BUILDING_TYPES[building_key]
        owned = 0
        for row in self.grid:                     
            for tile in row:                        
                if isinstance(tile.building, building_cls):  
                    owned = owned + 1
        cost = {}
        
        for res, amount in building_cls.base_cost.items():
            cost[res] = amount 

        for res, step in building_cls.build_cost_step.items():
            if res not in cost:                    
                cost[res] = 0
            cost[res] = cost[res] + step * owned

        return cost


    def production_per_minute(self, building_cls, row, col, level=1):
        """Sản lượng mỗi PHÚT của công trình `building_cls` ở cấp `level` tại (row, col), đã tính buff ô kề."""
        multiplier = 1.0
        if building_cls.boost_terrain:
            adjacent = rules.count_adjacent_terrain(self.grid, row, col, building_cls.boost_terrain)
            multiplier += adjacent * building_cls.boost_per_tile
        return {res: amount * level * multiplier for res, amount in building_cls.base_produces.items()}

    def add_building(self, row, col, building_key):
        """Đặt công trình `building_key` (vd "woodcutter") tại (row, col).

        Trả về True nếu đặt thành công, False nếu ô không hợp lệ, đã có công
        trình, đang bị bóng tối, hoặc không đủ tài nguyên.
        """
        tile = self.get_tile(row, col)
        building_cls = BUILDING_TYPES.get(building_key) 
        if tile is None or building_cls is None:
            return False
        if not building_cls.buildable:
            return False
        if building_cls.build_terrain is not None and tile.terrain != building_cls.build_terrain:
            return False
        if tile.is_dark or tile.building is not None:
            return False

        cost = self.build_cost(building_key)
        enough = True
        for res, amount in cost.items():
            have = self.resources.get(res, 0)
            if have < amount:
                enough = False
                break
        if not enough:
            return False

        for res, amount in cost.items():
            self.resources[res] -= amount

        tile.building = building_cls(row, col)
        return True

    def upgrade_building(self, row, col):
        """Nâng cấp công trình tại (row, col). Trả về True nếu thành công."""
        tile = self.get_tile(row, col)
        if tile is None or tile.building is None or tile.is_dark:
            return False
        upgraded = tile.building.upgrade(self.resources)
        if upgraded:
            self._check_win_condition()
        return upgraded

    def remove_building(self, row, col):
        """Phá bỏ công trình tại (row, col). Trả về True nếu có công trình để phá."""
        tile = self.get_tile(row, col)
        if tile is None or tile.building is None or not tile.building.buildable:
            return False
        tile.building = None
        return True

    def set_speed(self, multiplier):
        """Đặt tốc độ mô phỏng (1, 2, 3...). Ảnh hưởng tick_resources() và spread_darkness()."""
        self.speed_multiplier = multiplier

    def update_light(self):
        """Cập nhật trạng thái is_lighted của các ô dựa trên Tháp Ánh Sáng."""
        rules.update_light(self.grid)

        
    def tick_resources(self):
        """Cộng tài nguyên mỗi giây dựa trên các công trình đang hoạt động (chưa bị bóng tối)."""
        if self.is_paused:
            return

        for r, row in enumerate(self.grid):
            for c, tile in enumerate(row):
                if tile.building is not None and not tile.is_dark:
                    building = tile.building
                    bonus_multiplier = 1.0
                    if building.boost_terrain:
                        adjacent_count = rules.count_adjacent_terrain(self.grid, r, c, building.boost_terrain)
                        bonus_multiplier += adjacent_count * building.boost_per_tile
                    for res, amount in building.produces.items():
                        gained = self._carry.get(res, 0.0) + amount / 60 * bonus_multiplier
                        whole = int(gained) 
                        self._carry[res] = gained - whole
                        self.resources[res] = self.resources.get(res, 0) + whole

        self._check_win_condition()


    def spread_darkness(self):
        """Lan bóng tối thêm 1 ô. Tốc độ nhanh/chậm do main.py tự rút ngắn/kéo dài nhịp gọi."""
        if self.is_paused:
            return
        self._dark_charge += 1 / (1 + self.darkness_slowdown()) 
        if self._dark_charge >= 1:
            self._dark_charge -= 1
            rules.spread_darkness(self.grid)
        self._check_game_over()

    def darkness_slowdown(self):
        """Tổng độ làm chậm bóng tối của các Tháp Ánh Sáng còn sống (ô chưa bị tối), tăng theo cấp tháp."""
        total = 0.0
        for row in self.grid:
            for tile in row:
                if isinstance(tile.building, TowerOfLight) and not tile.is_dark:
                    total += TowerOfLight.slow_per_level * tile.building.level
        return total

    def _check_game_over(self):
        """Kiểm tra thua: bóng tối đã lan hết mức có thể (đã duyệt hết bản đồ)."""
        if rules.is_darkness_finished():
            self.game_over = True

    def _check_win_condition(self):
        """Kiểm tra thắng: Vòng Tròn Đá lên level 2, hoặc một Tháp Ánh Sáng lên cấp tối đa."""
        for row in self.grid:
            for tile in row:
                building = tile.building
                if isinstance(building, StoneCircle) and building.level >= building.max_level:
                    self.game_won = True
                elif isinstance(building, TowerOfLight) and building.level >= building.max_level:
                    self.game_won = True



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
            "game_won": self.game_won,
            "dark_progress": rules.get_darkness_progress(),
        }

    def load_from_dict(self, data):
        self.resources = {res: int(amount) for res, amount in data["resources"].items()}
        self._carry = {}
        self._dark_charge = 0.0
        self.game_over = data.get("game_over", False)
        self.game_won = data.get("game_won", False)
        for r, row in enumerate(data["grid"]):
            for c, tile_data in enumerate(row):
                tile = self.grid[r][c]
                tile.terrain = tile_data["terrain"] 
                tile.is_dark = tile_data["is_dark"]
                tile.is_lighted = tile_data["is_lighted"]

                building_data = tile_data["building"]
                if building_data:  
                    building_cls = BUILDING_TYPES[building_data["key"]] 
                    new_building = building_cls(r, c)
                    new_building.level = building_data["level"]
                    tile.building = new_building
                else:
                    tile.building = None

        # Save cũ không có dark_progress: ước lượng bằng số ô đã tối
        dark_count = sum(tile.is_dark for row in self.grid for tile in row) # tính số ô đã tối
        rules.set_darkness_progress(data.get("dark_progress", dark_count)) # khôi phục tiến độ bóng tối
