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
- `base_cost` (`dict[str, int]`) — giá xây ban đầu ở level 1. Vd `{"wood": 25, "light": 15}`.
  (`"light"` là **mana**; code giữ tên `light`, sidebar có thể hiển thị là "Mana".)
- `cost_multiplier` (`float`) — hệ số tăng giá mỗi lần nâng cấp (mặc định `1.5`).
- `base_produces` (`dict[str, float]`) — sản lượng **mỗi PHÚT** ở level 1
  (`GameState.tick_resources()` chạy mỗi giây và cộng `số/60`).
- `icon_key` (`str`) — tên sprite để TV2 tra trong bộ ảnh.
- `max_level` (`int`) — cấp tối đa được phép nâng.
- `build_terrain` (`str | None`) — địa hình BẮT BUỘC của ô được xây, vd
  `"forest"`. `None` = xây trên địa hình nào cũng được. `add_building` từ chối
  nếu `tile.terrain` khác. Vì không building nào có `build_terrain = "water"`
  nên **không xây được trên nước** (dành chỗ cho "Cảng" sau này).
- `buildable` (`bool`) — `False` = công trình có sẵn từ đầu game, người chơi
  **không tự xây** và **không phá** được (hiện chỉ có `StoneCircle`). UI nên
  bỏ qua các loại này khi liệt kê nút xây.
- `boost_terrain` (`str | None`) — loại địa hình kề giúp tăng sản lượng, vd
  `"forest"` (Woodcutter), `"rock"` (Quarry). `None` = không có buff ô kề
  (mặc định ở `Building` cha).
- `boost_per_tile` (`float`) — mỗi ô kề đúng `boost_terrain` cộng thêm bấy
  nhiêu % sản lượng (Woodcutter `0.20`, Quarry `0.25` — **cần đồng bộ** với số
  20% mà sidebar đang ghi cứng).
  Công thức áp dụng ở `GameState.tick_resources()`:
  `sản_lượng_mỗi_phút = base_produces × level × (1 + số_ô_kề_đúng_loại × boost_per_tile)`.

**Thuộc tính/method của mỗi instance (mỗi công trình đã xây):**
- `level` (`int`) — cấp hiện tại, bắt đầu từ `1`, tăng dần qua `upgrade()`.
- `produces` (`dict[str, float]`, đọc như thuộc tính — có `@property`) —
  sản lượng **mỗi phút** thực tế hiện tại = `base_produces × level` (chưa tính
  buff ô kề).
- `cost_for_next_level() -> dict[str, int]` — giá cần trả để nâng lên 1 cấp
  tiếp theo.
- `upgrade(resources: dict) -> bool` — trừ `resources` và tăng `level` nếu đủ
  tiền và chưa đạt `max_level`; trả `False` nếu không đủ điều kiện.
- `to_dict() -> dict` — dùng cho TV4 lưu file (gồm cả `level`).

**Registry:** `BUILDING_TYPES: dict[str, type[Building]]` — tra class theo
`key` (TV3 dùng để render danh sách nút xây; TV4 dùng để phục hồi building
khi load save).

**Building con hiện có** (số/phút ở level 1):

| Class (`key`) | Xây trên | Giá xây | Sinh/phút | Ghi chú |
|---|---|---|---|---|
| `Woodcutter` (`woodcutter`) | rừng (`forest`) | 5 wood | 10 wood | buff theo ô rừng kề |
| `Quarry` (`quarry`) | đá (`rock`) | 15 wood | 4 stone | buff theo ô đá kề |
| `MushroomHut` (`mushroom_hut`) | đất bằng (`grass`) | 20 wood + 5 stone | 3 mana | **placeholder** nguồn mana, sẽ thay bằng "Làng phép thuật" kề rừng nấm |
| `TowerOfLight` (`tower_of_light`) | đất bằng | 25 wood + 15 mana | 1.5 mana | tự phát sáng, chặn bóng tối ở ô kề (xem `update_light`) |
| `StoneCircle` (`stone_circle`) | đất bằng | — (nâng Lv2: 100 stone + 100 mana) | — | `buildable = False`, có sẵn ở **tâm bản đồ**, `max_level = 2`; **nâng lên Lv2 = thắng** |

Luật "xây kề tài nguyên" (phải có ô rừng/đá **kề bên** thay vì xây thẳng lên
ô) **chưa có**, hiện dùng `build_terrain` (xây thẳng lên ô). Có sẵn
`rules.is_adjacent_to()` / `rules.count_adjacent_terrain()` khi cần bổ sung.

