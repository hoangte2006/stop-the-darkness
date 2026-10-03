import pygame
import sys
import random
import math

from pathlib import Path


# =========================================================
# PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# PARTICLE
# =========================================================

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            40,
            100
        )

        self.vx = (
            math.cos(angle) * speed
        )

        self.vy = (
            math.sin(angle) * speed
        )

        self.size = random.randint(
            2,
            4
        )

        self.life = random.uniform(
            0.4,
            0.7
        )

        self.max_life = self.life


    def update(self, dt):

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Gravity nhẹ
        self.vy += 60 * dt

        self.life -= dt


    def draw(self, surface):

        if self.life <= 0:
            return

        alpha = int(
            255
            * (
                self.life
                / self.max_life
            )
        )

        particle_surface = pygame.Surface(
            (
                self.size * 2,
                self.size * 2
            ),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            particle_surface,
            (
                255,
                230,
                120,
                alpha
            ),
            (
                self.size,
                self.size
            ),
            self.size
        )

        surface.blit(
            particle_surface,
            (
                int(
                    self.x
                    - self.size
                ),
                int(
                    self.y
                    - self.size
                )
            )
        )


# =========================================================
# TILE
# =========================================================

class Tile:
    def __init__(
        self,
        tile_type,
        level=1
    ):

        self.tile_type = tile_type
        self.level = level


        # =================================================
        # UPGRADE ANIMATION
        # =================================================

        self.upgrading = False

        self.upgrade_animation_time = 0

        self.upgrade_animation_duration = 350


        # =================================================
        # FLASH
        # =================================================

        self.flash_time = 0

        self.flash_duration = 100


        # =================================================
        # DARKNESS
        # =================================================

        self.darkness = 0.0

        self.darkness_target = 0.0

        self.darkness_speed = 1.0


# =========================================================
# TILE MAP RENDERER
# =========================================================

