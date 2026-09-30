# Interface Contract — Stop the Darkness

File này liệt kê **mọi hàm/class public** mà các thành viên có thể gọi mà
không cần đọc code của người khác. Nếu bạn cần dữ liệu/hàm nào chưa có ở đây,
báo Leader (TV1) để thêm vào — không tự sửa `core/game_state.py`.

Số liệu đã chốt: **grid 12x12**, **tile 40x40px**, **sidebar 260px**,
**window 740x480**. Xem `core/constants.py`.

---

## `core/constants.py`

Hằng số dùng chung: `GRID_ROWS`, `GRID_COLS`, `TILE_SIZE`, `SIDEBAR_X`,
`SIDEBAR_WIDTH`, `SCREEN_WIDTH`, `SCREEN_HEIGHT`, và các `COLOR_*`.

---

## `entities/tile.py` — class `Tile`

Đại diện 1 ô trên bàn cờ.

**Thuộc tính:**
- `row`, `col` (`int`) — toạ độ ô.
- `terrain` (`str`) — `"grass"` | `"forest"` | `"water"` | `"rock"`.
- `building` (`Building | None`) — object công trình đang xây trên ô (xem
  `entities/building.py`), `None` nếu ô trống.
- `is_dark` (`bool`) — ô đã bị bóng tối chiếm chưa.
- `is_lighted` (`bool`) — có đang được Tháp Ánh Sáng bảo vệ không (tính bởi
  `core/rules.py: update_light()`).

**Method:**
- `tile.to_dict() -> dict` — dùng cho TV4 lưu file JSON.

---

## `entities/building.py` — class `Building` + con `Woodcutter`, `Quarry`, `TowerOfLight`

**Thuộc tính khai ở mỗi class (class-level):**
- `key` (`str`) — ID định danh, dùng để lưu/tải file và tra `BUILDING_TYPES`.
  Vd `"woodcutter"`, `"tower_of_light"`.
- `name` (`str`) — tên hiển thị (tiếng Việt) trên UI.
- `base_cost` (`dict[str, int]`) — giá xây ban đầu ở level 1. Vd `{"wood": 30}`.
- `cost_multiplier` (`float`) — hệ số tăng giá mỗi lần nâng cấp (mặc định `1.5`).
- `base_produces` (`dict[str, int]`) — sản lượng ở level 1.
- `icon_key` (`str`) — tên sprite để TV2 tra trong bộ ảnh.
- `max_level` (`int`) — cấp tối đa được phép nâng.

**Thuộc tính/method của mỗi instance (mỗi công trình đã xây):**
- `level` (`int`) — cấp hiện tại, bắt đầu từ `1`, tăng dần qua `upgrade()`.
- `produces` (`dict[str, int]`, đọc như thuộc tính — có `@property`) —
  sản lượng **thực tế hiện tại** = `base_produces × level`.
- `cost_for_next_level() -> dict[str, int]` — giá cần trả để nâng lên 1 cấp
  tiếp theo.
- `upgrade(resources: dict) -> bool` — trừ `resources` và tăng `level` nếu đủ
  tiền và chưa đạt `max_level`; trả `False` nếu không đủ điều kiện.
- `to_dict() -> dict` — dùng cho TV4 lưu file (gồm cả `level`).

**Registry:** `BUILDING_TYPES: dict[str, type[Building]]` — tra class theo
`key` (TV3 dùng để render danh sách nút xây; TV4 dùng để phục hồi building
khi load save).

**Building con hiện có:**
- `Woodcutter` — 2 wood → 2 wood/s ở level 1 (giá thấp để khởi động kinh tế,
  người chơi có sẵn 12 wood lúc bắt đầu).
- `Quarry` — 8 wood (không cần stone, vì Quarry chính là nguồn tạo ra stone
  đầu tiên) → 1 stone/s ở level 1.
- `TowerOfLight` — 30 wood + 10 stone → 1 light/s ở level 1, còn tự phát sáng
  bảo vệ ô xung quanh (xem `update_light` bên dưới).

Luật xây theo ô kề (vd Woodcutter phải cạnh rừng) **chưa có**, dùng
`rules.is_adjacent_to()` khi cần bổ sung sau.

---

