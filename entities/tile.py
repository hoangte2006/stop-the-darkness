"""Tile entity representing one board cell."""

from entities.base import Entity


class Tile(Entity):
    """Đại diện cho 1 ô trên bàn cờ."""

    def __init__(self, row, col, terrain="grass"):
        super().__init__(entity_id=f"tile_{row}_{col}", row=row, col=col) 
        self.terrain = terrain    # "grass" | "forest" | "water" | "rock"
        self.building = None     # None hoặc 1 instance của Building (xem entities/building.py)
        self.is_dark = False     # Ô đã bị bóng tối chiếm chưa?
        self.is_lighted = False  # Được bảo vệ bởi Tháp Ánh Sáng chưa?

    def to_dict(self):
        """Chuyển ô thành dict thuần để TV4 lưu ra JSON."""
        return {
            "row": self.row, 
            "col": self.col,
            "terrain": self.terrain,
            "building": self.building.key if self.building else None,
            "is_dark": self.is_dark,
            "is_lighted": self.is_lighted,
        }
