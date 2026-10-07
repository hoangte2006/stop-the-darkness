"""

Render game board bằng sprite và visual effects.



Renderer chỉ chịu trách nhiệm HIỂN THỊ.



Renderer KHÔNG:

- xây building

- nâng cấp building

- trừ tài nguyên

- cộng tài nguyên

- thay đổi level

- thay đổi GameState



Renderer chỉ đọc state hiện tại của game rồi vẽ.

"""

import math

import random

from pathlib import Path


import pygame

# ============================================================

# PATH

# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent

SPRITE_DIR = BASE_DIR / "assets/images/sprites"


# ============================================================

# SPRITE CONFIG

# ============================================================


SPRITE_FILES = {
    # ========================================================
    # TERRAIN
    # ========================================================
    ("grass", 0): "ground/ground.png",
    ("water", 0): "water/water.png",
    # --------------------------------------------------------
    # FOREST
    # --------------------------------------------------------
    ("forest", 0): "trees/tree.png",
    # --------------------------------------------------------
    # ROCK
    # --------------------------------------------------------
    ("rock", 0): "stone/stone.png",
    # --------------------------------------------------------
    # MUSHROOM TERRAIN
    # --------------------------------------------------------
    ("mushroom", 0): "mushroom/mushroom.png",
    # ========================================================
    # MUSHROOM BUILDING / FARM
    #
    # Hiện tại building.py bạn gửi chưa có MushroomFarm.
    # Nhưng giữ sprite ở đây để sau này có thể dùng.
    # ========================================================
    ("mushroom", 1): "structure/mushroom-1.png",
    ("mushroom", 2): "structure/mushroom-2.png",
    ("mushroom", 3): "structure/mushroom-3.png",
    # ========================================================
    # WOODCUTTER
    # ========================================================
    ("woodcutter", 1): "structure/woodcutter-1.png",
    ("woodcutter", 2): "structure/woodcutter-2.png",
    ("woodcutter", 3): "structure/woodcutter-3.png",
    # ========================================================
    # QUARRY
    # ========================================================
    ("quarry", 1): "structure/quarry-1.png",
    ("quarry", 2): "structure/quarry-2.png",
    ("quarry", 3): "structure/quarry-3.png",
    # ========================================================
    # TOWER OF LIGHT
    # ========================================================
    ("tower_of_light", 1): "structure/tower_of_light-1.png",
    ("tower_of_light", 2): "structure/tower_of_light-2.png",
    ("tower_of_light", 3): "structure/tower_of_light-3.png",

    ("stone_circle", 1): "stone-circle/stone-circle-1.png",
    ("stone_circle", 2): "stone-circle/stone-circle-2.png",
}


# ============================================================

# DARKNESS

# ============================================================


DARKNESS_FILE = "darkness/darkness.png"


# ============================================================

# TERRAIN ALIASES

#

# Chỉ dùng cho terrain.

#

# Building KHÔNG nằm ở đây vì building sử dụng:

#

#     building.icon_key

#

# ============================================================


TERRAIN_ALIASES = {
    "grass": "grass",
    "ground": "grass",
    "water": "water",
    "forest": "forest",
    "tree": "forest",
    "rock": "rock",
    "stone": "rock",
    "mushroom": "mushroom",
}


# ============================================================

# PARTICLE

# ============================================================


