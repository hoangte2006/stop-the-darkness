# Interface Contract — Stop the Darkness

File này liệt kê **mọi hàm/class public** mà các thành viên có thể gọi mà
không cần đọc code của người khác. Nếu bạn cần dữ liệu/hàm nào chưa có ở đây,
báo Leader (TV1) để thêm vào — không tự sửa `core/game_state.py`,
`core/constants.py` và `entities/building.py` (Leader giữ các file này).

Số liệu đã chốt: **grid 12x12**, **tile 40x40px**, **sidebar 260px**,
**window 740x480**. Xem `core/constants.py`.

---

## 0. Luật chơi (bản hiện tại)

- Tài nguyên: `wood` (gỗ), `stone` (đá), `light` (**mana**; code giữ tên `light`).
  Kho luôn là **số nguyên**. Bắt đầu: 20 gỗ. (`tech` còn trong kho nhưng chưa dùng.)
- **Thua**: bóng tối lan hết 144 ô của bản đồ. Bóng tối **nuốt mọi thứ** kể cả
  công trình (ô bị tối thì công trình ngừng sản xuất, không nâng cấp được).
- **Thắng** (2 đường):
  1. Nâng **Vòng tròn đá** (có sẵn ở tâm bản đồ) lên Lv2: 100 stone + 100 mana.
  2. Nâng một **Tháp ánh sáng** lên cấp tối đa (Lv3).
- **Tháp ánh sáng làm chậm bóng tối** (không chặn): mỗi cấp tháp kéo dài thêm
  `tower_slow` (theo độ khó) thời gian giữa 2 lần bóng tối lan. Tháp bị bóng tối
  nuốt thì hết làm chậm.
- Giá xây **tăng dần** theo số công trình cùng loại đã có (nhà gỗ: 5, 6, 7...),
  và nâng cấp tốn thêm **đá**.
- **3 mức độ khó** (chọn ở màn START, lưu theo từng ván), xem bảng bên dưới.

### Độ khó (`core/constants.py: DIFFICULTIES`)
| Mức | `production` (hệ số sản lượng) | `darkness_ms` (ms/ô ở 1x) | `map` (độ khó bản đồ TV6) | `tower_slow` (mỗi cấp tháp) |
|---|---|---|---|---|
| `easy` | 1.25 | 7000 | 1 | 0.35 |
| `normal` (mặc định) | 1.15 | 6000 | 1 | 0.25 |
| `hard` | 1.0 | 6000 | 2 | 0.15 |

Lý do `tower_slow` giảm theo độ khó: xây 3 tháp Lv1 rẻ (105 gỗ + 45 mana) từng làm
bóng tối chậm gấp đôi, xoá hết chênh lệch tốc độ bóng tối giữa các mức. Số liệu
mô phỏng ở mức Hard: người chơi bình thường thắng ~7% nếu không xây tháp, ~64-86%
nếu xây 3-5 tháp với `tower_slow = 0.35`; giảm còn 0.15 thì còn ~14-29%.

### Luồng màn hình và phím (`main.py`)
`screen_state`: `"start_menu"` → `"playing"` ↔ `"save_load"` → `"game_over"`.

| Phím / thao tác | Tác dụng |
|---|---|
| Start menu: **START GAME** | Màn chọn độ khó (Easy/Normal/Hard) rồi vào game |
| Start menu: **LOAD GAME** | Màn chọn slot (chỉ nạp), nạp ván đã lưu (khôi phục cả độ khó) |
| Start menu: **HOW TO PLAY** / **SETTINGS** | Màn hướng dẫn / chỉnh âm lượng nhạc và hiệu ứng |
| Chuột trái vào bàn cờ | Chọn ô (sidebar hiện thông tin) |
| Nút trên sidebar | Xây / nâng cấp / phá, Pause, 1x/2x/3x, **Menu** (mở Save/Load) |
| `Esc` (trong game) | Mở màn Save/Load (có cả Save và Load); game đứng yên khi đang mở |
| `Space` | Tạm dừng / tiếp tục |
| `Q` / `W` / `E` | Phím tắt **lưu** vào slot 1 / 2 / 3 (`saves/save-slotN.json`) |
| `1` / `2` / `3` | Phím tắt **nạp** từ slot 1 / 2 / 3 |
| `F1` | **Phím dev**: +100 mỗi tài nguyên (**phải xóa trước ngày thuyết trình**) |

