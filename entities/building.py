"""Building entity classes: base Building plus Woodcutter, Quarry, TowerOfLight.

Ở bước khung, các class con chỉ khai thuộc tính (giá, sản lượng, tên hiển thị)
để TV3 (sidebar) và TV1 (game_state) dùng ngay. Luật xây dựng chi tiết (ô kề,
nâng cấp...) sẽ bổ sung sau, không chặn các thành viên khác.
"""

from entities.base import Entity


class Building(Entity):
    """Class cha cho mọi công trình xây trên 1 Tile."""

    key = "building"          # ID định danh dùng để lưu/tải file, vd "woodcutter"
    name = "Building"         # Tên hiển thị trên UI
    base_cost = {}            # Giá xây ban đầu (level 1), vd {"wood": 30}
    cost_multiplier = 2.0     # Giá nâng cấp cấp thứ n = giá gốc x hệ_số^(n-2): Lv2 = giá gốc, Lv3 = gấp 2
    base_produces = {}        # Sản lượng ở level 1, vd {"wood": 2}
    icon_key = "default"      # Tên sprite trong renderer
    max_level = 3
    boost_terrain = None     # địa hình kề giúp tăng sản lượng, vd "forest". None = không có buff
    boost_per_tile = 0.0     # mỗi ô kề đúng địa hình cộng thêm bao nhiêu % sản lượng
    build_terrain = None     # địa hình BẮT BUỘC để xây được, vd "forest". None = xây đâu cũng được
    buildable = True         # False = có sẵn từ đầu game, người chơi không tự xây được
    build_cost_step = {}     # mỗi công trình CÙNG LOẠI đã xây làm giá xây tăng thêm bấy nhiêu, vd {"wood": 1}: 5, 6, 7...
    upgrade_base_cost = None # giá nâng lên Lv2 (None = dùng base_cost); Lv3 nhân thêm cost_multiplier

    def __init__(self, row, col):
        super().__init__(entity_id=f"{self.key}_{row}_{col}", row=row, col=col)
        self.level = 1

    @property
    def produces(self):
        """Sản lượng thực tế hiện tại, tăng theo level."""
        result = {}
        for res, amount in self.base_produces.items():
            result[res] = amount * self.level
        return result # trả về dict chứa sản lượng thực tế theo level : vd: {"wood": 2} -> level 1, {"wood": 4} -> level 2, {"wood": 6} -> level 3

    def cost_for_next_level(self):
        """Giá cần trả để nâng từ level hiện tại lên level + 1."""
        factor = self.cost_multiplier ** (self.level - 1) # ví dụ level 1 -> 2: x1.5, level 2 -> 3: x1.5^2 = x2.25
        result = {}
        base = self.upgrade_base_cost or self.base_cost
        for res, amount in base.items():
            result[res] = round(amount * factor) # round để tránh số lẻ, ví dụ 10 * 1.5 = 15, nhưng 10 * 1.5^2 = 22.5 -> round thành 23
        return result

    # Nâng cấp công trình: trừ tài nguyên và tăng level nếu đủ tiền, chưa đạt max_level.
    def upgrade(self, resources):
        """Trừ resources và tăng level nếu đủ tiền, chưa đạt max_level."""
        if self.level >= self.max_level:
            return False

        cost = self.cost_for_next_level()

        enough = True
        for res, amount in cost.items(): # vd cost = {"wood": 30, "stone": 10}
            have = resources.get(res, 0) # tui đang có bao nhiêu res đó vd: resources = {"wood": 50, "stone": 5} -> have = 5
            if have < amount: # không đủ 1 loại là fail luôn vd: 5 < 10 -> enough = False
                enough = False
                break
        if not enough:
            return False

        # Trừ tài nguyên và nâng level 
        for res, amount in cost.items(): 
            resources[res] -= amount
        self.level += 1
        return True

    # Chuyển Building thành dict thuần để TV4 lưu ra JSON.
    def to_dict(self):
        return {"key": self.key, "row": self.row, "col": self.col, "level": self.level}



class Woodcutter(Building):
    key = "woodcutter"
    name = "Nhà đốn gỗ"
    base_cost = {"wood": 5}
    build_cost_step = {"wood": 1}                 # nhà gỗ thứ 1: 5 gỗ, thứ 2: 6, thứ 3: 7...
    upgrade_base_cost = {"wood": 5, "stone": 2}   # nâng Lv2; Lv3 gấp đôi
    base_produces = {"wood": 10}  # mỗi PHÚT ở level 1
    icon_key = "woodcutter"
    boost_terrain = "forest"
    boost_per_tile = 0.20
    build_terrain = "forest"      # chỉ xây được TRÊN ô rừng


class Quarry(Building):
    key = "quarry"
    name = "Mỏ đá"
    base_cost = {"wood": 15}
    build_cost_step = {"wood": 3}
    upgrade_base_cost = {"wood": 15, "stone": 5}
    base_produces = {"stone": 4}  # mỗi PHÚT ở level 1
    icon_key = "quarry"
    boost_terrain = "rock"
    boost_per_tile = 0.25
    build_terrain = "rock"        # chỉ xây được TRÊN ô đá


class TowerOfLight(Building):
    key = "tower_of_light"
    name = "Tháp ánh sáng"
    base_cost = {"wood": 25, "light": 15}   # light = mana
    build_cost_step = {"wood": 10}
    upgrade_base_cost = {"wood": 25, "light": 15, "stone": 10}
    cost_multiplier = 8                    # nâng Lv2 = giá gốc, nâng Lv3 = gấp 8 (tổng xây+nâng ~250 gỗ + 150 mana)
    base_produces = {"light": 1.5}          # mỗi PHÚT ở level 1
    slow_per_level = 0.35                   # mỗi cấp tháp kéo dài thêm 35% thời gian giữa 2 lần bóng tối lan
    icon_key = "tower_of_light"
    build_terrain = "grass"       # chỉ xây được trên đất bằng


class MushroomHut(Building):
    key = "mushroom_hut"
    name = "Nhà nấm"
    base_cost = {"wood": 20, "stone": 5}
    build_cost_step = {"wood": 3, "stone": 1}
    upgrade_base_cost = {"wood": 20, "stone": 9}
    base_produces = {"light": 6}  # mana, mỗi PHÚT ở level 1
    icon_key = "mushroom"
    build_terrain = "mushroom"    # chỉ xây được TRÊN ô nấm


class StoneCircle(Building):
    key = "stone_circle"
    name = "Vòng tròn đá"
    base_cost = {"stone": 100, "light": 100}  # giá nâng lên Lv2 (hệ số cấp 1 = 1) -> nâng được là thắng
    base_produces = {}
    icon_key = "stone_circle"
    max_level = 2
    build_terrain = "grass"
    buildable = False             # có sẵn ở tâm bản đồ, không xây thêm được

class StoneCircle(Building):
    key = "stone_circle"
    name = "Vòng tròn đá"
    base_cost = {"stone": 10}
    base_produces = {}
    icon_key = "stone_circle"
    max_level = 2

# Registry để tra class theo `key` (dùng khi xây công trình mới hoặc load save file).
BUILDING_TYPES = {
    Woodcutter.key: Woodcutter,
    Quarry.key: Quarry,
    MushroomHut.key: MushroomHut,
    TowerOfLight.key: TowerOfLight,
    StoneCircle.key: StoneCircle,
}