---

## `core/game_state.py` — class `GameState`

Import bằng `from core.game_state import GameState`. File này là "hợp đồng
giao tiếp" dùng chung cho cả team — không sửa nếu không phải Leader.

**Method:**
- `get_tile(row: int, col: int) -> Tile | None` — lấy ô, `None` nếu ngoài bàn cờ.
- `add_building(row: int, col: int, building_key: str) -> bool` — xây công
  trình; `False` nếu ô không hợp lệ / công trình `buildable = False` / sai
  `build_terrain` / đã có building / đang tối / thiếu tài nguyên.
- `upgrade_building(row: int, col: int) -> bool` — nâng cấp công trình đã có
  trên ô đó; `False` nếu ô trống, **ô đang tối**, hoặc không đủ điều kiện (gọi
  vào `Building.upgrade()`). Nâng cấp thành công thì tự kiểm tra điều kiện
  thắng (nâng Vòng tròn đá lên Lv2 là thắng ngay).
- `remove_building(row: int, col: int) -> bool` — phá bỏ công trình tại ô đó
  (nút "Demolish/Sell"); `False` nếu ô trống hoặc công trình `buildable = False`
  (không phá được Vòng tròn đá).
- `set_speed(multiplier: int) -> None` — đặt tốc độ mô phỏng (1/2/3). Bản
  thân `GameState` chỉ lưu `speed_multiplier`; **main.py** mới là nơi thực sự
  rút ngắn nhịp đồng hồ (`pygame.time.set_timer`) dựa theo giá trị này.
- `tick_resources() -> None` — cộng tài nguyên theo các building đang hoạt
  động (gọi theo nhịp `RESOURCE_EVENT` của main.py, mặc định 1 giây/lần).
  Mỗi nhịp cộng `sản_lượng_mỗi_phút / 60`. **Kho `resources` luôn là số
  nguyên**: phần lẻ chưa đủ 1 đơn vị được dồn vào `_carry` (nội bộ) và chỉ
  chuyển vào kho khi đủ 1. Không nhân `speed_multiplier` ở đây (tốc độ đã
  được `main.py` thể hiện bằng cách rút ngắn nhịp gọi).
- `spread_darkness() -> None` — lan bóng tối thêm 1 ô theo thứ tự vòng xoáy
  (gọi theo nhịp `DARKNESS_EVENT` của main.py), rồi tự kiểm tra điều kiện thua.
- `update_light() -> None` — tính lại `is_lighted` cho mọi ô dựa trên các
  Tháp Ánh Sáng hiện có (gọi `rules.update_light()`). **main.py đã gọi hàm
  này mỗi frame** (trước `renderer.draw()`) nên luôn đồng bộ, không cần tự
  gọi thêm sau khi xây/nâng cấp/phá TowerOfLight.
- `to_dict() -> dict` — serialize toàn bộ state, đưa cho `services/storage.save_game`.
  Gồm `resources`, `grid`, `game_over`, `game_won` và `dark_progress` (bóng
  tối đã đi tới bước nào của vòng xoáy).
- `load_from_dict(data: dict) -> None` — nạp lại state từ dict do
  `services/storage.load_game` đọc được, khôi phục cả `dark_progress` (save cũ
  không có trường này thì ước lượng bằng số ô đang tối) và ép `resources` về
  số nguyên.

**Thuộc tính public:**
- `resources: dict[str, int]` — bắt đầu `{"wood": 20, "stone": 0, "tech": 0, "light": 0}`
  (`light` = mana). Luôn là số nguyên.
- `grid: list[list[Tile]]`
- `selected_tile: Tile | None`
- `is_paused: bool`
- `game_over: bool` — `True` khi bóng tối đã lan hết mức có thể. TV5 dùng để
  hiện màn hình Game Over.
- `game_won: bool` — `True` khi thắng game: **Vòng tròn đá (ở tâm bản đồ) đã
  được nâng lên Lv2** (tốn 100 stone + 100 mana). Kiểm tra ngay khi nâng cấp
  thành công và ở cuối mỗi `tick_resources()`. Không còn thắng bằng `tech`.
  `main.py` check cờ này sau mỗi `tick_resources()`, chuyển `screen_state` sang
  `"game_over"` và gọi `menu.draw_game_over(won=game.game_won)` để hiện đúng
  "YOU WIN!"/"GAME OVER".
- `speed_multiplier: int` — 1/2/3, đổi qua `set_speed()`.

## `core/rules.py` — logic thuật toán, `GameState` gọi vào