---

## `core/constants.py`

Hằng số dùng chung: `GRID_ROWS`, `GRID_COLS`, `TILE_SIZE`, `SIDEBAR_X`,
`SIDEBAR_WIDTH`, `SCREEN_WIDTH`, `SCREEN_HEIGHT`, các `COLOR_*`, và
`DIFFICULTIES` / `DEFAULT_DIFFICULTY` (xem bảng độ khó ở trên).

---

## `entities/tile.py` — class `Tile`

Đại diện 1 ô trên bàn cờ.

**Thuộc tính:**
- `row`, `col` (`int`) — toạ độ ô.
- `terrain` (`str`) — `"grass"` | `"forest"` | `"water"` | `"rock"` | `"mushroom"`.
  (Bộ sinh map còn tạo `"ruins"` ở tâm, nhưng `GameState` luôn đổi ô tâm thành
  `"grass"` và đặt Vòng tròn đá lên đó, nên **ô `ruins` không bao giờ xuất hiện
  trong game**.)
- `building` (`Building | None`) — object công trình đang xây trên ô (xem
  `entities/building.py`), `None` nếu ô trống.
- `is_dark` (`bool`) — ô đã bị bóng tối chiếm chưa.
- `is_lighted` (`bool`) — ô nằm cạnh Tháp ánh sáng (tính bởi
  `rules.update_light()`). **Chỉ để hiển thị** ("Illuminated" ở sidebar), **không
  bảo vệ ô khỏi bóng tối**.

**Method:**
- `tile.to_dict() -> dict` — dùng cho lưu file JSON.

---

## `entities/building.py` — class `Building` + các công trình

**Thuộc tính khai ở mỗi class (class-level):**
- `key` (`str`) — ID định danh, dùng để lưu/tải file và tra `BUILDING_TYPES`.
- `name` (`str`) — tên hiển thị (tiếng Việt) trên UI.
- `base_cost` (`dict[str, int]`) — giá xây công trình **đầu tiên** của loại này.
  (`"light"` là mana.)
- `build_cost_step` (`dict[str, int]`) — mỗi công trình **cùng loại** đã có làm giá
  xây tăng thêm bấy nhiêu. Giá xây thật tính bởi `GameState.build_cost()`.
- `upgrade_base_cost` (`dict | None`) — giá nâng lên **Lv2** (`None` = dùng
  `base_cost`). Nâng lên Lv3 = giá này × `cost_multiplier`.
- `cost_multiplier` (`float`) — hệ số giá nâng Lv2→Lv3 (mặc định `2.0`, Tháp `8`).
- `base_produces` (`dict[str, float]`) — sản lượng **mỗi PHÚT** ở level 1
  (`tick_resources()` chạy mỗi giây và cộng `số/60`), **chưa** nhân hệ số độ khó.
- `icon_key` (`str`) — tên loại sprite để TV2 tra (**xem phần TV2**).
- `max_level` (`int`) — cấp tối đa (mặc định 3; Vòng tròn đá là 2).
- `build_terrain` (`str | None`) — địa hình BẮT BUỘC của ô được xây (`None` = nơi
  nào cũng được). Không công trình nào xây được trên `"water"`.
- `buildable` (`bool`) — `False` = có sẵn từ đầu game, người chơi không tự xây và
  không phá được (hiện chỉ có `StoneCircle`). **UI nên bỏ qua loại này khi liệt
  kê nút xây.**
- `boost_terrain` (`str | None`) / `boost_per_tile` (`float`) — buff theo ô kề:
  mỗi ô kề đúng loại địa hình cộng thêm `boost_per_tile` vào hệ số sản lượng.
  Woodcutter: rừng, `0.20`. Quarry: đá, `0.25`.
- `slow_per_level` (`float`) — **chỉ `TowerOfLight`**. Giờ chỉ dùng để nhận biết "đây
  là Tháp"; **độ làm chậm thật lấy từ `GameState.tower_slow` theo độ khó**.

