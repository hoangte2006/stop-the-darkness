"""
UI Package - File: sidebar.py
Quản lý thanh điều khiển bên phải màn hình.
Bao gồm: Tài nguyên, tốc độ, nâng cấp, phá dỡ, buff ô kề, preview buff và màn Thống kê / Achievements.
"""

import pygame
from core.constants import SIDEBAR_X, SIDEBAR_WIDTH, SCREEN_HEIGHT
from entities.building import BUILDING_TYPES
from ui.button import Button
from core import rules


class Sidebar:
    """Lớp Sidebar chứa các thành phần giao diện hiển thị thông tin trò chơi."""

    def __init__(self):
        self.sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)

        self.font_title = pygame.font.SysFont("Verdana", 15, bold=True)
        self.font_normal = pygame.font.SysFont("Verdana", 12)
        self.font_small = pygame.font.SysFont("Verdana", 10)

        self.bg_color = (15, 18, 22)
        self.text_color = (200, 200, 205)
        self.current_speed = 1

        # Màn Thống kê / Achievements (Nhiệm vụ 3)
        self.show_stats_modal = False
        self.stats = {
            "buildings_built": 0,
            "highest_level": 1,
            "wins": 0,
            "losses": 0,
        }

        self._initialize_speed_buttons()

        # Nút bật/tắt bảng Thống kê
        self.stats_button = Button(
            rect=(self.sidebar_rect.x + 20, 145, self.sidebar_rect.width - 40, 26),
            text="Achievements / Stats",
            font=self.font_small,
            bg_color=(35, 45, 60),
            hover_color=(55, 75, 105),
        )

        # Nút đóng modal Thống kê
        self.close_stats_button = Button(
            rect=(SIDEBAR_X - 220, 410, 100, 30),
            text="Close",
            font=self.font_normal,
            bg_color=(80, 40, 40),
            hover_color=(120, 50, 50),
        )

        # Nút nâng cấp
        self.upgrade_button = Button(
            rect=(self.sidebar_rect.x + 20, 380, self.sidebar_rect.width - 40, 32),
            text="Upgrade Building",
            font=self.font_normal,
            bg_color=(45, 100, 50),
            hover_color=(60, 130, 70),
        )

        # Nút phá dỡ
        self.demolish_button = Button(
            rect=(self.sidebar_rect.x + 20, 420, self.sidebar_rect.width - 40, 30),
            text="Demolish / Sell",
            font=self.font_normal,
            bg_color=(140, 45, 45),
            hover_color=(180, 60, 60),
        )

        self.build_buttons: dict[str, Button] = {}
        self._initialize_build_buttons()

    def _initialize_speed_buttons(self) -> None:
        btn_width, btn_height = 40, 24
        start_x = self.sidebar_rect.x + 20
        y_pos = 110
        spacing = 5

        self.btn_pause = Button((start_x, y_pos, btn_width, btn_height), "||", self.font_normal)
        self.btn_1x = Button((start_x + (btn_width + spacing) * 1, y_pos, btn_width, btn_height), "1x", self.font_normal)
        self.btn_2x = Button((start_x + (btn_width + spacing) * 2, y_pos, btn_width, btn_height), "2x", self.font_normal)
        self.btn_3x = Button((start_x + (btn_width + spacing) * 3, y_pos, btn_width, btn_height), "3x", self.font_normal)

        self.speed_buttons = [self.btn_pause, self.btn_1x, self.btn_2x, self.btn_3x]

    def _initialize_build_buttons(self) -> None:
        start_y_position = 275
        for index, (building_key, building_class) in enumerate(BUILDING_TYPES.items()):
            button_y = start_y_position + index * 52

            eng_name = getattr(building_class, "name", "Building")
            if eng_name in ["Nhà đốn gỗ", "Woodcutter"]:
                eng_name = "Lumber Camp"
            elif eng_name in ["Mỏ đá", "Quarry"]:
                eng_name = "Stone Quarry"
            elif eng_name in ["Tháp ánh sáng", "Tower of Light"]:
                eng_name = "Light Tower"

            self.build_buttons[building_key] = Button(
                rect=(self.sidebar_rect.x + 20, button_y, self.sidebar_rect.width - 40, 32),
                text=f"Build {eng_name}",
                font=self.font_normal,
            )

    def _has_enough_resources(self, required_cost: dict[str, int], current_resources: dict[str, int]) -> bool:
        return all(current_resources.get(k, 0) >= v for k, v in required_cost.items())

    def _get_buff_info(self, game_state, row: int, col: int, building_key: str) -> str:
        target_terrain = None
        key_str = str(building_key).lower()
        if "lumber" in key_str or "wood" in key_str:
            target_terrain = "forest"
        elif "quarry" in key_str or "stone" in key_str or "mine" in key_str:
            target_terrain = "rock"

        if target_terrain and hasattr(rules, "count_adjacent_terrain"):
            count = rules.count_adjacent_terrain(game_state.grid, row, col, target_terrain)
            if count > 0:
                buff_percent = count * 20
                return f"+{buff_percent}% do {count} o ke"
        return ""

    def handle_event(self, event: pygame.event.Event, game_state, audio=None) -> None:
        # 1. Xử lý modal Thống kê
        if self.show_stats_modal:
            if self.close_stats_button.handle_event(event):
                self.show_stats_modal = False
            return

        if self.stats_button.handle_event(event):
            self.show_stats_modal = True
            return

        # 2. Xử lý các nút tốc độ
        if self.btn_pause.handle_event(event):
            game_state.is_paused = not getattr(game_state, "is_paused", False)
        elif self.btn_1x.handle_event(event):
            game_state.is_paused = False
            self.current_speed = 1
            if hasattr(game_state, "set_speed"):
                game_state.set_speed(1)
        elif self.btn_2x.handle_event(event):
            game_state.is_paused = False
            self.current_speed = 2
            if hasattr(game_state, "set_speed"):
                game_state.set_speed(2)
        elif self.btn_3x.handle_event(event):
            game_state.is_paused = False
            self.current_speed = 3
            if hasattr(game_state, "set_speed"):
                game_state.set_speed(3)

        # 3. Xử lý tương tác ô đất
        selected_tile = getattr(game_state, "selected_tile", None)
        if not selected_tile:
            return

        if getattr(selected_tile, "building", None):
            if self.upgrade_button.handle_event(event):
                if hasattr(game_state, "upgrade_building"):
                    game_state.upgrade_building(selected_tile.row, selected_tile.col)
                cur_lvl = getattr(selected_tile.building, "level", 1)
                if cur_lvl > self.stats["highest_level"]:
                    self.stats["highest_level"] = cur_lvl
            elif self.demolish_button.handle_event(event):
                if hasattr(game_state, "remove_building"):
                    game_state.remove_building(selected_tile.row, selected_tile.col)
        elif not getattr(selected_tile, "is_dark", False):
            for building_key, button in self.build_buttons.items():
                if button.handle_event(event):
                    if hasattr(game_state, "add_building"):
                        game_state.add_building(selected_tile.row, selected_tile.col, building_key)
                    self.stats["buildings_built"] += 1
                    break

    def update(self, game_state) -> None:
        mouse_position = pygame.mouse.get_pos()

        if getattr(game_state, "is_game_over", False):
            if getattr(game_state, "is_victory", False):
                self.stats["wins"] = max(1, self.stats["wins"])
            else:
                self.stats["losses"] = max(1, self.stats["losses"])

        if self.show_stats_modal:
            self.close_stats_button.is_hovered = self.close_stats_button.rect.collidepoint(mouse_position)
            return

        self.stats_button.is_hovered = self.stats_button.rect.collidepoint(mouse_position)

        ACTIVE_COLOR = (80, 120, 180)
        PAUSE_COLOR = (180, 60, 60)
        NORMAL_COLOR = (45, 50, 60)

        is_paused = getattr(game_state, "is_paused", False)
        self.btn_pause.bg_color = PAUSE_COLOR if is_paused else NORMAL_COLOR

        is_running = not is_paused
        self.btn_1x.bg_color = ACTIVE_COLOR if (self.current_speed == 1 and is_running) else NORMAL_COLOR
        self.btn_2x.bg_color = ACTIVE_COLOR if (self.current_speed == 2 and is_running) else NORMAL_COLOR
        self.btn_3x.bg_color = ACTIVE_COLOR if (self.current_speed == 3 and is_running) else NORMAL_COLOR

        for btn in self.speed_buttons:
            btn.is_hovered = btn.rect.collidepoint(mouse_position)

        selected_tile = getattr(game_state, "selected_tile", None)

        if selected_tile and getattr(selected_tile, "building", None) and not getattr(selected_tile, "is_dark", False):
            b = selected_tile.building
            is_max = getattr(b, "level", 1) >= getattr(b, "max_level", 3)
            can_afford = hasattr(b, "cost_for_next_level") and self._has_enough_resources(
                b.cost_for_next_level(), getattr(game_state, "resources", {})
            )
            self.upgrade_button.is_enabled = (not is_max) and can_afford
            self.upgrade_button.is_hovered = self.upgrade_button.rect.collidepoint(mouse_position)

            self.demolish_button.is_enabled = True
            self.demolish_button.is_hovered = self.demolish_button.rect.collidepoint(mouse_position)
        else:
            self.upgrade_button.is_enabled = False
            self.demolish_button.is_enabled = False

        for building_key, button in self.build_buttons.items():
            button.is_hovered = button.rect.collidepoint(mouse_position)
            if selected_tile and getattr(selected_tile, "building", None) is None and not getattr(selected_tile, "is_dark", False):
                b_class = BUILDING_TYPES[building_key]
                button.is_enabled = self._has_enough_resources(
                    getattr(b_class, "base_cost", {}), getattr(game_state, "resources", {})
                )
            else:
                button.is_enabled = False

    def draw(self, screen: pygame.Surface, game_state) -> None:
        pygame.draw.rect(screen, self.bg_color, self.sidebar_rect)
        pygame.draw.line(screen, (60, 65, 75), (self.sidebar_rect.x, 0), (self.sidebar_rect.x, SCREEN_HEIGHT), 2)

        resources = getattr(game_state, "resources", {})
        screen.blit(self.font_title.render("RESOURCES", True, (240, 200, 100)), (self.sidebar_rect.x + 15, 12))
        res_texts = [
            f"Wood: {resources.get('wood', 0)}",
            f"Stone: {resources.get('stone', 0)}",
            f"Light: {resources.get('light', 0)}",
        ]
        for index, text in enumerate(res_texts):
            screen.blit(self.font_normal.render(text, True, self.text_color), (self.sidebar_rect.x + 20, 36 + index * 18))

        for btn in self.speed_buttons:
            btn.draw(screen)
        self.stats_button.draw(screen)

        pygame.draw.line(screen, (40, 45, 55), (self.sidebar_rect.x + 10, 180), (self.sidebar_rect.right - 10, 180))

        selected_tile = getattr(game_state, "selected_tile", None)
        if not selected_tile:
            screen.blit(self.font_normal.render("Select a tile on map...", True, (120, 120, 120)), (self.sidebar_rect.x + 15, 195))
            self._draw_stats_modal(screen)
            return

        terrain_type = getattr(selected_tile, "terrain", "grass")
        terrain_color = (150, 255, 150) if terrain_type == "grass" else (100, 200, 255)
        terrain_text = f"Tile [{selected_tile.row}, {selected_tile.col}] - {terrain_type.upper()}"
        screen.blit(self.font_title.render(terrain_text, True, terrain_color), (self.sidebar_rect.x + 15, 195))

        is_dark = getattr(selected_tile, "is_dark", False)
        is_lighted = getattr(selected_tile, "is_lighted", False)
        status_text = "Consumed!" if is_dark else ("Illuminated" if is_lighted else "In Darkness")
        status_color = (255, 80, 80) if is_dark else ((255, 255, 100) if is_lighted else (150, 150, 150))
        screen.blit(self.font_normal.render(f"Status: {status_text}", True, status_color), (self.sidebar_rect.x + 15, 218))

        if getattr(selected_tile, "building", None):
            b = selected_tile.building
            b_name = getattr(b, "name", "Building")
            b_lvl = getattr(b, "level", 1)
            b_max = getattr(b, "max_level", 3)
            title = f"{b_name} (Lv {b_lvl}/{b_max})"
            screen.blit(self.font_title.render(title, True, (100, 220, 255)), (self.sidebar_rect.x + 15, 250))

            buff_info = self._get_buff_info(game_state, selected_tile.row, selected_tile.col, getattr(b, "key", b_name))
            if buff_info:
                screen.blit(self.font_small.render(f"Buff: {buff_info}", True, (120, 255, 120)), (self.sidebar_rect.x + 15, 275))

            if self.upgrade_button.is_hovered and b_lvl < b_max and hasattr(b, "cost_for_next_level"):
                cost_dict = b.cost_for_next_level()
                cost_str = " | ".join([f"{v} {k}" for k, v in cost_dict.items()])
                screen.blit(self.font_small.render(f"Cost: {cost_str}", True, (255, 255, 150)), (self.sidebar_rect.x + 20, 362))

            self.upgrade_button.draw(screen)
            self.demolish_button.draw(screen)

        elif not is_dark:
            screen.blit(self.font_title.render("BUILDINGS", True, (240, 200, 100)), (self.sidebar_rect.x + 15, 250))
            for building_key, button in self.build_buttons.items():
                button.draw(screen)

                if button.is_hovered:
                    cost_dict = getattr(BUILDING_TYPES[building_key], "base_cost", {})
                    cost_str = " | ".join([f"{v} {k}" for k, v in cost_dict.items()])
                    screen.blit(self.font_small.render(f"Cost: {cost_str}", True, (255, 255, 150)), (button.rect.x, button.rect.bottom + 2))

                    preview_buff = self._get_buff_info(game_state, selected_tile.row, selected_tile.col, building_key)
                    if preview_buff:
                        screen.blit(self.font_small.render(f"Preview: {preview_buff}", True, (120, 255, 120)), (button.rect.x, button.rect.bottom + 14))

        self._draw_stats_modal(screen)

    def _draw_stats_modal(self, screen: pygame.Surface) -> None:
        if not self.show_stats_modal:
            return

        modal_rect = pygame.Rect(SIDEBAR_X - 320, 150, 300, 310)

        pygame.draw.rect(screen, (20, 24, 32), modal_rect, border_radius=8)
        pygame.draw.rect(screen, (210, 175, 80), modal_rect, width=2, border_radius=8)

        title = self.font_title.render("ACHIEVEMENTS / STATS", True, (240, 200, 100))
        screen.blit(title, (modal_rect.x + 20, modal_rect.y + 20))

        stat_lines = [
            f"Buildings Built: {self.stats['buildings_built']}",
            f"Highest Building Level: Lv {self.stats['highest_level']}",
            f"Total Victories: {self.stats['wins']}",
            f"Total Defeats: {self.stats['losses']}",
        ]
        for idx, line in enumerate(stat_lines):
            surf = self.font_normal.render(line, True, (220, 225, 230))
            screen.blit(surf, (modal_rect.x + 25, modal_rect.y + 65 + idx * 30))

        self.close_stats_button.rect.topleft = (modal_rect.x + 100, modal_rect.y + 250)
        self.close_stats_button.draw(screen)