class TileMapRenderer:
    def __init__(
        self,
        tile_size=40
    ):

        self.tile_size = tile_size

        self.tiles = {}

        self.darkness_image = None


    # =====================================================
    # LOAD SPRITES
    # =====================================================

    def load_sprites(self):

        sprite_paths = {

            # TREE
            ("tree", 1):
                BASE_DIR
                / "assets/images/sprites/trees/tree-1.png",

            ("tree", 2):
                BASE_DIR
                / "assets/images/sprites/trees/tree-2.png",

            ("tree", 3):
                BASE_DIR
                / "assets/images/sprites/trees/tree-3.png",


            # STONE
            ("stone", 1):
                BASE_DIR
                / "assets/images/sprites/stone/stone-1.png",

            ("stone", 2):
                BASE_DIR
                / "assets/images/sprites/stone/stone-2.png",

            ("stone", 3):
                BASE_DIR
                / "assets/images/sprites/stone/stone-3.png",


            # BUILDING
            ("building", 1):
                BASE_DIR
                / "assets/images/sprites/structure/building-1.png",

            ("building", 2):
                BASE_DIR
                / "assets/images/sprites/structure/building-2.png",

            ("building", 3):
                BASE_DIR
                / "assets/images/sprites/structure/building-3.png",


            # STATIC
            ("ground", 1):
                BASE_DIR
                / "assets/images/sprites/ground/ground.png",

            ("water", 1):
                BASE_DIR
                / "assets/images/sprites/water/water.png",
        }


        for key, filepath in sprite_paths.items():

            if not filepath.exists():

                print(
                    f"Lỗi: Không tìm thấy ảnh:"
                )

                print(filepath)

                sys.exit()


            image = pygame.image.load(
                str(filepath)
            ).convert_alpha()


            image = pygame.transform.scale(
                image,
                (
                    self.tile_size,
                    self.tile_size
                )
            )


            self.tiles[key] = image


        # =================================================
        # DARKNESS
        # =================================================

        darkness_path = (
            BASE_DIR
            / "assets/images/sprites/darkness/darkness.png"
        )


        if not darkness_path.exists():

            print(
                "Lỗi: Không tìm thấy ảnh:"
            )

            print(darkness_path)

            sys.exit()


        self.darkness_image = pygame.image.load(
            str(darkness_path)
        ).convert_alpha()


        self.darkness_image = pygame.transform.scale(
            self.darkness_image,
            (
                self.tile_size,
                self.tile_size
            )
        )


    # =====================================================
    # WHITE FLASH
    # =====================================================

    def create_flash_image(
        self,
        image,
        alpha
    ):

        flash_image = image.copy()


        white = pygame.Surface(
            flash_image.get_size(),
            pygame.SRCALPHA
        )


        white.fill(
            (
                255,
                255,
                255,
                alpha
            )
        )


        flash_image.blit(
            white,
            (
                0,
                0
            ),
            special_flags=pygame.BLEND_RGBA_ADD
        )


        return flash_image


    # =====================================================
    # DRAW TILE
    # =====================================================

    def draw_tile(
        self,
        surface,
        tile,
        row,
        col
    ):

        x = (
            col
            * self.tile_size
        )

        y = (
            row
            * self.tile_size
        )


        key = (
            tile.tile_type,
            tile.level
        )


        if key not in self.tiles:
            return


        original_image = (
            self.tiles[key]
        )


        image = original_image


        # =================================================
        # FLASH WHITE
        # =================================================

        if tile.flash_time > 0:

            flash_progress = (
                tile.flash_time
                / tile.flash_duration
            )


            flash_alpha = int(
                180
                * flash_progress
            )


            image = (
                self.create_flash_image(
                    original_image,
                    flash_alpha
                )
            )


        # =================================================
        # UPGRADE ANIMATION
        # =================================================

        if tile.upgrading:

            progress = (
                tile.upgrade_animation_time
                / tile.upgrade_animation_duration
            )


            # ---------------------------------------------
            # SCALE
            # ---------------------------------------------

            if progress < 0.5:

                scale = (
                    1.0
                    + progress * 0.30
                )

            else:

                scale = (
                    1.15
                    - (
                        progress - 0.5
                    ) * 0.30
                )


            # ---------------------------------------------
            # BOUNCE
            # ---------------------------------------------

            bounce_height = 8


            bounce_offset = (
                math.sin(
                    progress
                    * math.pi
                )
                * bounce_height
            )


            new_size = int(
                self.tile_size
                * scale
            )


            animated_image = (
                pygame.transform.smoothscale(
                    image,
                    (
                        new_size,
                        new_size
                    )
                )
            )


            draw_x = (
                x
                - (
                    new_size
                    - self.tile_size
                ) // 2
            )


            draw_y = (
                y
                - (
                    new_size
                    - self.tile_size
                ) // 2
                - bounce_offset
            )


            surface.blit(
                animated_image,
                (
                    draw_x,
                    draw_y
                )
            )


        else:

            surface.blit(
                image,
                (
                    x,
                    y
                )
            )


        # =================================================
        # DARKNESS
        # =================================================

        if tile.darkness > 0:

            darkness_surface = (
                self.darkness_image.copy()
            )


            alpha = int(
                255
                * tile.darkness
            )


            darkness_surface.set_alpha(
                alpha
            )


            surface.blit(
                darkness_surface,
                (
                    x,
                    y
                )
            )


    # =====================================================
    # DRAW MAP
    # =====================================================

    def draw(
        self,
        surface,
        grid_matrix
    ):

        for row_idx, row in enumerate(
            grid_matrix
        ):

            for col_idx, tile in enumerate(
                row
            ):

                self.draw_tile(
                    surface,
                    tile,
                    row_idx,
                    col_idx
                )


# =========================================================
# SELECTED TILE GLOW
# =========================================================