**Thuộc tính/method của mỗi instance (mỗi công trình đã xây):**
- `level` (`int`) — cấp hiện tại, bắt đầu từ `1`.
- `produces` (`dict[str, float]`) — sản lượng mỗi phút = `base_produces × level`
  (chưa tính buff ô kề và độ khó).
- `cost_for_next_level() -> dict[str, int]` — giá nâng lên cấp kế tiếp.
- `upgrade(resources: dict) -> bool` — trừ tài nguyên và tăng `level` nếu đủ tiền
  và chưa đạt `max_level`.
- `to_dict() -> dict` — dùng cho lưu file (gồm cả `level`).

**Registry:** `BUILDING_TYPES: dict[str, type[Building]]` — tra class theo `key`
(sidebar dùng để liệt kê nút xây; `GameState.load_from_dict` dùng để phục hồi building).

**Các công trình hiện có** (số gốc, trước hệ số độ khó):

| Class (`key`) | Xây trên | Giá xây (cái 1) | Mỗi cái thêm | Nâng Lv2 | Nâng Lv3 | Sinh/phút Lv1 | `icon_key` |
|---|---|---|---|---|---|---|---|
| `Woodcutter` (`woodcutter`) | rừng | 5 wood | +1 wood | 5 wood + 2 stone | 10 wood + 4 stone | 10 wood | `woodcutter` |
| `Quarry` (`quarry`) | đá | 15 wood | +3 wood | 15 wood + 5 stone | 30 wood + 10 stone | 4 stone | `quarry` |
| `MushroomHut` (`mushroom_hut`) | **ô nấm** | 20 wood + 5 stone | +3 wood, +1 stone | 20 wood + 9 stone | 40 wood + 18 stone | 6 mana | `mushroom` |
| `TowerOfLight` (`tower_of_light`) | đất bằng | 25 wood + 15 mana | +10 wood | 25 wood + 15 mana + 10 stone | 200 wood + 120 mana + 80 stone | 1.5 mana, **làm chậm bóng tối** | `tower_of_light` |
| `StoneCircle` (`stone_circle`) | đất bằng (tâm map) | không xây được | — | 100 stone + 100 mana (**= thắng**) | — | — | `stone_circle` |

Công thức giá xây: `giá = base_cost + build_cost_step × số_công_trình_cùng_loại_đang_có`
(phá công trình thì giá giảm lại). Công thức sản lượng:
`mỗi_phút = base_produces × level × (1 + số_ô_kề_đúng_loại × boost_per_tile) × production_multiplier`
(`production_multiplier` là hệ số theo độ khó của ván).

Luật "xây kề tài nguyên" (xây trên đất bằng, kề rừng/đá) **chưa có**; hiện công
trình xây thẳng **lên** ô tài nguyên (`build_terrain`).

---

## `core/game_state.py` — class `GameState`

Import bằng `from core.game_state import GameState`. `GameState(difficulty="normal")`
là một ván mới (bóng tối tự reset). Tên mức không có trong `DIFFICULTIES` thì in cảnh
báo và dùng `normal`.

**Method:**
- `get_tile(row, col) -> Tile | None` — lấy ô, `None` nếu ngoài bàn cờ.
- `build_cost(building_key: str) -> dict[str, int]` — giá xây công trình kế tiếp
  thuộc loại đó (đã tính bước tăng). **UI phải dùng hàm này để hiện giá và bật/tắt
  nút xây**, không đọc thẳng `base_cost`.
- `production_per_minute(building_cls, row, col, level=1) -> dict[str, float]` —
  sản lượng mỗi phút của loại đó ở cấp `level` tại ô `(row, col)`, đã tính buff ô
  kề **và hệ số độ khó**. Dùng để hiện "Sinh/phút" hiện tại và sau nâng cấp.
- `add_building(row, col, building_key) -> bool` — xây công trình; `False` nếu ô
  không hợp lệ / `buildable = False` / sai `build_terrain` / đã có building / đang
  tối / thiếu tài nguyên (theo `build_cost`).
