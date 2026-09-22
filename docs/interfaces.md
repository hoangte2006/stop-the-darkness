# Interface Contract — Stop the Darkness

File này liệt kê **mọi hàm/class public** mà các thành viên có thể gọi mà
không cần đọc code của người khác. Nếu bạn cần dữ liệu/hàm nào chưa có ở đây,
báo Leader (TV1) để thêm vào — không tự sửa `core/game_state.py`.

Số liệu đã chốt: **grid 12x12**, **tile 40x40px**, **sidebar 260px**,
**window 740x480**. Xem `core/constants.py`.

## `core/constants.py`
Hằng số dùng chung: `GRID_ROWS`, `GRID_COLS`, `TILE_SIZE`, `SIDEBAR_X`,
`SIDEBAR_WIDTH`, `SCREEN_WIDTH`, `SCREEN_HEIGHT`, và các `COLOR_*`.

## `entities/tile.py` — class `Tile`
Đại diện 1 ô trên bàn cờ.

| Thuộc tính | Kiểu | Ý nghĩa |
|---|---|---|
| `row`, `col` | `int` | Toạ độ ô |
| `terrain` | `str` | `"grass"` \| `"forest"` \| `"water"` \| `"rock"` |
| `building` | `Building \| None` | Object công trình đang xây trên ô (xem `entities/building.py`), `None` nếu trống |
| `is_dark` | `bool` | Ô đã bị bóng tối chiếm chưa |
| `is_lighted` | `bool` | Được Tháp Ánh Sáng bảo vệ chưa (chưa có logic thật, luôn `False` ở bản khung) |

- `tile.to_dict() -> dict` — dùng cho TV4 lưu file.

## `entities/building.py` — class `Building` + con `Woodcutter`, `Quarry`, `TowerOfLight`

| Thuộc tính (class-level) | Kiểu | Ý nghĩa |
|---|---|---|
| `key` | `str` | ID định danh, vd `"woodcutter"`, `"tower_of_light"` |
| `name` | `str` | Tên hiển thị (tiếng Việt) trên UI |
| `cost` | `dict[str, int]` | Giá xây, vd `{"wood": 30}` |
| `produces` | `dict[str, int]` | Tài nguyên sinh ra mỗi giây |
| `icon_key` | `str` | Tên sprite để TV2 tra trong bộ ảnh |

`BUILDING_TYPES: dict[str, type[Building]]` — registry tra class theo `key`
(TV3 dùng để render danh sách nút xây; TV4 dùng để phục hồi building khi load save).

Building con hiện có: `Woodcutter` (30 wood → +2 wood/s), `Quarry` (20 wood +
10 stone → +1 stone/s), `TowerOfLight` (30 wood + 10 stone → +1 light/s).
Luật xây theo ô kề (vd Woodcutter phải cạnh rừng) **chưa có** ở bản khung —
sẽ bổ sung sau trong `core/rules.py`, không đổi các thuộc tính trên.

## `core/game_state.py` — class `GameState`
Import bằng `from core.game_state import GameState`.

| Method | Chữ ký | Trả về | Ý nghĩa |
|---|---|---|---|
| `get_tile` | `(row: int, col: int)` | `Tile \| None` | Lấy ô, `None` nếu ngoài bàn cờ |
| `add_building` | `(row: int, col: int, building_key: str)` | `bool` | Xây công trình; `False` nếu ô không hợp lệ/đã có building/đang tối/thiếu tài nguyên |
| `tick_resources` | `()` | `None` | Cộng tài nguyên theo các building đang hoạt động (gọi mỗi giây) |
| `spread_darkness` | `()` | `None` | Lan bóng tối 1 nhịp (gọi mỗi 3 giây) |
| `to_dict` | `()` | `dict` | Serialize toàn bộ state — đưa dict này cho `services/storage.save_game` |
| `load_from_dict` | `(data: dict)` | `None` | Nạp lại state từ dict đọc được bởi `services/storage.load_game` |

Thuộc tính public: `resources: dict[str, int]`, `grid: list[list[Tile]]`,
`selected_tile: Tile | None`, `is_paused: bool`.

## Interface các bạn khác cần cung cấp (Leader gọi vào)

- **TV2 — `ui/renderer.py`**: `draw(screen, game: GameState) -> None` — vẽ
  bàn cờ dựa trên `game.grid` (dùng `tile.terrain`, `tile.building.icon_key`,
  `tile.is_dark`).
- **TV3 — `ui/button.py`**: class `Button` với `handle_event(event) -> bool`
  (trả `True` nếu bị click) và `is_clicked(mouse_pos) -> bool`.
  **`ui/sidebar.py`**: hiển thị `game.resources`, danh sách building từ
  `entities.building.BUILDING_TYPES`, và gọi `game.add_building(...)` khi bấm nút xây.
- **TV4 — `services/storage.py`**: `save_game(data: dict, filename: str) -> bool`
  (nhận `game.to_dict()`), `load_game(filename: str) -> dict` (trả dict để
  truyền vào `game.load_from_dict(...)`).
- **TV5 — `services/audio.py`**: class `AudioManager` với `play_bgm(name: str) -> None`,
  `play_sfx(name: str) -> None`, `set_volume(value: float) -> None`.
- **TV6 — `core/map_generator.py`**: `generate_map(rows: int = GRID_ROWS, cols: int = GRID_COLS) -> list[list[str]]`
  (đã có bản mock random ở khung, thay bằng Cellular Automata/Perlin Noise thật —
  **giữ nguyên chữ ký**, `game_state.py` đang gọi thẳng vào hàm này).

## Việc còn lại của Leader (chưa phải khung, làm sau — không chặn ai)

- `core/rules.py`: thay `spread_darkness()` (đang random 1 ô/nhịp) bằng BFS
  thật; hoàn thiện `is_adjacent_to()` cho luật xây theo ô kề.
- `entities/building.py`: bổ sung luật xây dựng thật (kiểm tra ô kề, nâng cấp cấp độ).