class Particle:
    """

    Hạt nhỏ bay ra khi building được upgrade.



    Đây chỉ là visual effect.

    """

    def __init__(self, x, y):

        self.x = x

        self.y = y

        # Hướng bay ngẫu nhiên 360 độ.

        angle = random.uniform(
            0,
            math.pi * 2,
        )

        # Tốc độ ngẫu nhiên.

        speed = random.uniform(
            40,
            100,
        )

        self.vx = math.cos(angle) * speed

        self.vy = math.sin(angle) * speed

        # Kích thước particle.

        self.size = random.randint(
            2,
            4,
        )

        # Thời gian sống.

        self.life = random.uniform(
            0.4,
            0.7,
        )

        self.max_life = self.life

    # ========================================================

    # UPDATE

    # ========================================================

    def update(self, dt):

        self.x += self.vx * dt

        self.y += self.vy * dt

        # Gravity nhẹ.

        self.vy += 60 * dt

        # Giảm thời gian sống.

        self.life -= dt

    # ========================================================

    # DRAW

    # ========================================================

    def draw(self, surface):

        if self.life <= 0:

            return

        # Particle mờ dần khi sắp biến mất.

        alpha = int(255 * (self.life / self.max_life))

        particle_surface = pygame.Surface(
            (
                self.size * 2,
                self.size * 2,
            ),
            pygame.SRCALPHA,
        )

        pygame.draw.circle(
            particle_surface,
            (
                255,
                230,
                120,
                alpha,
            ),
            (
                self.size,
                self.size,
            ),
            self.size,
        )

        surface.blit(
            particle_surface,
            (
                int(self.x - self.size),
                int(self.y - self.size),
            ),
        )


# ============================================================

# TILE MAP RENDERER

# ============================================================