- `upgrade_building(row, col) -> bool` — nâng cấp; `False` nếu ô trống, **ô đang
  tối**, hoặc không đủ điều kiện. Thành công thì tự kiểm tra điều kiện thắng.
- `remove_building(row, col) -> bool` — phá công trình; `False` nếu ô trống hoặc
  `buildable = False` (không phá được Vòng tròn đá).
- `set_speed(multiplier)` — đặt tốc độ (1/2/3). `GameState` chỉ lưu
  `speed_multiplier`; **main.py** mới là nơi rút ngắn nhịp đồng hồ.
- `tick_resources()` — cộng tài nguyên theo các building chưa bị tối (gọi mỗi
  nhịp `RESOURCE_EVENT`). Cộng `sản_lượng_mỗi_phút / 60 × buff ô kề × production_multiplier`;
  phần lẻ dồn vào `_carry` (nội bộ), kho luôn là số nguyên. **Không** nhân
  `speed_multiplier` (tốc độ đã được `main.py` thể hiện bằng cách rút ngắn nhịp gọi).
- `spread_darkness()` — gọi theo nhịp `DARKNESS_EVENT`. Mỗi lần gọi cộng vào bộ
  đếm `_dark_charge` lượng `1 / (1 + darkness_slowdown())`; đủ 1 thì lan thêm 1
  ô. Rồi kiểm tra điều kiện thua.
- `darkness_slowdown() -> float` — tổng độ làm chậm của các Tháp còn sống
  (`tower_slow × level`), tháp ở ô đã tối thì không tính.
- `update_light()` — tính lại `is_lighted` (chỉ để hiển thị). `main.py` gọi mỗi frame.
- `to_dict() -> dict` / `load_from_dict(data)` — serialize / khôi phục toàn bộ
  state (`resources`, `grid`, `game_over`, `game_won`, `dark_progress`,
  `difficulty`). Nạp save sẽ khôi phục luôn `production_multiplier`,
  `darkness_interval_ms`, `tower_slow` theo `difficulty` trong save. Save cũ thiếu
  `dark_progress` / `difficulty` vẫn nạp được (giữ độ khó hiện tại).

**Thuộc tính public:**
- `resources: dict[str, int]` — `{"wood": 20, "stone": 0, "tech": 0, "light": 0}`.
- `grid: list[list[Tile]]`, `selected_tile: Tile | None`, `is_paused: bool`.
- `difficulty: str` — `"easy"` | `"normal"` | `"hard"`.
- `production_multiplier: float`, `darkness_interval_ms: int`, `tower_slow: float` —
  3 giá trị tra từ `DIFFICULTIES[difficulty]`. **`main.py` dùng
  `game.darkness_interval_ms` để đặt đồng hồ bóng tối.**
- `game_over: bool` — `True` khi bóng tối lan hết bản đồ (màn Game Over).
- `game_won: bool` — `True` khi thắng (Vòng tròn đá Lv2 **hoặc** một Tháp đạt cấp
  tối đa). `main.py` kiểm tra cờ này sau mỗi `tick_resources()` rồi gọi
  `menu.draw_game_over(won=game.game_won)`.
- `speed_multiplier: int` — 1/2/3, đổi qua `set_speed()`.

**Khởi tạo bản đồ (trong `__init__`):** gọi
`generate_map(GRID_ROWS, GRID_COLS, difficulty=DIFFICULTIES[difficulty]["map"])` lại
cho tới khi có ít nhất 6 ô mỗi loại rừng/đá/nước (nếu một mức độ khó nào của
`map_generator` tạo ra ít hơn 6 ô của một loại, **game sẽ đứng hình** do vòng lặp
sinh lại); ép ô tâm `(6, 6)` thành `"grass"` và đặt `StoneCircle` lên đó.

## `core/rules.py` — logic thuật toán, `GameState` gọi vào

- `spread_darkness(grid)` — tối **đúng 1 ô** mỗi lần gọi, theo thứ tự cố định từ
  góc dưới-trái, vòng quanh mép ngoài rồi thu dần vào tâm (`build_spiral_order`).
  **Không bỏ qua ô `is_lighted`** (không ô nào được bảo vệ).