## `core/game_state.py` — class `GameState`

Import bằng `from core.game_state import GameState`. File này là "hợp đồng
giao tiếp" dùng chung cho cả team — không sửa nếu không phải Leader.

**Method:**
- `get_tile(row: int, col: int) -> Tile | None` — lấy ô, `None` nếu ngoài bàn cờ.
- `add_building(row: int, col: int, building_key: str) -> bool` — xây công
  trình; `False` nếu ô không hợp lệ / đã có building / đang tối / thiếu
  tài nguyên.
- `upgrade_building(row: int, col: int) -> bool` — nâng cấp công trình đã có
  trên ô đó; `False` nếu ô trống hoặc không đủ điều kiện (gọi thẳng vào
  `Building.upgrade()`).
- `remove_building(row: int, col: int) -> bool` — phá bỏ công trình tại ô đó
  (nút "Demolish/Sell"); `False` nếu ô trống hoặc không có công trình.
- `set_speed(multiplier: int) -> None` — đặt tốc độ mô phỏng (1/2/3). Bản
  thân `GameState` chỉ lưu `speed_multiplier`; **main.py** mới là nơi thực sự
  rút ngắn nhịp đồng hồ (`pygame.time.set_timer`) dựa theo giá trị này.
- `tick_resources() -> None` — cộng tài nguyên theo các building đang hoạt
  động (gọi theo nhịp `RESOURCE_EVENT` của main.py).
- `spread_darkness() -> None` — lan bóng tối thêm 1 ô theo thứ tự vòng xoáy
  (gọi theo nhịp `DARKNESS_EVENT` của main.py), rồi tự kiểm tra điều kiện thua.
- `update_light() -> None` — tính lại `is_lighted` cho mọi ô dựa trên các
  Tháp Ánh Sáng hiện có (gọi `rules.update_light()`). Nên gọi lại sau mỗi lần
  `add_building`/`upgrade_building`/`remove_building` ảnh hưởng tới TowerOfLight.
- `to_dict() -> dict` — serialize toàn bộ state, đưa cho `services/storage.save_game`.
- `load_from_dict(data: dict) -> None` — nạp lại state từ dict do
  `services/storage.load_game` đọc được.

**Thuộc tính public:**
- `resources: dict[str, int]` — bắt đầu `{"wood": 12, "stone": 0, "tech": 0, "light": 0}`.
- `grid: list[list[Tile]]`
- `selected_tile: Tile | None`
- `is_paused: bool`
- `game_over: bool` — `True` khi bóng tối đã lan hết mức có thể. TV5 dùng để
  hiện màn hình Game Over.
- `speed_multiplier: int` — 1/2/3, đổi qua `set_speed()`.

## `core/rules.py` — logic thuật toán, `GameState` gọi vào

- `spread_darkness(grid: list[list[Tile]]) -> None` — tối thêm đúng 1 ô mỗi
  lần gọi, theo thứ tự cố định từ góc dưới-trái, vòng quanh mép ngoài rồi thu
  dần vào tâm (xem `build_spiral_order`). Ô đang `is_lighted` sẽ được bỏ qua,
  không bị tối.
- `update_light(grid: list[list[Tile]]) -> None` — tính lại `is_lighted` cho
  mọi ô dựa trên vị trí các `TowerOfLight` hiện có. Gọi lại hàm này mỗi khi
  xây/nâng cấp/phá 1 Tháp Ánh Sáng.
- `is_adjacent_to(grid, row: int, col: int, terrain: str) -> bool` — kiểm
  tra 4 ô kề `(row, col)` có ô nào thuộc loại địa hình `terrain` không (dùng
  cho luật xây theo ô kề, chưa gắn vào `add_building`).

---

## Interface các bạn khác cần cung cấp (Leader gọi vào)