def draw_selected_tile(
    surface,
    row,
    col,
    tile_size
):

    if (
        row is None
        or col is None
    ):
        return


    x = (
        col
        * tile_size
    )

    y = (
        row
        * tile_size
    )


    # =====================================================
    # PULSE
    # =====================================================

    time = pygame.time.get_ticks()


    pulse = (
        math.sin(
            time * 0.006
        )
        + 1
    ) / 2


    glow_alpha = int(
        80
        + pulse * 120
    )


    border_width = int(
        2
        + pulse * 2
    )


    glow_size = 8


    glow_surface = pygame.Surface(
        (
            tile_size
            + glow_size * 2,

            tile_size
            + glow_size * 2
        ),
        pygame.SRCALPHA
    )


    glow_rect = pygame.Rect(
        glow_size,
        glow_size,
        tile_size,
        tile_size
    )


    # =====================================================
    # GLOW NGOÀI
    # =====================================================

    pygame.draw.rect(
        glow_surface,
        (
            255,
            220,
            60,
            glow_alpha // 4
        ),
        glow_rect,
        width=8,
        border_radius=5
    )


    pygame.draw.rect(
        glow_surface,
        (
            255,
            235,
            100,
            glow_alpha // 2
        ),
        glow_rect,
        width=5,
        border_radius=4
    )


    surface.blit(
        glow_surface,
        (
            x - glow_size,
            y - glow_size
        )
    )


    # =====================================================
    # VIỀN CHÍNH
    # =====================================================

    pygame.draw.rect(
        surface,
        (
            255,
            245,
            140
        ),
        (
            x + 1,
            y + 1,
            tile_size - 2,
            tile_size - 2
        ),
        width=border_width,
        border_radius=3
    )


# =========================================================
# SPIRAL
# =========================================================

def get_spiral_coordinates(
    rows,
    cols
):

    coords = []


    top = 0
    bottom = rows - 1

    left = 0
    right = cols - 1


    while (
        top <= bottom
        and left <= right
    ):

        # Trái -> phải

        for i in range(
            left,
            right + 1
        ):

            coords.append(
                (
                    top,
                    i
                )
            )


        top += 1


        # Trên -> dưới

        for i in range(
            top,
            bottom + 1
        ):

            coords.append(
                (
                    i,
                    right
                )
            )


        right -= 1


        # Phải -> trái

        if top <= bottom:

            for i in range(
                right,
                left - 1,
                -1
            ):

                coords.append(
                    (
                        bottom,
                        i
                    )
                )


            bottom -= 1


        # Dưới -> trên

        if left <= right:

            for i in range(
                bottom,
                top - 1,
                -1
            ):

                coords.append(
                    (
                        i,
                        left
                    )
                )


            left += 1


    return coords


# =========================================================
# PARTICLES
# =========================================================

particles = []


def create_upgrade_particles(
    row,
    col,
    tile_size
):

    center_x = (
        col * tile_size
        + tile_size / 2
    )


    center_y = (
        row * tile_size
        + tile_size / 2
    )


    particle_count = (
        random.randint(
            10,
            16
        )
    )


    for _ in range(
        particle_count
    ):

        particles.append(
            Particle(
                center_x,
                center_y
            )
        )


def update_particles(dt):

    for particle in particles:
        particle.update(dt)


    particles[:] = [

        particle

        for particle in particles

        if particle.life > 0
    ]


def draw_particles(surface):

    for particle in particles:

        particle.draw(
            surface
        )


# =========================================================
# UPDATE TILE
# =========================================================

def update_tiles(
    level_matrix,
    delta_time
):

    dt = (
        delta_time
        / 1000.0
    )


    for row in level_matrix:

        for tile in row:


            # =================================================
            # UPGRADE
            # =================================================

            if tile.upgrading:

                tile.upgrade_animation_time += (
                    delta_time
                )


                if (
                    tile.upgrade_animation_time
                    >= tile.upgrade_animation_duration
                ):

                    tile.upgrading = False

                    tile.upgrade_animation_time = 0


            # =================================================
            # FLASH
            # =================================================

            if tile.flash_time > 0:

                tile.flash_time -= (
                    delta_time
                )


                if tile.flash_time < 0:

                    tile.flash_time = 0


            # =================================================
            # DARKNESS
            # =================================================

            if (
                tile.darkness
                < tile.darkness_target
            ):

                tile.darkness += (
                    tile.darkness_speed
                    * dt
                )


                if (
                    tile.darkness
                    > tile.darkness_target
                ):

                    tile.darkness = (
                        tile.darkness_target
                    )