- `update_light(grid)` — tính lại `is_lighted` quanh các `TowerOfLight` (hiển thị).
- `reset_darkness()` — đặt tiến độ bóng tối về 0 (`GameState.__init__` gọi).
- `get_darkness_progress() -> int` / `set_darkness_progress(value)` — đọc/ghi
  tiến độ (0..144) cho save/load.
- `is_adjacent_to(grid, row, col, terrain) -> bool` — 4 ô kề có ô loại `terrain` không.
- `count_adjacent_terrain(grid, row, col, terrain) -> int` — đếm số ô kề (0-4) đúng
  loại, dùng cho buff ô kề.

---

## Interface các bạn khác cung cấp

### TV2 — `ui/renderer.py` (đã hoàn thành)
Class `TileMapRenderer(tile_size)`:
- `load_sprites()` — nạp toàn bộ sprite 1 lần (**phải gọi sau `pygame.display.set_mode`**).
- `draw(screen, game)` — vẽ cả bàn cờ, tự chọn sprite, tự chạy hiệu ứng nâng cấp và
  hiệu ứng bóng tối. Chỉ **đọc** `game`, không thay đổi gì.

Cách chọn sprite (bảng `SPRITE_FILES`, khoá là `(loại, cấp)`, ảnh trong
`assets/images/sprites/`):
- Địa hình: `("grass", 0)`, `("forest", 0)`, `("rock", 0)`, `("water", 0)`, `("mushroom", 0)`.
- Công trình: tra theo `building.icon_key` và `building.level`, ví dụ
  `("woodcutter", 2)`.

> ⚠️ **Thêm công trình mới thì nên thêm sprite** vào `SPRITE_FILES`. Công trình có
> `icon_key` (hoặc ô có địa hình) chưa có trong bảng sẽ **in cảnh báo và dùng ảnh
> dự phòng** (game không crash), nhưng hình sẽ không đúng. Hiện có sprite cho:
> `woodcutter`, `quarry`, `tower_of_light`, `mushroom` (3 cấp) và `stone_circle`
> (2 cấp, ảnh riêng của TV2 trong `assets/images/sprites/stone-circle/`).

### TV3 — `ui/button.py`, `ui/sidebar.py` (đã hoàn thành)
- `Button`: `handle_event(event) -> bool`, `is_clicked(mouse_pos) -> bool`, `draw(screen)`.
- `Sidebar` (tạo 1 lần mỗi ván):
  - `sidebar.handle_event(event, game, audio=None)` — gọi cho **mọi** sự kiện.
  - `sidebar.update(game)` — mỗi frame, trước khi vẽ.
  - `sidebar.draw(screen, game)` — vẽ sidebar.
  - `sidebar.open_save_load` (`bool`) — cờ bật khi người chơi bấm nút **Menu**;
    `main.py` đọc cờ này, đổi màn hình sang Save/Load rồi tự tắt cờ.

