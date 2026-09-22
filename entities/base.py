"""Base class for game entities."""


class Entity:
    """Class cha cho mọi thực thể có vị trí trên bàn cờ (Tile, Building...)."""

    def __init__(self, entity_id, row, col):
        self.entity_id = entity_id  # ID duy nhất, vd "tower_of_light_3_5"
        self.row = row
        self.col = col
