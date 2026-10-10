# core/constants.py

# Kích thước bản đồ lưới
GRID_ROWS = 12
GRID_COLS = 12
TILE_SIZE = 40  # Mỗi ô 40x40 pixel

# Bảng điều khiển bên phải (Sidebar)
SIDEBAR_WIDTH = 260
SIDEBAR_X = GRID_COLS * TILE_SIZE  # 480

# Kích thước màn hình = bàn cờ (12x40) + sidebar (260)
SCREEN_WIDTH = SIDEBAR_X + SIDEBAR_WIDTH  # 740
SCREEN_HEIGHT = GRID_ROWS * TILE_SIZE     # 480

# Bảng màu đại diện (RGB)
COLOR_BG = (25, 25, 30)         # Nền tối
COLOR_GRID_LINE = (50, 50, 60)   # Đường kẻ lưới
COLOR_SIDEBAR = (40, 42, 54)     # Khung thông tin bên phải

# Màu địa hình (Terrain)
COLOR_GRASS = (80, 160, 80)     # Cỏ xanh
COLOR_FOREST = (34, 110, 34)    # Rừng cây rậm
COLOR_WATER = (65, 125, 210)    # Nước biển
COLOR_ROCK = (130, 130, 140)    # Núi đá

# Màu bóng tối & ánh sáng
COLOR_DARKNESS = (20, 10, 30)   # Bóng tối nuốt chửng
COLOR_LIGHT_TOWER = (220, 180, 50) # Tháp ánh sáng

# Bảng độ khó: production = hệ số nhân sản lượng, darkness_ms = số mili-giây giữa 2 lần bóng tối lan (tốc độ 1x)
DIFFICULTIES = {
    "easy":   {"production": 1.25, "darkness_ms": 7000, "map": 1},
    "normal": {"production": 1.15, "darkness_ms": 6000, "map": 1},
    "hard":   {"production": 1.0,  "darkness_ms": 6000, "map": 1},
}
DEFAULT_DIFFICULTY = "normal"