Sidebar hiện: tài nguyên (Wood / Stone / Mana), nút tốc độ/Pause/**Menu**, thông tin
ô, 4 nút xây (Nhà gỗ, Mỏ đá, Nhà nấm, Tháp ánh sáng; giá thật + sản lượng/phút +
buff ô kề khi rê chuột), nút Upgrade/Demolish kèm sản lượng hiện tại và sau nâng
cấp, độ làm chậm của Tháp (theo độ khó), bảng Thống kê. Bỏ qua công trình
`buildable = False`. Số giây còn lại của bảng Thống kê (thắng/thua) tính theo từng
ván (sidebar tạo mới mỗi ván).

### TV4 — `services/storage.py` (đã hoàn thành phần lưu 3 slot)
- `save_game(data: dict, saveSlot: int = 1) -> bool` — ghi `data` vào
  `saves/save-slot{1..3}.json`, `False` nếu slot sai hoặc ghi lỗi.
- `load_game(saveSlot: int = 1) -> dict` — đọc slot, trả `{}` nếu thiếu file/hỏng
  (lỗi in ra terminal; `main.py` kiểm tra `if not data`).
- `SAVE_FILES` — bảng slot → đường dẫn file.

**Chưa có:** `get_slot_info(slot) -> dict | None`. Tạm thời `main.py` tự tạo thông
tin slot bằng giờ sửa đổi file (`get_slot_infos()`), trả `{"display_text": "Saved HH:MM dd/mm"}`
hoặc `None` nếu slot trống. Màn Save/Load của TV5 đọc khoá **`"display_text"`**
(hoặc `level` + `date`); nếu TV4 viết `get_slot_info` thì trả cùng khoá này.

### TV5 — `services/audio.py`, `ui/menu.py` (đã hoàn thành)
- `AudioManager`: `load_default_sounds()`, `play_music(filename, loop=True)`,
  `play_sound(name)` (có chống spam: cooldown 400ms cho `"darkness"`, 100ms cho
  `"build"`), `stop_music()`, `set_music_volume(v)`, `set_sound_volume(v)` (giới hạn
  0..1). Âm đã nạp: `"button"`, `"build"`, `"bell"`, `"darkness"` (`"darkness"` hiện
  **chưa được gọi** ở đâu trong game).
- `Menu(screen)`:
  - Gán `menu.audio = audio` ngay sau khi tạo, và đặt âm lượng đã lưu:
    `audio.set_music_volume(menu.settings["music_volume"])`,
    `audio.set_sound_volume(menu.settings["sound_volume"])` (`main.py` đã làm).
  - **Cách gọn (main.py đang dùng cho start menu):** `menu.draw(slot_infos=None, can_save=False)`
    vẽ màn hiện tại theo `menu.state`; `menu.handle_event(event)` trả
    `"quit"` | `"easy"/"normal"/"hard"` | `("load", n)` | `("save", n)` | `None`.
  - Các màn riêng (`main.py` gọi trực tiếp cho Save/Load trong game và Game Over):
    `draw_start_menu()`, `draw_difficulty_menu()` + `handle_difficulty_event(event)`,
    `draw_save_load_menu(slot_infos, can_save)` +
    `handle_save_load_event(event)` → `("save", n)` | `("load", n)` | `"back"` | `None`,
    `draw_tutorial()` + `handle_tutorial_event(event)`, `draw_settings_menu()` +
    `handle_settings_event(event)`, `draw_game_over(won=False)` +
    `handle_game_over_event(event)` → `"restart"` | `None`, và `update()` (hiệu ứng nền).
  - Cài đặt âm lượng lưu ở `settings.json` (thư mục chạy game; **đã nằm trong
    `.gitignore`**), gồm `music_volume` và `sound_volume`.

### TV6 — `core/map_generator.py` (đã hoàn thành)
`generate_map(rows=GRID_ROWS, cols=GRID_COLS, difficulty=1) -> list[list[str]]`.
Loại ô: `grass`, `forest` (cụm), `water` (dải liền), `rock` (rải đơn lẻ, ở độ khó
2, 3 thiên về xa tâm), `mushroom` (đốm nhỏ), `ruins` (đúng tâm). Tối thiểu
mỗi bản đồ: 6 rừng, 6 nước, 12 đá, 4 nấm. Số ô theo độ khó (bản mới nhất):

| `difficulty` | grass | forest | water | rock | mushroom | ruins |
|---|---|---|---|---|---|---|
| 1 | 56 | 40 | 26 | 17 | 4 | 1 |
| 2 | 71 | 32 | 22 | 14 | 4 | 1 |
| 3 | 83 | 26 | 17 | 13 | 4 | 1 |

`GameState` gọi hàm này với `difficulty=DIFFICULTIES[mức]["map"]` (Easy và Normal
dùng 1, Hard dùng 2). Muốn đổi bản đồ cho một mức, đổi số `"map"` trong bảng
`DIFFICULTIES` (Leader chốt).

---

## Những chỗ Leader đã chỉnh trong file của thành viên khác

Khi ghép các nhánh, Leader có sửa/lấy một số chỗ trong file của các bạn. Nếu bạn
sửa lại các file này, hãy `git fetch` rồi `git merge origin/main` trước để khỏi
xung đột:

| File (của ai) | Leader đã làm gì |
|---|---|
| `ui/sidebar.py` (TV3) | Nút Build bật/tắt và chữ "Cost" dùng `game.build_cost()` thay vì `base_cost`; thêm các dòng "Sinh/phút", "Nâng LvN" và độ làm chậm của Tháp (đọc `game.tower_slow`); thêm hàm `_format_rates`; thêm nút **Menu** và cờ `open_save_load`. TV3 đã giữ các phần này trong bản mới. |
| `ui/renderer.py` (TV2) | **Lấy nguyên bản mới nhất của TV2** (ảnh dự phòng thay vì crash, ảnh Vòng tròn đá riêng). Hai ảnh tạm cũ `structure/stone_circle-1.png`, `-2.png` không còn được dùng. |
| `entities/building.py` (Leader) | Nhánh TV2 có thêm một class `StoneCircle` riêng (giá `{"stone": 10}`, không `buildable = False`) — **không lấy**, vì sẽ đè lên class của Leader và làm sai luật thắng. File này **chỉ Leader sửa**. |
| `ui/menu.py`, `services/audio.py` (TV5) | Ghép nhánh TV5, **lấy nguyên bản của TV5**, không sửa gì. |
| `services/storage.py` (TV4) | Lấy `storage.py` từ nhánh TV4. **Không lấy** thay đổi của TV4 trong `core/game_state.py` và `core/rules.py` (bản đó làm mất cấp công trình và `game_won` khi nạp save; Leader đã có sẵn lưu/nạp `dark_progress`). |
| `core/map_generator.py` (TV6) | Ghép nhánh TV6 nguyên bản. `GameState` tự đổi ô tâm thành `grass` và đặt Vòng tròn đá lên đó. |
| `main.py` | Leader viết: nối start menu của TV5 (chọn độ khó, Load Game, Settings, How to Play), màn Save/Load (nút Menu và phím `Esc`), phím tắt lưu/nạp theo 3 slot, đồng hồ bóng tối theo độ khó. |

---

## Thêm một công trình mới (checklist)

1. `entities/building.py`: tạo class con (đủ `key`, `name`, `base_cost`,
   `build_cost_step`, `upgrade_base_cost`, `base_produces`, `icon_key`,
   `build_terrain`...) và đăng ký vào `BUILDING_TYPES`.
2. `ui/renderer.py` (TV2): thêm sprite cho `icon_key` vào `SPRITE_FILES` (mỗi cấp
   một ảnh). Thiếu thì game không crash nhưng hiện ảnh dự phòng và in cảnh báo.
3. `ui/sidebar.py` (TV3): nút xây tự được tạo từ `BUILDING_TYPES` (bỏ qua công trình
   `buildable = False`); hiện bố cục chứa vừa **4 nút xây** (y từ 325, cách 30px,
   cao 26px), thêm nút thứ 5 phải kiểm tra còn nằm **trong màn hình**.
4. Cập nhật bảng công trình trong file này và chạy thử mô phỏng cân bằng.

## Thêm một mức độ khó mới (checklist)

1. `core/constants.py`: thêm một dòng vào `DIFFICULTIES` với đủ 4 khoá
   (`production`, `darkness_ms`, `map`, `tower_slow`), thiếu khoá là `KeyError`.
2. `ui/menu.py` (TV5): thêm nút cho mức mới ở màn chọn độ khó, trả về đúng tên mức.
3. `main.py`: danh sách `("easy", "normal", "hard")` ở nhánh start menu cũng cần
   thêm tên mức mới.

---

## Việc còn lại

**Của Leader:**
- **Xóa phím dev F1** trước ngày thuyết trình.
- Gọi `audio.play_sound("darkness")` khi một ô bị tối (âm đã nạp, chưa dùng).
- Cân nhắc đọc `get_slot_info` của TV4 nếu bạn ấy viết, thay cho `get_slot_infos()`
  tạm trong `main.py`.

**Đã chủ động đóng băng, để sau giữa kỳ:** luật "xây kề tài nguyên", công trình
tăng sản lượng cho công trình kề (Xưởng, Cảng), cây mở khóa công trình.
