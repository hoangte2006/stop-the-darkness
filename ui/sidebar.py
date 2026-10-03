"""
UI Package - File: sidebar.py
Manages the right-side control panel.
Displays resources, tile info, speed controls, and building interactions.
"""

import pygame
from core.constants import SIDEBAR_X, SIDEBAR_WIDTH, SCREEN_HEIGHT
from entities.building import BUILDING_TYPES
from ui.button import Button

class Sidebar:
    """ Sidebar class containing game UI elements and interactions. """

    def __init__(self):
        self.sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        
        self.font_title = pygame.font.SysFont("Verdana", 16, bold=True)
        self.font_normal = pygame.font.SysFont("Verdana", 12)
        self.font_small = pygame.font.SysFont("Verdana", 10)
        
        self.bg_color = (15, 18, 22)
        self.text_color = (200, 200, 205)
        self.current_speed = 1 
        
        self._initialize_speed_buttons()

        # Upgrade Button
        self.upgrade_button = Button(
            rect=(self.sidebar_rect.x + 20, 360, self.sidebar_rect.width - 40, 35),
            text="Upgrade Building",
            font=self.font_normal,
            bg_color=(45, 100, 50),
            hover_color=(60, 130, 70)
        )
        
        # Demolish Button (Red Warning)
        self.demolish_button = Button(
            rect=(self.sidebar_rect.x + 20, 405, self.sidebar_rect.width - 40, 35),
            text="Demolish / Sell",
            font=self.font_normal,
            bg_color=(150, 50, 50),
            hover_color=(180, 70, 70)
        )
        
        self.build_buttons: dict[str, Button] = {}
        self._initialize_build_buttons()

    def _initialize_speed_buttons(self) -> None:
        btn_width, btn_height = 40, 25
        start_x = self.sidebar_rect.x + 20
        y_pos = 110 
        spacing = 5

        self.btn_pause = Button((start_x, y_pos, btn_width, btn_height), "||", self.font_normal)
        self.btn_1x = Button((start_x + (btn_width + spacing) * 1, y_pos, btn_width, btn_height), "1x", self.font_normal)
        self.btn_2x = Button((start_x + (btn_width + spacing) * 2, y_pos, btn_width, btn_height), "2x", self.font_normal)
        self.btn_3x = Button((start_x + (btn_width + spacing) * 3, y_pos, btn_width, btn_height), "3x", self.font_normal)
        
        self.speed_buttons = [self.btn_pause, self.btn_1x, self.btn_2x, self.btn_3x]

    def _initialize_build_buttons(self) -> None:
        start_y_position = 250 
        for index, (building_key, building_class) in enumerate(BUILDING_TYPES.items()):
            button_y = start_y_position + index * 55 
            self.build_buttons[building_key] = Button(
                rect=(self.sidebar_rect.x + 20, button_y, self.sidebar_rect.width - 40, 35),
                text=f"Build {building_class.name}",
                font=self.font_normal
            )

    def _has_enough_resources(self, required_cost: dict[str, int], current_resources: dict[str, int]) -> bool:
        return all(current_resources.get(resource_name, 0) >= required_amount 
                   for resource_name, required_amount in required_cost.items())

    def handle_event(self, event: pygame.event.Event, game_state, audio=None) -> None:
        if self.btn_pause.handle_event(event):
            game_state.is_paused = not game_state.is_paused
        elif self.btn_1x.handle_event(event):
            game_state.is_paused = False
            self.current_speed = 1
            if hasattr(game_state, 'set_speed'): game_state.set_speed(1)
        elif self.btn_2x.handle_event(event):
            game_state.is_paused = False
            self.current_speed = 2
            if hasattr(game_state, 'set_speed'): game_state.set_speed(2)
        elif self.btn_3x.handle_event(event):
            game_state.is_paused = False
            self.current_speed = 3
            if hasattr(game_state, 'set_speed'): game_state.set_speed(3)

        selected_tile = game_state.selected_tile
        if not selected_tile:
            return

        if selected_tile.building:
            if self.upgrade_button.handle_event(event):
                upgraded = game_state.upgrade_building(selected_tile.row, selected_tile.col)
                if upgraded and audio:
                    audio.play_sound("build")
            elif self.demolish_button.handle_event(event):
                if hasattr(game_state, 'remove_building'):
                    game_state.remove_building(selected_tile.row, selected_tile.col)
        elif not selected_tile.is_dark:
            for building_key, button in self.build_buttons.items():
                if button.handle_event(event):
                    built = game_state.add_building(selected_tile.row, selected_tile.col, building_key)
                    if built and audio:
                        audio.play_sound("build")
                    break

    def update(self, game_state) -> None:
        mouse_position = pygame.mouse.get_pos()
        
        ACTIVE_COLOR = (80, 120, 180)  
        PAUSE_COLOR = (180, 60, 60)    
        NORMAL_COLOR = (45, 50, 60)    

        if getattr(game_state, 'is_paused', False):
            self.btn_pause.bg_color = PAUSE_COLOR
        else:
            self.btn_pause.bg_color = NORMAL_COLOR

        is_running = not getattr(game_state, 'is_paused', False)
        self.btn_1x.bg_color = ACTIVE_COLOR if (self.current_speed == 1 and is_running) else NORMAL_COLOR
        self.btn_2x.bg_color = ACTIVE_COLOR if (self.current_speed == 2 and is_running) else NORMAL_COLOR
        self.btn_3x.bg_color = ACTIVE_COLOR if (self.current_speed == 3 and is_running) else NORMAL_COLOR

        for btn in self.speed_buttons:
            btn.is_hovered = btn.rect.collidepoint(mouse_position)
            
        selected_tile = game_state.selected_tile
        
        if selected_tile and selected_tile.building and not selected_tile.is_dark:
            current_building = selected_tile.building
            
            is_max_level = current_building.level >= current_building.max_level
            can_afford_upgrade = self._has_enough_resources(current_building.cost_for_next_level(), game_state.resources)
            self.upgrade_button.is_enabled = (not is_max_level) and can_afford_upgrade
            self.upgrade_button.is_hovered = self.upgrade_button.rect.collidepoint(mouse_position)
            
            self.demolish_button.is_enabled = True
            self.demolish_button.is_hovered = self.demolish_button.rect.collidepoint(mouse_position)
        else:
            self.upgrade_button.is_enabled = False
            self.demolish_button.is_enabled = False

        for building_key, button in self.build_buttons.items():
            button.is_hovered = button.rect.collidepoint(mouse_position)
            if selected_tile and selected_tile.building is None and not selected_tile.is_dark:
                building_class = BUILDING_TYPES[building_key]
                button.is_enabled = self._has_enough_resources(building_class.base_cost, game_state.resources)
            else:
                button.is_enabled = False

    def draw(self, screen: pygame.Surface, game_state) -> None:
        pygame.draw.rect(screen, self.bg_color, self.sidebar_rect)
        pygame.draw.line(screen, (60, 65, 75), (self.sidebar_rect.x, 0), (self.sidebar_rect.x, SCREEN_HEIGHT), 2)

        screen.blit(self.font_title.render("RESOURCES", True, (240, 200, 100)), (self.sidebar_rect.x + 15, 15))
        
        resource_texts = [
            f"🪵 Wood: {game_state.resources.get('wood', 0)}",
            f"🪨 Stone: {game_state.resources.get('stone', 0)}",
            f"💡 Light: {game_state.resources.get('light', 0)}"
        ]
        for index, text in enumerate(resource_texts):
            screen.blit(self.font_normal.render(text, True, self.text_color), (self.sidebar_rect.x + 20, 40 + index * 20))

        for btn in self.speed_buttons:
            btn.draw(screen)

        pygame.draw.line(screen, (40, 45, 55), (self.sidebar_rect.x + 10, 150), (self.sidebar_rect.right - 10, 150))
        selected_tile = game_state.selected_tile
        
        if not selected_tile:
            screen.blit(self.font_normal.render("Select a tile on the map...", True, (120, 120, 120)), (self.sidebar_rect.x + 15, 165))
            return

        terrain_color = (150, 255, 150) if selected_tile.terrain == "grass" else (100, 200, 255)
        terrain_text = f"Tile [{selected_tile.row}, {selected_tile.col}] - {selected_tile.terrain.upper()}"
        screen.blit(self.font_title.render(terrain_text, True, terrain_color), (self.sidebar_rect.x + 15, 165))
        
        status_text = "Consumed!" if selected_tile.is_dark else ("Illuminated" if selected_tile.is_lighted else "In Darkness")
        status_color = (255, 80, 80) if selected_tile.is_dark else ((255, 255, 100) if selected_tile.is_lighted else (150, 150, 150))
        screen.blit(self.font_normal.render(f"Status: {status_text}", True, status_color), (self.sidebar_rect.x + 15, 190))

        if selected_tile.building:
            current_building = selected_tile.building
            building_title = f"{current_building.name} (Lv {current_building.level}/{current_building.max_level})"
            screen.blit(self.font_title.render(building_title, True, (100, 220, 255)), (self.sidebar_rect.x + 15, 225))
            
            if self.upgrade_button.is_hovered and current_building.level < current_building.max_level:
                cost_dict = current_building.cost_for_next_level()
                cost_str = " | ".join([f"{v} {k}" for k, v in cost_dict.items()])
                screen.blit(self.font_small.render(f"Cost: {cost_str}", True, (255, 255, 150)), (self.sidebar_rect.x + 20, 345))

            self.upgrade_button.draw(screen)
            self.demolish_button.draw(screen)

        elif not selected_tile.is_dark:
            screen.blit(self.font_title.render("BUILDINGS", True, (240, 200, 100)), (self.sidebar_rect.x + 15, 225))
            for building_key, button in self.build_buttons.items():
                button.draw(screen)
                
                if button.is_hovered:
                    cost_dict = BUILDING_TYPES[building_key].base_cost
                    cost_str = " | ".join([f"{v} {k}" for k, v in cost_dict.items()])
                    screen.blit(self.font_small.render(f"Cost: {cost_str}", True, (255, 255, 150)), (button.rect.x, button.rect.bottom + 2))