# =========================================================
# UPGRADE TILE
# =========================================================

def upgrade_tile(
    tile,
    row,
    col
):

    upgradeable_types = {
        "tree",
        "stone",
        "building",
    }


    # Không phải object nâng cấp được
    if (
        tile.tile_type
        not in upgradeable_types
    ):
        return


    # Bóng tối quá nhiều
    if tile.darkness > 0.5:

        print(
            "Không thể nâng cấp: "
            "ô đang bị bóng tối chiếm."
        )

        return


    # Max level
    if tile.level >= 3:

        print(
            f"{tile.tile_type} "
            "đã đạt level tối đa!"
        )

        return


    # Đang animation
    if tile.upgrading:
        return


    # =====================================================
    # LEVEL UP
    # =====================================================

    tile.level += 1


    # =====================================================
    # EFFECT 1 - BOUNCE
    # =====================================================

    tile.upgrading = True

    tile.upgrade_animation_time = 0


    # =====================================================
    # EFFECT 2 - FLASH
    # =====================================================

    tile.flash_time = (
        tile.flash_duration
    )


    # =====================================================
    # EFFECT 3 - PARTICLES
    # =====================================================

    create_upgrade_particles(
        row,
        col,
        TILE_SIZE
    )


    print(
        f"{tile.tile_type} "
        f"đã nâng lên level "
        f"{tile.level}"
    )


# =========================================================
# DRAW SIDE PANEL
# =========================================================

def draw_side_panel(
    surface,
    selected_tile,
    panel_rect,
    font_title,
    font_normal,
    font_button
):

    # =====================================================
    # BACKGROUND
    # =====================================================

    pygame.draw.rect(
        surface,
        (
            28,
            31,
            38
        ),
        panel_rect
    )


    # Đường ngăn cách map / panel

    pygame.draw.line(
        surface,
        (
            80,
            84,
            95
        ),
        (
            panel_rect.x,
            0
        ),
        (
            panel_rect.x,
            panel_rect.height
        ),
        2
    )


    # =====================================================
    # CHƯA CHỌN TILE
    # =====================================================

    if selected_tile is None:

        text = font_normal.render(
            "Hãy nâng cấp công trình nhanh nào!",
            True,
            (
                190,
                190,
                190
            )
        )


        text_rect = text.get_rect(
            center=(
                panel_rect.centerx,
                80
            )
        )


        surface.blit(
            text,
            text_rect
        )


        return None


    # =====================================================
    # TITLE
    # =====================================================

    names = {
        "tree": "TREE",
        "stone": "STONE",
        "building": "BUILDING",
    }


    display_name = names.get(
        selected_tile.tile_type,
        selected_tile.tile_type.upper()
    )


    title_surface = (
        font_title.render(
            display_name,
            True,
            (
                255,
                240,
                170
            )
        )
    )


    title_rect = (
        title_surface.get_rect(
            center=(
                panel_rect.centerx,
                65
            )
        )
    )


    surface.blit(
        title_surface,
        title_rect
    )


    # =====================================================
    # LEVEL
    # =====================================================

    level_surface = (
        font_normal.render(
            f"Level: {selected_tile.level} / 3",
            True,
            (
                230,
                230,
                230
            )
        )
    )


    level_rect = (
        level_surface.get_rect(
            center=(
                panel_rect.centerx,
                115
            )
        )
    )


    surface.blit(
        level_surface,
        level_rect
    )


    # =====================================================
    # SAU NÀY THÊM THÔNG TIN
    # =====================================================

    placeholder = (
        font_normal.render(
            "Thông tin nâng cấp sẽ thêm sau",
            True,
            (
                140,
                145,
                155
            )
        )
    )


    placeholder_rect = (
        placeholder.get_rect(
            center=(
                panel_rect.centerx,
                165
            )
        )
    )


    surface.blit(
        placeholder,
        placeholder_rect
    )


    # =====================================================
    # BUTTON
    # =====================================================

    button_width = (
        panel_rect.width
        - 60
    )

    button_height = 52


    button_rect = pygame.Rect(
        panel_rect.x + 30,
        panel_rect.bottom - 90,
        button_width,
        button_height
    )


    mouse_pos = (
        pygame.mouse.get_pos()
    )


    hovering = (
        button_rect.collidepoint(
            mouse_pos
        )
    )


    can_upgrade = True


    button_text = "NÂNG CẤP"


    # =====================================================
    # BUTTON STATE
    # =====================================================

    if selected_tile.level >= 3:

        can_upgrade = False

        button_text = (
            "ĐÃ MAX LEVEL"
        )


    elif selected_tile.darkness > 0.5:

        can_upgrade = False

        button_text = (
            "BỊ BÓNG TỐI CHIẾM"
        )


    elif selected_tile.upgrading:

        can_upgrade = False

        button_text = (
            "ĐANG NÂNG CẤP..."
        )


    # =====================================================
    # BUTTON COLOR
    # =====================================================

    if not can_upgrade:

        button_color = (
            75,
            78,
            85
        )


    elif hovering:

        button_color = (
            205,
            164,
            45
        )


    else:

        button_color = (
            177,
            137,
            32
        )


    # Shadow

    shadow_rect = (
        button_rect.copy()
    )

    shadow_rect.y += 4


    pygame.draw.rect(
        surface,
        (
            15,
            15,
            18
        ),
        shadow_rect,
        border_radius=8
    )


    pygame.draw.rect(
        surface,
        button_color,
        button_rect,
        border_radius=8
    )


    # Button border

    pygame.draw.rect(
        surface,
        (
            240,
            210,
            110
        ),
        button_rect,
        width=2,
        border_radius=8
    )


    text_color = (
        255,
        255,
        255
    )


    button_surface = (
        font_button.render(
            button_text,
            True,
            text_color
        )
    )


    button_text_rect = (
        button_surface.get_rect(
            center=button_rect.center
        )
    )


    surface.blit(
        button_surface,
        button_text_rect
    )


    # Trả button_rect về để xử lý click
    return button_rect


