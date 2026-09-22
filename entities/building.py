"""Building entity classes: base Building plus Woodcutter, Quarry, TowerOfLight.

Ở bước khung, các class con chỉ khai thuộc tính (giá, sản lượng, tên hiển thị)
để TV3 (sidebar) và TV1 (game_state) dùng ngay. Luật xây dựng chi tiết (ô kề,
nâng cấp...) sẽ bổ sung sau, không chặn các thành viên khác.
"""

from entities.base import Entity


class Building(Entity):
    """Class cha cho mọi công trình xây trên 1 Tile."""

    key = "building"        # ID định danh dùng để lưu/tải file, vd "woodcutter"
    name = "Building"       # Tên hiển thị trên UI
    cost = {}                # vd {"wood": 30}
    produces = {}            # Tài nguyên tạo ra mỗi giây, vd {"wood": 2}
    icon_key = "default"    # Tên sprite trong renderer

    def __init__(self, row, col):
        super().__init__(entity_id=f"{self.key}_{row}_{col}", row=row, col=col)
        self.level = 1

    # là 
    def to_dict(self):  
        return {"key": self.key, "row": self.row, "col": self.col, "level": self.level}


class Woodcutter(Building): # 
    key = "woodcutter"
    name = "Nhà đốn gỗ"
    cost = {"wood": 30}
    produces = {"wood": 2}
    icon_key = "woodcutter"


class Quarry(Building):
    key = "quarry"
    name = "Mỏ đá"
    cost = {"wood": 20, "stone": 10}
    produces = {"stone": 1}
    icon_key = "quarry"


class TowerOfLight(Building):
    key = "tower_of_light"
    name = "Tháp ánh sáng"
    cost = {"wood": 30, "stone": 10}
    produces = {"light": 1}
    icon_key = "tower_of_light"


# Registry để tra class theo `key` (dùng khi xây công trình mới hoặc load save file).
BUILDING_TYPES = {
    Woodcutter.key: Woodcutter,
    Quarry.key: Quarry,
    TowerOfLight.key: TowerOfLight,
}