- `spread_darkness(grid: list[list[Tile]]) -> None` — tối thêm đúng 1 ô mỗi
  lần gọi, theo thứ tự cố định từ góc dưới-trái, vòng quanh mép ngoài rồi thu
  dần vào tâm (xem `build_spiral_order`). Ô đang `is_lighted` sẽ được bỏ qua,
  không bị tối.
- `update_light(grid: list[list[Tile]]) -> None` — tính lại `is_lighted` cho
  mọi ô dựa trên vị trí các `TowerOfLight` hiện có. Gọi lại hàm này mỗi khi
  xây/nâng cấp/phá 1 Tháp Ánh Sáng.
- `reset_darkness() -> None` — đặt tiến độ bóng tối về 0. `GameState.__init__`
  gọi hàm này để ván mới (Restart) không thừa hưởng tiến độ của ván trước.
- `get_darkness_progress() -> int` / `set_darkness_progress(value: int) -> None`
  — đọc/ghi tiến độ bóng tối (số bước vòng xoáy đã đi, 0..144), dùng cho
  save/load. `set_darkness_progress` tự giới hạn giá trị trong 0..144.
- `is_adjacent_to(grid, row: int, col: int, terrain: str) -> bool` — kiểm
  tra 4 ô kề `(row, col)` có ô nào thuộc loại địa hình `terrain` không (dùng
  cho luật xây theo ô kề, chưa gắn vào `add_building`).
- `count_adjacent_terrain(grid, row: int, col: int, terrain: str) -> int` —
  đếm trong 4 ô kề có bao nhiêu ô thuộc địa hình `terrain` (0-4). Dùng ở
  `GameState.tick_resources()` để tính buff ô kề của building
  (`boost_terrain`/`boost_per_tile`, xem phần `entities/building.py`).

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
  `draw_start_menu()`, `draw_game_over(won: bool = False)` (hiện "YOU WIN!"
  nếu `won=True`, "GAME OVER" nếu `False` — gọi bằng
  `menu.draw_game_over(won=game.game_won)`), `handle_start_menu_event(event) -> "start"|"quit"|None`,
  `handle_game_over_event(event) -> "restart"|None`. Cả 2 đã ghép vào
  `main.py` (màn hình Start → Playing → Game Over/Win).
- **TV6 — `core/map_generator.py`**: `generate_map(rows: int = GRID_ROWS, cols: int = GRID_COLS) -> list[list[str]]`
  — **đã hoàn thành** (Cellular Automata gom cụm, đúng tỷ lệ 50/25/15/10%
  grass/forest/water/rock). `game_state.py` gọi thẳng vào hàm này, không cần
  sửa gì thêm.

---

## Việc còn lại của Leader (chưa xong, không chặn ai)

- ~~Cơ chế buff theo ô kề (adjacency bonus)~~ — **đã xong** (Giai đoạn 2):
  `rules.count_adjacent_terrain()` + `Building.boost_terrain`/`boost_per_tile`
  + `GameState.tick_resources()`. Xem phần `entities/building.py` và
  `core/rules.py` ở trên.
- ~~Điều kiện thắng~~ — **đã xong**: nâng Vòng tròn đá (tâm bản đồ) lên Lv2,
  xem `game.game_won` ở phần thuộc tính public của `GameState`.
- ~~Giới hạn địa hình xây~~ — **đã xong**: `Building.build_terrain` (Woodcutter
  trên rừng, Quarry trên đá, Tháp trên đất bằng, cấm xây trên nước).
- ~~Cân bằng sản lượng~~ — **đã xong**: sản lượng tính theo phút, kho tài
  nguyên là số nguyên, bóng tối 5 giây/ô (`DARKNESS_INTERVAL_MS` trong `main.py`).

**Để sau giữa kỳ (đã chủ động đóng băng thiết kế):**
- Luật "xây kề tài nguyên" (xây trên đất bằng, kề rừng/đá thay vì xây thẳng
  lên ô) + hàm đề xuất công trình theo ô (`offer_for`) + giao diện rê chuột.
- Địa hình rừng nấm (`"mushroom"`, TV6 + TV2) và "Làng phép thuật" thay cho
  `MushroomHut` tạm.
- Nhà tăng sản lượng cho công trình kề (Xưởng gỗ/đá, Cảng).
- Cây mở khóa công trình; Tháp ánh sáng làm chậm (thay vì chặn) bóng tối.

**Phải nhớ trước ngày thuyết trình:** xóa phím dev **F1** (cộng 100 mỗi tài
nguyên) trong `main.py`.