# =========================================================
# GAME INIT
# =========================================================

pygame.init()


ROWS = 12

COLS = 16

TILE_SIZE = 40


# =========================================================
# SIZE
# =========================================================

MAP_WIDTH = (
    COLS
    * TILE_SIZE
)

MAP_HEIGHT = (
    ROWS
    * TILE_SIZE
)


# Map = 2/3 màn hình
# Panel = 1/3 màn hình
#
# Map width = 640
# Panel width = 320
# Total = 960

PANEL_WIDTH = (
    MAP_WIDTH // 2
)


SCREEN_WIDTH = (
    MAP_WIDTH
    + PANEL_WIDTH
)


SCREEN_HEIGHT = (
    MAP_HEIGHT
)


screen = pygame.display.set_mode(
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
)


pygame.display.set_caption(
    "Bóng tối lấn chiếm xoắn ốc"
)


# =========================================================
# FONT
# =========================================================

font_title = pygame.font.SysFont(
    "arial",
    28,
    bold=True
)


font_normal = pygame.font.SysFont(
    "arial",
    16
)


font_button = pygame.font.SysFont(
    "arial",
    18,
    bold=True
)


# =========================================================
# PANEL RECT
# =========================================================

panel_rect = pygame.Rect(
    MAP_WIDTH,
    0,
    PANEL_WIDTH,
    SCREEN_HEIGHT
)


# =========================================================
# RENDERER
# =========================================================

renderer = TileMapRenderer(
    TILE_SIZE
)

renderer.load_sprites()


# =========================================================
# MAP RANDOM
# =========================================================

tile_types = [

    "tree",

    "ground",

    "water",

    "stone",

    "building",
]


level_matrix = []


for row in range(
    ROWS
):

    row_tiles = []


    for col in range(
        COLS
    ):

        tile_type = (
            random.choice(
                tile_types
            )
        )


        tile = Tile(
            tile_type,
            level=1
        )


        row_tiles.append(
            tile
        )


    level_matrix.append(
        row_tiles
    )


# =========================================================
# SPIRAL
# =========================================================

spiral_path = (
    get_spiral_coordinates(
        ROWS,
        COLS
    )
)