class TileMapRenderer:

    def __init__(self, tile_size):

        self.tile_size = tile_size

        # ====================================================

        # SPRITE CACHE

        # ====================================================

        self.sprites = {}

        # [FIX-1] Sprite dự phòng dùng khi key/file sprite bị thiếu hoặc hỏng.
        # Tạo bằng Pygame nên không phụ thuộc thêm vào file ảnh nào khác.
        self.fallback_sprite = self._create_fallback_sprite()

        # [FIX-2] Ghi nhớ warning đã in để lỗi thiếu sprite không spam mỗi frame.
        self._warned_renderer_issues = set()

        # ====================================================

        # DARKNESS SPRITE

        # ====================================================

        self.darkness_image = None

        # ====================================================

        # PARTICLES

        # ====================================================

        self.particles = []

        # ====================================================

        # LEVEL CACHE

        #

        # Renderer ghi nhớ level nhìn thấy ở frame trước.

        #

        # Ví dụ:

        #

        #   frame trước = 1

        #   frame hiện tại = 2

        #

        # => renderer biết building vừa upgrade.

        #

        # Renderer KHÔNG tự tăng level.

        # ====================================================

        self._known_levels = {}

        # ====================================================

        # UPGRADE EFFECT STATE

        # ====================================================

        self._upgrade_effects = {}

        # ====================================================

        # DARKNESS VISUAL STATE

        # ====================================================

        self._darkness_values = {}

        # ====================================================

        # TIME

        # ====================================================

        self._last_draw_time = None

        # ====================================================

        # GAME INSTANCE

        #

        # Dùng phát hiện restart/new game.

        # ====================================================

        self._current_game_id = None

    # ========================================================

    # LOAD SPRITES

    # ========================================================

    def load_sprites(self):
        """

        Load toàn bộ sprite một lần khi game khởi động.

        [FIX-3]
        - Thiếu file PNG -> dùng fallback sprite, không crash.
        - File hỏng / Pygame load lỗi -> dùng fallback sprite, không crash.
        - Không yêu cầu display phải được set trước khi load ảnh.
        - Darkness bị thiếu -> dùng darkness procedural, không crash.

        """

        self.sprites.clear()

        for key, relative_path in SPRITE_FILES.items():

            full_path = SPRITE_DIR / relative_path

            image = self._load_sprite_image(
                full_path,
                key,
            )

            self.sprites[key] = image

        # ====================================================
        # DARKNESS
        # ====================================================

        darkness_path = SPRITE_DIR / DARKNESS_FILE

        self.darkness_image = self._load_darkness_image(darkness_path)

    # ========================================================
    # FALLBACK / SAFE SPRITE HELPERS
    # ========================================================

    def _create_fallback_sprite(self):
        """
        [FIX-4]
        Tạo sprite dự phòng hoàn toàn bằng Pygame.

        Không dùng font và không dùng file ngoài, vì vậy chính fallback
        cũng không thể bị lỗi do thiếu asset.
        """

        size = max(1, int(self.tile_size))

        surface = pygame.Surface(
            (size, size),
            pygame.SRCALPHA,
        )

        # Nền tím đậm để dev nhìn ra ngay tile đang thiếu sprite.
        surface.fill((130, 45, 150, 255))

        # Ô caro nhẹ giúp fallback dễ nhận biết.
        half = max(1, size // 2)

        pygame.draw.rect(
            surface,
            (175, 75, 195, 255),
            (0, 0, half, half),
        )

        pygame.draw.rect(
            surface,
            (175, 75, 195, 255),
            (half, half, size - half, size - half),
        )

        # Viền + dấu X.
        border_width = max(1, size // 16)

        pygame.draw.rect(
            surface,
            (255, 255, 255, 255),
            surface.get_rect(),
            border_width,
        )

        padding = max(2, size // 5)

        pygame.draw.line(
            surface,
            (255, 255, 255, 255),
            (padding, padding),
            (size - padding, size - padding),
            border_width,
        )

        pygame.draw.line(
            surface,
            (255, 255, 255, 255),
            (size - padding, padding),
            (padding, size - padding),
            border_width,
        )

        return surface

    def _create_fallback_darkness(self):
        """
        [FIX-5]
        Nếu darkness.png bị thiếu/hỏng thì vẫn giữ được hiệu ứng bóng tối
        bằng một surface đen procedural.
        """

        size = max(1, int(self.tile_size))

        surface = pygame.Surface(
            (size, size),
            pygame.SRCALPHA,
        )

        surface.fill((0, 0, 0, 255))

        return surface

    def _warn_once(self, warning_key, message):
        """
        [FIX-6]
        In mỗi warning đúng một lần để thiếu sprite không spam terminal
        30/60 lần mỗi giây.
        """

        if warning_key in self._warned_renderer_issues:
            return

        self._warned_renderer_issues.add(warning_key)

        print("[Renderer WARNING] " + message)

    def _prepare_loaded_image(self, image):
        """
        [FIX-7]
        convert_alpha() chỉ được dùng khi Pygame đã có display surface.
        Nếu renderer load asset trước pygame.display.set_mode(), ảnh vẫn
        được dùng bình thường thay vì crash.
        """

        if pygame.display.get_surface() is not None:
            image = image.convert_alpha()

        return pygame.transform.scale(
            image,
            (
                self.tile_size,
                self.tile_size,
            ),
        )

    def _load_sprite_image(self, full_path, key):
        """
        [FIX-8]
        Load một sprite an toàn. Mọi lỗi asset phổ biến đều chuyển sang
        fallback thay vì làm renderer crash.
        """

        if not full_path.exists():

            self._warn_once(
                ("missing-file", key),
                (
                    f"Thiếu file sprite cho {key}: {full_path}. "
                    "Đang dùng fallback sprite."
                ),
            )

            return self.fallback_sprite

        try:

            image = pygame.image.load(str(full_path))

            return self._prepare_loaded_image(image)

        except (
            pygame.error,
            OSError,
            ValueError,
        ) as error:

            self._warn_once(
                ("load-error", key),
                (
                    f"Không load được sprite {key} từ {full_path}: "
                    f"{error}. Đang dùng fallback sprite."
                ),
            )

            return self.fallback_sprite

    def _load_darkness_image(self, darkness_path):
        """
        [FIX-9]
        Darkness cũng không còn là điểm crash của renderer.
        """

        fallback = self._create_fallback_darkness()

        if not darkness_path.exists():

            self._warn_once(
                "missing-darkness-file",
                (
                    f"Thiếu darkness sprite: {darkness_path}. "
                    "Đang dùng darkness procedural."
                ),
            )

            return fallback

        try:

            image = pygame.image.load(str(darkness_path))

            return self._prepare_loaded_image(image)

        except (
            pygame.error,
            OSError,
            ValueError,
        ) as error:

            self._warn_once(
                "darkness-load-error",
                (
                    f"Không load được darkness sprite {darkness_path}: "
                    f"{error}. Đang dùng darkness procedural."
                ),
            )

            return fallback

    # ========================================================

    # DRAW WHOLE MAP

    # ========================================================

    def draw(
        self,
        screen,
        game,
    ):
        """

        Main chỉ cần gọi:



            renderer.draw(screen, game)



        Không cần:

            renderer.update(...)

        """

        # ====================================================

        # NEW GAME / RESTART

        # ====================================================

        game_id = id(game)

        if self._current_game_id != game_id:

            self._reset_visual_state()

            self._current_game_id = game_id

        # ====================================================

        # DELTA TIME

        # ====================================================

        now = pygame.time.get_ticks()

        if self._last_draw_time is None:

            dt = 0.0

        else:

            delta_ms = now - self._last_draw_time

            # Tránh animation nhảy quá xa khi game lag.

            delta_ms = min(
                delta_ms,
                100,
            )

            dt = delta_ms / 1000.0

        self._last_draw_time = now

        # ====================================================

        # ACTIVE TILE IDS

        # ====================================================

        active_tile_ids = set()

        # ====================================================

        # DRAW MAP

        # ====================================================

        for row in game.grid:

            for tile in row:

                tile_id = id(tile)

                active_tile_ids.add(tile_id)

                # --------------------------------------------

                # Kiểm tra building có vừa upgrade hay không.

                # --------------------------------------------

                self._check_visual_level_change(
                    tile,
                    now,
                )

                # --------------------------------------------

                # Update darkness fade.

                # --------------------------------------------

                self._update_darkness_visual(
                    tile,
                    dt,
                )

                # --------------------------------------------

                # Draw tile.

                # --------------------------------------------

                self._draw_tile(
                    screen,
                    tile,
                    now,
                )

        # ====================================================

        # PARTICLES

        # ====================================================

        self._update_particles(dt)

        self._draw_particles(screen)

        # ====================================================

        # CLEANUP

        # ====================================================

        self._cleanup_inactive_tiles(active_tile_ids)

    # ========================================================

    # RESET VISUAL STATE

    # ========================================================

    def _reset_visual_state(self):
        """

        Reset state riêng của renderer.



        Không thay đổi game.

        """

        self._known_levels.clear()

        self._upgrade_effects.clear()

        self._darkness_values.clear()

        self.particles.clear()

        self._last_draw_time = None

    # ========================================================

    # CHECK BUILDING LEVEL CHANGE

    # ========================================================

    def _check_visual_level_change(
        self,
        tile,
        now,
    ):
        """

        Renderer chỉ quan sát building.level.



        Ví dụ:



            frame trước:

                level = 1



            frame này:

                level = 2



        => chạy animation upgrade.



        Renderer không biết và không quan tâm:

            - upgrade có tốn bao nhiêu gỗ

            - user có đủ tài nguyên không

            - GameState xử lý như thế nào

        """

        building = getattr(
            tile,
            "building",
            None,
        )

        tile_id = id(tile)

        # ====================================================

        # KHÔNG CÓ BUILDING

        # ====================================================

        if building is None:

            # Nếu trước đó tile từng có building,

            # xóa cache level cũ.

            self._known_levels.pop(
                tile_id,
                None,
            )

            self._upgrade_effects.pop(
                tile_id,
                None,
            )

            return

        # ====================================================

        # CURRENT LEVEL

        # ====================================================

        current_level = self._get_tile_visual_level(tile)

        previous_level = self._known_levels.get(tile_id)

        # ====================================================

        # LẦN ĐẦU NHÌN THẤY BUILDING

        #

        # Không chạy animation lúc vừa tạo building.

        # ====================================================

        if previous_level is None:

            self._known_levels[tile_id] = current_level

            return

        # ====================================================

        # LEVEL TĂNG

        # ====================================================

        if current_level > previous_level:

            self._upgrade_effects[tile_id] = {
                "start": now,
                "duration": 350,
            }

            self._create_upgrade_particles(
                tile.row,
                tile.col,
            )

        # ====================================================

        # UPDATE CACHE

        # ====================================================

        self._known_levels[tile_id] = current_level

    # ========================================================

    # GET VISUAL LEVEL

    # ========================================================

    @staticmethod
    def _get_tile_visual_level(
        tile,
    ):
        """

        Building:

            dùng tile.building.level



        Terrain:

            dùng tile.level nếu có.



        Mặc định:

            building = 1

            terrain = 0

        """

        building = getattr(
            tile,
            "building",
            None,
        )

        if building is not None:

            level = getattr(
                building,
                "level",
                1,
            )

        else:

            level = getattr(
                tile,
                "level",
                0,
            )

        try:

            return int(level)

        except (
            TypeError,
            ValueError,
        ):

            return 1 if building is not None else 0

    # ========================================================

    # DRAW TILE

    # ========================================================

    def _draw_tile(
        self,
        screen,
        tile,
        now,
    ):
        """

        Vẽ một Tile.

        """

        # ====================================================

        # SCREEN POSITION

        # ====================================================

        x = tile.col * self.tile_size

        y = tile.row * self.tile_size

        # ====================================================

        # GET SPRITE SAFELY

        # ====================================================

        # [FIX-10]
        # Không còn raise KeyError khi key không tồn tại.
        # Unknown building/terrain/type/level đều đi tới fallback sprite.
        key = self._sprite_key_for_tile(tile)

        sprite = self.sprites.get(key)

        if sprite is None:

            self._warn_once(
                ("missing-sprite-key", key),
                (f"Không tìm thấy sprite cho key {key}. " "Đang dùng fallback sprite."),
            )

            sprite = self.fallback_sprite

        # ====================================================

        # UPGRADE EFFECT

        # ====================================================

        tile_id = id(tile)

        effect = self._upgrade_effects.get(tile_id)

        if effect is not None:

            elapsed = now - effect["start"]

            duration = effect["duration"]

            if elapsed < duration:

                self._draw_upgrade_animation(
                    screen,
                    sprite,
                    x,
                    y,
                    elapsed,
                    duration,
                )

            else:

                self._upgrade_effects.pop(
                    tile_id,
                    None,
                )

                screen.blit(
                    sprite,
                    (
                        x,
                        y,
                    ),
                )

        # ====================================================

        # NORMAL DRAW

        # ====================================================

        else:

            screen.blit(
                sprite,
                (
                    x,
                    y,
                ),
            )

        # ====================================================

        # DARKNESS

        # ====================================================

        self._draw_darkness(
            screen,
            tile,
            x,
            y,
        )

    # ========================================================

    # GET SPRITE KEY

    # ========================================================

    def _sprite_key_for_tile(
        self,
        tile,
    ):
        """

        Chuyển tile thành sprite key.



        Ví dụ:



            Woodcutter level 1

                -> ("woodcutter", 1)



            Woodcutter level 2

                -> ("woodcutter", 2)



            Quarry level 1

                -> ("quarry", 1)



            TowerOfLight level 3

                -> ("tower_of_light", 3)



            Forest

                -> ("forest", 0)



            Mushroom terrain

                -> ("mushroom", 0)

        """

        sprite_type = self._get_sprite_type(tile)

        building = getattr(
            tile,
            "building",
            None,
        )

        # ====================================================

        # TERRAIN

        # ====================================================

        if building is None:

            return (
                sprite_type,
                0,
            )

        # ====================================================

        # BUILDING

        # ====================================================

        level = self._get_tile_visual_level(tile)

        level = self._resolve_level(
            sprite_type,
            level,
        )

        return (
            sprite_type,
            level,
        )

    # ========================================================

    # GET SPRITE TYPE

    # ========================================================

    def _get_sprite_type(
        self,
        tile,
    ):
        """

        Xác định sprite type.



        BUILDING:



            Woodcutter

            icon_key = "woodcutter"



            Quarry

            icon_key = "quarry"



            TowerOfLight

            icon_key = "tower_of_light"



        TERRAIN:



            grass

            water

            forest

            rock

            mushroom

        """

        building = getattr(
            tile,
            "building",
            None,
        )

        # ====================================================

        # BUILDING

        # ====================================================

        if building is not None:

            # ------------------------------------------------

            # Ưu tiên icon_key.

            #

            # Đây chính là field building.py dành cho renderer.

            # ------------------------------------------------

            icon_key = getattr(
                building,
                "icon_key",
                None,
            )

            if icon_key:

                icon_key = self._normalize_name(icon_key)

                # Building base có icon_key = "default".

                # Nếu subclass quên override thì fallback sang key.

                if icon_key != "default":

                    return icon_key

            # ------------------------------------------------

            # FALLBACK: building.key

            # ------------------------------------------------

            building_key = getattr(
                building,
                "key",
                None,
            )

            if building_key:

                return self._normalize_name(building_key)

            # [FIX-11]
            # Building không khai báo icon_key/key không còn làm renderer crash.
            # Sentinel này sẽ không có trong self.sprites và _draw_tile sẽ
            # tự chuyển sang fallback sprite.
            return "__missing_building_sprite__"

        # ====================================================

        # TERRAIN

        # ====================================================

        terrain = getattr(
            tile,
            "terrain",
            "grass",
        )

        terrain = self._normalize_name(terrain)

        terrain = TERRAIN_ALIASES.get(
            terrain,
            terrain,
        )

        # [FIX-12]
        # Không reject terrain lạ ở đây. Nếu chưa có sprite config tương ứng,
        # _draw_tile sẽ dùng fallback. Nhờ vậy renderer chỉ lo hiển thị và
        # không làm game dừng vì dữ liệu visual mới/chưa đồng bộ.
        return terrain

    # ========================================================

    # NORMALIZE NAME

    # ========================================================

    @staticmethod
    def _normalize_name(
        value,
    ):
        """

        Chuẩn hóa String hoặc Enum.



        Ví dụ:



            "FOREST"

                -> "forest"



            Terrain.FOREST

                -> "forest"

        """

        enum_value = getattr(
            value,
            "value",
            value,
        )

        text = str(enum_value).strip().lower()

        if "." in text:

            text = text.split(".")[-1]

        return text

    # ========================================================

    # AVAILABLE LEVELS

    # ========================================================

    @staticmethod
    def _available_levels(
        sprite_type,
    ):
        """

        Ví dụ:



            forest:

                [0]



            rock:

                [0]



            mushroom:

                [0, 1, 2, 3]



            woodcutter:

                [1, 2, 3]



            quarry:

                [1, 2, 3]



            tower_of_light:

                [1, 2, 3]

        """

        return sorted(
            level
            for (
                current_type,
                level,
            ) in SPRITE_FILES.keys()
            if (current_type == sprite_type)
        )

    # ========================================================

    # RESOLVE LEVEL

    # ========================================================

    def _resolve_level(
        self,
        sprite_type,
        requested_level,
    ):
        """

        Đảm bảo level luôn có sprite hợp lệ.



        Ví dụ:



            woodcutter có:

                [1, 2, 3]



            request:

                1 -> 1

                2 -> 2

                3 -> 3

                4 -> 3



        Renderer không thay đổi building.level.

        Chỉ chọn sprite gần nhất để hiển thị.

        """

        levels = self._available_levels(sprite_type)

        if not levels:

            # [FIX-13]
            # Loại building chưa có sprite config: giữ một level hợp lý để
            # tạo key. Key đó sẽ miss ở self.sprites và được _draw_tile
            # chuyển sang fallback sprite, không raise KeyError.
            try:
                return int(requested_level)
            except (TypeError, ValueError):
                return 1

        try:

            requested_level = int(requested_level)

        except (
            TypeError,
            ValueError,
        ):

            return levels[0]

        # ====================================================

        # EXACT

        # ====================================================

        if requested_level in levels:

            return requested_level

        # ====================================================

        # BELOW MIN

        # ====================================================

        if requested_level < levels[0]:

            return levels[0]

        # ====================================================

        # ABOVE MAX

        # ====================================================

        if requested_level > levels[-1]:

            return levels[-1]

        # ====================================================

        # LEVEL BỊ THIẾU Ở GIỮA

        # ====================================================

        return min(
            levels,
            key=lambda level: abs(level - requested_level),
        )

    # ========================================================

    # DRAW UPGRADE ANIMATION

    # ========================================================

    def _draw_upgrade_animation(
        self,
        screen,
        sprite,
        x,
        y,
        elapsed,
        duration,
    ):
        """

        Hiệu ứng upgrade:



        1. Flash trắng

        2. Phóng to

        3. Nảy lên

        4. Particle

        """

        if duration <= 0:

            screen.blit(
                sprite,
                (
                    x,
                    y,
                ),
            )

            return

        # ====================================================

        # PROGRESS

        # ====================================================

        progress = elapsed / duration

        progress = max(
            0.0,
            min(
                1.0,
                progress,
            ),
        )

        # ====================================================

        # FLASH

        # ====================================================

        image = sprite

        flash_duration = 100

        if elapsed < flash_duration:

            flash_progress = 1.0 - (elapsed / flash_duration)

            flash_alpha = int(180 * flash_progress)

            image = self._create_flash_image(
                sprite,
                flash_alpha,
            )

        # ====================================================

        # SCALE

        #

        # 1.0 -> 1.15 -> 1.0

        # ====================================================

        if progress < 0.5:

            scale = 1.0 + (progress * 0.30)

        else:

            scale = 1.15 - ((progress - 0.5) * 0.30)

        # ====================================================

        # BOUNCE

        # ====================================================

        bounce_height = 8

        bounce_offset = math.sin(progress * math.pi) * bounce_height

        # ====================================================

        # SCALE IMAGE

        # ====================================================

        new_size = max(
            1,
            int(self.tile_size * scale),
        )

        animated_image = pygame.transform.smoothscale(
            image,
            (
                new_size,
                new_size,
            ),
        )

        # ====================================================

        # GIỮ SCALE Ở TÂM TILE

        # ====================================================

        draw_x = x - (new_size - self.tile_size) // 2

        draw_y = y - (new_size - self.tile_size) // 2 - int(bounce_offset)

        screen.blit(
            animated_image,
            (
                draw_x,
                draw_y,
            ),
        )

    # ========================================================

    # CREATE FLASH IMAGE

    # ========================================================

    @staticmethod
    def _create_flash_image(
        image,
        alpha,
    ):
        """

        Tạo bản sao sprite có hiệu ứng trắng sáng.

        """

        flash_image = image.copy()

        white_surface = pygame.Surface(
            flash_image.get_size(),
            pygame.SRCALPHA,
        )

        white_surface.fill(
            (
                255,
                255,
                255,
                alpha,
            )
        )

        flash_image.blit(
            white_surface,
            (
                0,
                0,
            ),
            special_flags=pygame.BLEND_RGBA_ADD,
        )

        return flash_image

    # ========================================================

    # CREATE PARTICLES

    # ========================================================

    def _create_upgrade_particles(
        self,
        row,
        col,
    ):
        """

        Tạo particle ở tâm tile.

        """

        center_x = col * self.tile_size + self.tile_size / 2

        center_y = row * self.tile_size + self.tile_size / 2

        particle_count = random.randint(
            10,
            16,
        )

        for _ in range(particle_count):

            self.particles.append(
                Particle(
                    center_x,
                    center_y,
                )
            )

    # ========================================================

    # UPDATE PARTICLES

    # ========================================================

    def _update_particles(
        self,
        dt,
    ):

        if dt <= 0:

            return

        for particle in self.particles:

            particle.update(dt)

        # Xóa particle đã chết.

        self.particles = [particle for particle in self.particles if particle.life > 0]

    # ========================================================

    # DRAW PARTICLES

    # ========================================================

    def _draw_particles(
        self,
        screen,
    ):

        for particle in self.particles:

            particle.draw(screen)

    # ========================================================

    # GET DARKNESS TARGET

    # ========================================================

    @staticmethod
    def _get_darkness_target(
        tile,
    ):
        """

        Nếu game có darkness_target:

            dùng darkness_target.



        Nếu không:

            is_dark = True  -> 1.0

            is_dark = False -> 0.0

        """

        explicit_target = getattr(
            tile,
            "darkness_target",
            None,
        )

        if explicit_target is not None:

            try:

                return max(
                    0.0,
                    min(
                        1.0,
                        float(explicit_target),
                    ),
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

        if getattr(
            tile,
            "is_dark",
            False,
        ):

            return 1.0

        return 0.0

    # ========================================================

    # UPDATE DARKNESS VISUAL

    # ========================================================

    def _update_darkness_visual(
        self,
        tile,
        dt,
    ):
        """

        Fade darkness.



        Chỉ thay đổi:

            self._darkness_values



        Không thay đổi tile.

        """

        tile_id = id(tile)

        target = self._get_darkness_target(tile)

        current = self._darkness_values.get(tile_id)

        # ====================================================

        # FIRST FRAME

        # ====================================================

        if current is None:

            initial = getattr(
                tile,
                "darkness",
                None,
            )

            if initial is not None:

                try:

                    current = float(initial)

                except (
                    TypeError,
                    ValueError,
                ):

                    current = target

            else:

                current = target

        # ====================================================

        # SPEED

        # ====================================================

        try:

            speed = float(
                getattr(
                    tile,
                    "darkness_speed",
                    1.5,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            speed = 1.5

        speed = max(
            0.0,
            speed,
        )

        # ====================================================

        # FADE

        # ====================================================

        if current < target:

            current += speed * dt

            current = min(
                current,
                target,
            )

        elif current > target:

            current -= speed * dt

            current = max(
                current,
                target,
            )

        # ====================================================

        # CLAMP

        # ====================================================

        current = max(
            0.0,
            min(
                1.0,
                current,
            ),
        )

        self._darkness_values[tile_id] = current

    # ========================================================

    # DRAW DARKNESS

    # ========================================================

    def _draw_darkness(
        self,
        screen,
        tile,
        x,
        y,
    ):

        if self.darkness_image is None:

            return

        darkness = self._darkness_values.get(
            id(tile),
            0.0,
        )

        if darkness <= 0:

            return

        alpha = int(255 * darkness)

        darkness_surface = self.darkness_image.copy()

        darkness_surface.set_alpha(alpha)

        screen.blit(
            darkness_surface,
            (
                x,
                y,
            ),
        )

    # ========================================================

    # CLEANUP INACTIVE TILE CACHE

    # ========================================================

    def _cleanup_inactive_tiles(
        self,
        active_tile_ids,
    ):
        """

        Xóa cache renderer của những Tile không còn trong grid.

        """

        cached_ids = (
            set(self._known_levels.keys())
            | set(self._upgrade_effects.keys())
            | set(self._darkness_values.keys())
        )

        inactive_ids = cached_ids - active_tile_ids

        for tile_id in inactive_ids:

            self._known_levels.pop(
                tile_id,
                None,
            )

            self._upgrade_effects.pop(
                tile_id,
                None,
            )

            self._darkness_values.pop(
                tile_id,
                None,
            )