- **TV2 — `ui/renderer.py`**: **đã hoàn thành** — class `TileMapRenderer(tile_size)`
  với:
  - `load_sprites() -> None` — nạp toàn bộ sprite 1 lần, gọi trước vòng lặp
    game (đọc file trong `assets/images/ui/sprites/`, map bằng dict
    `SPRITE_FILES` trong file này).
  - `sprite_key_for_tile(tile: Tile) -> str` — quyết định 1 tile nên vẽ bằng
    sprite nào: `is_dark` → `"darkness"`, có `building` → `"building"`,
    ngược lại dùng `tile.terrain`.
  - `draw(screen, game: GameState) -> None` — vẽ toàn bộ `game.grid` lên
    `screen`, dùng đúng sprite cho từng ô qua `sprite_key_for_tile`.

  Ví dụ dùng trong `main.py`:
  ```python
  renderer = TileMapRenderer(TILE_SIZE)   # 1 lan truoc vong lap
  renderer.load_sprites()
  ...
  renderer.draw(screen, game)             # moi frame
  ```
- **TV3 — `ui/button.py`**: class `Button` với `handle_event(event) -> bool`
  (trả `True` nếu bị click), `is_clicked(mouse_pos) -> bool`, và
  `draw(screen) -> None`.
  **`ui/sidebar.py`**: class `Sidebar` (không phải hàm đơn) — tạo **1 lần**
  trước vòng lặp game (`sidebar = Sidebar()`), rồi gọi 3 method mỗi frame:
  - `sidebar.handle_event(event, game) -> None` — gọi cho **mọi** sự kiện
    trong vòng lặp bắt sự kiện (không chỉ click chuột, còn cần bắt hover).
    Tự xử lý nút Pause/1x/2x/3x (gọi `game.set_speed`), Upgrade/Demolish
    (gọi `game.upgrade_building`/`game.remove_building`), và các nút xây
    từng loại building (gọi `game.add_building`).
  - `sidebar.update(game) -> None` — gọi 1 lần mỗi frame (trước khi vẽ) để
    cập nhật màu/trạng thái bật-tắt của từng nút theo `game` hiện tại.
  - `sidebar.draw(screen, game) -> None` — vẽ toàn bộ sidebar lên `screen`.

  Ví dụ dùng trong `main.py`:
  ```python
  sidebar = Sidebar()                      # 1 lan truoc vong lap
  ...
  for event in pygame.event.get():
      sidebar.handle_event(event, game)    # moi su kien
  ...
  sidebar.update(game)                     # moi frame, truoc khi ve
  sidebar.draw(screen, game)
  ```
- **TV4 — `services/storage.py`**: `save_game(data: dict, filename: str) -> bool`
  (nhận `game.to_dict()`), `load_game(filename: str) -> dict` (trả dict để
  truyền vào `game.load_from_dict(...)`).
- **TV5 — `services/audio.py`**: **đã hoàn thành** — class `AudioManager` với
  `load_default_sounds() -> None`, `play_music(filename: str, loop=True) -> None`,
  `play_sound(name: str) -> None`, `set_music_volume`/`set_sound_volume(value: float) -> None`.
  **`ui/menu.py`**: **đã hoàn thành** — class `Menu(screen)` với
  `draw_start_menu()`, `draw_game_over()`, `handle_start_menu_event(event) -> "start"|"quit"|None`,
  `handle_game_over_event(event) -> "restart"|None`. Cả 2 đã ghép vào
  `main.py` (màn hình Start → Playing → Game Over).
- **TV6 — `core/map_generator.py`**: `generate_map(rows: int = GRID_ROWS, cols: int = GRID_COLS) -> list[list[str]]`
  — **đã hoàn thành** (Cellular Automata gom cụm, đúng tỷ lệ 50/25/15/10%
  grass/forest/water/rock). `game_state.py` gọi thẳng vào hàm này, không cần
  sửa gì thêm.

---

## Việc còn lại của Leader (chưa xong, không chặn ai)

- **Cơ chế buff theo ô kề (adjacency bonus)** — dùng `rules.is_adjacent_to()`
  đã có sẵn, nối vào `tick_resources()` để công trình cạnh nhau tự cộng thêm
  sản lượng. Đây là nền tảng để thêm các loại building mới (Village,
  PortVillage...) sau này.
- Điều kiện thắng (vd sống sót đủ N nhịp) — chưa chốt số, sẽ thêm
  `game.game_won` tương tự `game_over`.
- `entities/building.py`: gắn luật xây theo ô kề (vd Woodcutter phải cạnh
  rừng) vào `add_building`, nếu nhóm muốn giới hạn vị trí xây theo địa hình.