current_step = 0


# =========================================================
# DARKNESS EVENT
# =========================================================

DARKNESS_SPREAD_EVENT = (
    pygame.USEREVENT
    + 1
)


pygame.time.set_timer(
    DARKNESS_SPREAD_EVENT,
    2000
)


# =========================================================
# SELECTED TILE
# =========================================================

selected_row = None

selected_col = None

selected_tile = None


# =========================================================
# UPGRADE BUTTON RECT
# =========================================================

upgrade_button_rect = None


# =========================================================
# CLOCK
# =========================================================

clock = pygame.time.Clock()


# =========================================================
# GAME LOOP
# =========================================================

running = True


while running:

    delta_time = (
        clock.tick(
            60
        )
    )


    dt = (
        delta_time
        / 1000.0
    )


    # =====================================================
    # EVENT
    # =====================================================

    for event in pygame.event.get():


        # =================================================
        # QUIT
        # =================================================

        if event.type == pygame.QUIT:

            running = False


        # =================================================
        # LEFT CLICK
        # =================================================

        elif (
            event.type
            == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):

            mouse_x, mouse_y = (
                event.pos
            )


            # =============================================
            # CLICK TRONG MAP
            # =============================================

            if mouse_x < MAP_WIDTH:

                col = (
                    mouse_x
                    // TILE_SIZE
                )

                row = (
                    mouse_y
                    // TILE_SIZE
                )


                if (
                    0 <= row < ROWS
                    and
                    0 <= col < COLS
                ):

                    tile = (
                        level_matrix[
                            row
                        ][
                            col
                        ]
                    )


                    selectable_types = {
                        "tree",
                        "stone",
                        "building",
                    }


                    # =====================================
                    # CHỈ CHỌN OBJECT CÓ THỂ UPGRADE
                    # =====================================

                    if (
                        tile.tile_type
                        in selectable_types
                    ):

                        selected_row = row

                        selected_col = col

                        selected_tile = tile


                    # =====================================
                    # CLICK GROUND/WATER -> BỎ CHỌN
                    # =====================================

                    else:

                        selected_row = None

                        selected_col = None

                        selected_tile = None


            # =============================================
            # CLICK BUTTON UPGRADE
            # =============================================

            else:

                if (
                    upgrade_button_rect
                    is not None
                    and
                    upgrade_button_rect.collidepoint(
                        event.pos
                    )
                    and
                    selected_tile
                    is not None
                ):

                    upgrade_tile(
                        selected_tile,
                        selected_row,
                        selected_col
                    )


        # =================================================
        # DARKNESS
        # =================================================

        elif (
            event.type
            == DARKNESS_SPREAD_EVENT
        ):

            if (
                current_step
                < len(
                    spiral_path
                )
            ):

                r, c = (
                    spiral_path[
                        current_step
                    ]
                )


                tile = (
                    level_matrix[
                        r
                    ][
                        c
                    ]
                )


                tile.darkness_target = 1.0


                current_step += 1


    # =====================================================
    # UPDATE
    # =====================================================

    update_tiles(
        level_matrix,
        delta_time
    )


    update_particles(
        dt
    )


    # =====================================================
    # DRAW
    # =====================================================

    screen.fill(
        (
            0,
            0,
            0
        )
    )


    # =====================================================
    # MAP
    # =====================================================

    renderer.draw(
        screen,
        level_matrix
    )


    # =====================================================
    # SELECTED GLOW
    # =====================================================

    draw_selected_tile(
        screen,
        selected_row,
        selected_col,
        TILE_SIZE
    )


    # =====================================================
    # PARTICLES
    # =====================================================

    draw_particles(
        screen
    )


    # =====================================================
    # SIDE PANEL
    # =====================================================

    upgrade_button_rect = (
        draw_side_panel(
            screen,
            selected_tile,
            panel_rect,
            font_title,
            font_normal,
            font_button
        )
    )


    # =====================================================
    # DISPLAY
    # =====================================================

    pygame.display.flip()


# =========================================================
# EXIT
# =========================================================

pygame.quit()

sys.exit()