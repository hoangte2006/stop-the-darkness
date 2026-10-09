import pygame
import math
import random
import json
from pathlib import Path

SETTINGS_FILE = Path("settings.json")
DEFAULT_SETTINGS = {
    "music_volume": 0.3,
    "sound_volume": 0.8
}

def load_settings():
    """Load settings from JSON file or return defaults if file doesn't exist."""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    """Save current settings dictionary to JSON file."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"[Settings] Error saving settings: {e}")


class Menu:
    def __init__(self, screen):
        self.screen = screen

        self.width = screen.get_width()
        self.height = screen.get_height()

        # Fonts
        self.title_font = pygame.font.Font(None, 82)
        self.subtitle_font = pygame.font.Font(None, 30)
        self.button_font = pygame.font.Font(None, 38)
        self.small_font = pygame.font.Font(None, 26)

        # Load settings and bind audio
        self.settings = load_settings()
        self.audio = None

        # Start menu buttons (5 buttons: Start, Load, Tutorial, Settings, Quit)
        button_width = 260
        button_height = 42
        center_x = self.width // 2
        start_y = int(self.height * 0.38)
        gap = 50                          

        self.start_button = pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height)
        self.load_button = pygame.Rect(center_x - button_width // 2, start_y + gap, button_width, button_height)
        self.tutorial_button = pygame.Rect(center_x - button_width // 2, start_y + gap * 2, button_width, button_height)
        self.settings_button = pygame.Rect(center_x - button_width // 2, start_y + gap * 3, button_width, button_height)
        self.quit_button = pygame.Rect(center_x - button_width // 2, start_y + gap * 4, button_width, button_height)
        
        # Settings slider rects
        self.slider_width = 300
        self.slider_height = 14
        slider_x = center_x - self.slider_width // 2

        self.music_slider_rect = pygame.Rect(slider_x, int(self.height * 0.40), self.slider_width, self.slider_height)
        self.sound_slider_rect = pygame.Rect(slider_x, int(self.height * 0.55), self.slider_width, self.slider_height)

        # Dragging state trackers
        self.dragging_music = False
        self.dragging_sound = False

        # Difficulty Menu buttons
        diff_w = 260
        diff_h = 50
        diff_start_y = self.height // 2 - 60
        diff_gap = 60

        self.diff_easy_btn = pygame.Rect(center_x - diff_w // 2, diff_start_y, diff_w, diff_h)
        self.diff_normal_btn = pygame.Rect(center_x - diff_w // 2, diff_start_y + diff_gap, diff_w, diff_h)
        self.diff_hard_btn = pygame.Rect(center_x - diff_w // 2, diff_start_y + diff_gap * 2, diff_w, diff_h)
        self.diff_back_btn = pygame.Rect(center_x - diff_w // 2, diff_start_y + diff_gap * 3, diff_w, diff_h)

        # Common Back button and slot tracking
        self.common_back_btn = pygame.Rect(center_x - 100, self.height - 80, 200, 48)
        self.save_load_rects = []
        
        # Current screen state: "main" | "difficulty" | "load" | "tutorial"
        self.state = "main"

        # Animation timer
        self.time = 0

        # Light particles
        self.particles = []

        for _ in range(35):
            self.particles.append({
                "x": random.randint(0, self.width),
                "y": random.randint(0, self.height),
                "speed": random.uniform(0.2, 0.8),
                "size": random.randint(1, 3),
                "phase": random.uniform(0, math.pi * 2)
            })

    def update(self):
        """
        Update menu animations.
        """
        self.time += 0.02

        for particle in self.particles:
            particle["y"] -= particle["speed"]

            if particle["y"] < 0:
                particle["y"] = self.height
                particle["x"] = random.randint(0, self.width)

    def draw_background(self):
        """
        Draw the dark background and central light.
        """
        self.screen.fill((8, 8, 15))

        center_x = self.width // 2
        center_y = self.height // 2

        # Pulsing central light
        pulse = (math.sin(self.time * 2) + 1) * 0.5

        for radius in range(180, 20, -20):
            strength = int(8 + pulse * 8)

            pygame.draw.circle(
                self.screen,
                (strength, strength, strength + 5),
                (center_x, center_y),
                radius
            )

        # Draw light particles
        for particle in self.particles:
            brightness = int(
                100 + 80 * math.sin(
                    self.time * 2 + particle["phase"]
                )
            )

            brightness = max(40, min(220, brightness))

            pygame.draw.circle(
                self.screen,
                (brightness, brightness, brightness),
                (
                    int(particle["x"]),
                    int(particle["y"])
                ),
                particle["size"]
            )

    def draw_button(self, rect, text):
        """
        Draw a button with hover effect.
        """
        mouse_pos = pygame.mouse.get_pos()
        hovered = rect.collidepoint(mouse_pos)

        if hovered:
            background = (75, 75, 95)
            border = (220, 220, 230)
        else:
            background = (35, 35, 50)
            border = (100, 100, 120)

        # Button background
        pygame.draw.rect(
            self.screen,
            background,
            rect,
            border_radius=10
        )

        # Button border
        pygame.draw.rect(
            self.screen,
            border,
            rect,
            width=2,
            border_radius=10
        )

        # Button text
        text_surface = self.button_font.render(
            text,
            True,
            (245, 245, 245)
        )

        text_rect = text_surface.get_rect(
            center=rect.center
        )

        self.screen.blit(text_surface, text_rect)

    def draw_start_menu(self):
        """
        Draw the main start menu.
        """
        self.draw_background()

        # Title
        title = self.title_font.render(
            "STOP THE DARKNESS",
            True,
            (240, 240, 245)
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                self.height // 4
            )
        )

        self.screen.blit(title, title_rect)


        # Start button
        self.draw_button(
            self.start_button,
            "START GAME"
        )
        
        # Load button
        self.draw_button(
            self.load_button,
            "LOAD GAME"
        )

        # Tutorial button
        self.draw_button(
            self.tutorial_button,
            "HOW TO PLAY"
        )
        
        # Settings button
        self.draw_button(
            self.settings_button, 
            "SETTINGS"
        )

        # Quit button
        self.draw_button(
            self.quit_button,
            "QUIT"
        )

        # Bottom message
        info = self.small_font.render(
            "The darkness is coming...",
            True,
            (110, 110, 125)
        )

        info_rect = info.get_rect(
            center=(
                self.width // 2,
                self.height - 35
            )
        )

        self.screen.blit(info, info_rect)

    def draw_game_over(self, won=False):
        """
        Draw the game over screen / victory screen.
        """
        self.draw_background()

        # Game title
        title_text = "YOU WIN!" if won else "GAME OVER"
        title = self.title_font.render(
            title_text,
            True,
            (235, 235, 240)
        )

        title_rect = title.get_rect(
            center=(
                self.width // 2,
                self.height // 3
            )
        )

        self.screen.blit(title, title_rect)

        # Game message
        message_text = (
            "The light has survived."
            if won
            else "The darkness has taken over."
        )
        message = self.subtitle_font.render(
            message_text,
            True,
            (170, 170, 185)
        )

        message_rect = message.get_rect(
            center=(
                self.width // 2,
                self.height // 3 + 65
            )
        )

        self.screen.blit(message, message_rect)

        # Restart button
        restart_button = pygame.Rect(
            self.width // 2 - 130,
            self.height // 2 + 30,
            260,
            60
        )

        self.draw_button(
            restart_button,
            "RESTART"
        )

        # Hint
        hint = self.small_font.render(
            "Press R to restart",
            True,
            (120, 120, 135)
        )

        hint_rect = hint.get_rect(
            center=(
                self.width // 2,
                self.height - 45
            )
        )

        self.screen.blit(hint, hint_rect)

    def handle_start_menu_event(self, event):
        """
        Handle events from the start menu.

        Returns:
            "start" when Start Game is clicked.
            "quit" when Quit is clicked.
            None otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:

            if self.start_button.collidepoint(event.pos):
                return "start"
            
            if self.load_button.collidepoint(event.pos):
                return "load"

            if self.tutorial_button.collidepoint(event.pos):
                return "tutorial"
            
            if self.settings_button.collidepoint(event.pos):
                return "settings"

            if self.quit_button.collidepoint(event.pos):
                return "quit"

        return None

    def handle_game_over_event(self, event):
        """
        Handle events from the game over screen.

        Returns:
            "restart" when restart is clicked.
            None otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:

            restart_button = pygame.Rect(
                self.width // 2 - 130,
                self.height // 2 + 30,
                260,
                60
            )

            if restart_button.collidepoint(event.pos):
                return "restart"

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                return "restart"

        return None
    
    # DIFFICULTY MENU
    def draw_difficulty_menu(self):
        """
        Draw difficulty selection screen.
        """
        self.draw_background()

        title = self.title_font.render("SELECT DIFFICULTY", True, (240, 240, 245))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 5))
        self.screen.blit(title, title_rect)

        self.draw_button(self.diff_easy_btn, "EASY")
        self.draw_button(self.diff_normal_btn, "NORMAL")
        self.draw_button(self.diff_hard_btn, "HARD")
        self.draw_button(self.diff_back_btn, "BACK")

    def handle_difficulty_event(self, event):
        """
        Handle events for difficulty menu.
        Returns: "easy" | "normal" | "hard" | "back" | None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.diff_easy_btn.collidepoint(event.pos):
                return "easy"
            if self.diff_normal_btn.collidepoint(event.pos):
                return "normal"
            if self.diff_hard_btn.collidepoint(event.pos):
                return "hard"
            if self.diff_back_btn.collidepoint(event.pos):
                return "back"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"

        return None

    # SAVE / LOAD MENU
    def draw_save_load_menu(self, slot_infos, can_save=False):
        """
        Draw save/load menu with 3 slots.
        :param slot_infos: list of 3 slot data items
        :param can_save: False if opened from start menu (load-only), True in-game
        """
        self.draw_background()

        title_text = "SAVE & LOAD" if can_save else "LOAD GAME"
        title = self.title_font.render(title_text, True, (240, 240, 245))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 6))
        self.screen.blit(title, title_rect)

        self.save_load_rects = []
        card_w = min(680, self.width - 60)
        card_h = 75
        card_start_y = self.height // 6 + 60
        card_gap = 88
        center_x = self.width // 2

        for i in range(3):
            card_rect = pygame.Rect(
                center_x - card_w // 2,
                card_start_y + i * card_gap,
                card_w,
                card_h
            )
            pygame.draw.rect(self.screen, (25, 25, 38), card_rect, border_radius=10)
            pygame.draw.rect(self.screen, (70, 70, 90), card_rect, width=2, border_radius=10)

            slot_data = slot_infos[i] if i < len(slot_infos) else None
            is_empty = (
                slot_data is None 
                or slot_data == "" 
                or (isinstance(slot_data, dict) and not slot_data.get("valid", True))
            )
            
            if is_empty:
                desc_str = "Empty Slot"
            elif isinstance(slot_data, dict):
                desc_str = slot_data.get("display_text", f"Level {slot_data.get('level', 1)} - {slot_data.get('date', '')}")
            else:
                desc_str = str(slot_data)

            slot_label = self.button_font.render(f"Slot {i + 1}", True, (230, 230, 240))
            self.screen.blit(slot_label, (card_rect.x + 20, card_rect.y + 12))

            detail_label = self.small_font.render(desc_str, True, (140, 140, 160))
            self.screen.blit(detail_label, (card_rect.x + 20, card_rect.y + 44))

            btn_w = 95
            btn_h = 42
            btn_y = card_rect.centery - btn_h // 2

            if can_save:
                save_btn_rect = pygame.Rect(card_rect.right - 215, btn_y, btn_w, btn_h)
                self.draw_button(save_btn_rect, "Save")
                self.save_load_rects.append(("save", i + 1, save_btn_rect, True))

                load_btn_rect = pygame.Rect(card_rect.right - 105, btn_y, btn_w, btn_h)
                self.draw_button(load_btn_rect, "Load")
                self.save_load_rects.append(("load", i + 1, load_btn_rect, not is_empty))
            else:
                load_btn_rect = pygame.Rect(card_rect.right - 120, btn_y, 100, btn_h)
                self.draw_button(load_btn_rect, "Load")
                self.save_load_rects.append(("load", i + 1, load_btn_rect, not is_empty))

        self.draw_button(self.common_back_btn, "BACK")

    def handle_save_load_event(self, event):
        """
        Handle events in save/load menu.
        Returns: ("save", n) | ("load", n) | "back" | None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for action, slot_idx, rect, enabled in self.save_load_rects:
                if enabled and rect.collidepoint(event.pos):
                    return (action, slot_idx)

            if self.common_back_btn.collidepoint(event.pos):
                return "back"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"

        return None

    # TUTORIAL / HOW TO PLAY
    def draw_tutorial(self):
        """
        Draw tutorial and control bindings screen.
        """
        self.draw_background()

        title = self.title_font.render("HOW TO PLAY", True, (240, 240, 245))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 6))
        self.screen.blit(title, title_rect)

        panel_w = min(700, self.width - 60)
        panel_h = 320
        panel_rect = pygame.Rect(
            self.width // 2 - panel_w // 2,
            self.height // 6 + 55,
            panel_w,
            panel_h
        )
        pygame.draw.rect(self.screen, (20, 20, 30), panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (60, 60, 80), panel_rect, width=2, border_radius=12)

        guide_lines = [
            ("WASD / ARROW KEYS", "Move your character around the map"),
            ("MOUSE CURSOR", "Aim flashlight / Direction of light"),
            ("SPACEBAR", "Place torch / Activate light ability"),
            ("SURVIVAL GOAL", "Keep light alive & protect the core"),
            ("AVOID DARKNESS", "Monsters move faster in shadows!")
        ]

        start_y = panel_rect.y + 30
        for i, (action, desc) in enumerate(guide_lines):
            act_text = self.subtitle_font.render(action, True, (240, 200, 100))
            desc_text = self.subtitle_font.render(f"-  {desc}", True, (200, 200, 215))

            self.screen.blit(act_text, (panel_rect.x + 35, start_y + i * 55))
            self.screen.blit(desc_text, (panel_rect.x + 270, start_y + i * 55))

        self.draw_button(self.common_back_btn, "BACK")

    def handle_tutorial_event(self, event):
        """
        Handle events in tutorial screen.
        Returns: "back" | None
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.common_back_btn.collidepoint(event.pos):
                return "back"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"

        return None
    
    def draw(self, slot_infos=None, can_save=False):
        """
        Draw the current active menu screen based on self.state.
        """
        if self.state == "main":
            self.draw_start_menu()
        elif self.state == "difficulty":
            self.draw_difficulty_menu()
        elif self.state == "load":
            self.draw_save_load_menu(slot_infos or [None, None, None], can_save=can_save)
        elif self.state == "tutorial":
            self.draw_tutorial()
        elif self.state == "settings":
            self.draw_settings_menu()

    def handle_event(self, event):
        """
        Handle events across all menu sub-screens.
        Returns: 
            - "easy" | "normal" | "hard" (difficulty selected to start game)
            - ("load", n) | ("save", n) (slot action confirmed)
            - "quit" (exit game)
            - None (navigating sub-screens)
        """
        if self.state == "main":
            action = self.handle_start_menu_event(event)
            if action == "start":
                self.state = "difficulty"
            elif action == "load":
                self.state = "load"
            elif action == "tutorial":
                self.state = "tutorial"
            elif action == "settings":
                self.state = "settings"
            elif action == "quit":
                return "quit"

        elif self.state == "difficulty":
            diff = self.handle_difficulty_event(event)
            if diff == "back":
                self.state = "main"
            elif diff in ("easy", "normal", "hard"):
                self.state = "main"
                return diff

        elif self.state == "load":
            res = self.handle_save_load_event(event)
            if res == "back":
                self.state = "main"
            elif res is not None:
                return res

        elif self.state == "tutorial":
            res = self.handle_tutorial_event(event)
            if res == "back":
                self.state = "main"
                
        elif self.state == "settings":
            res = self.handle_settings_event(event)
            if res == "back":
                self.state = "main"

        return None
    
    # SETTINGS MENU
    def draw_slider(self, rect, value, label):
        """Draw volume slider bar with interactive handle."""
        label_surf = self.subtitle_font.render(label, True, (220, 220, 230))
        self.screen.blit(label_surf, (rect.x, rect.y - 28))

        pct_surf = self.small_font.render(f"{int(value * 100)}%", True, (240, 200, 100))
        self.screen.blit(pct_surf, (rect.right - 45, rect.y - 26))

        pygame.draw.rect(self.screen, (40, 40, 55), rect, border_radius=7)
        pygame.draw.rect(self.screen, (90, 90, 110), rect, width=2, border_radius=7)

        fill_width = int(rect.width * value)
        if fill_width > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_width, rect.height)
            pygame.draw.rect(self.screen, (100, 140, 230), fill_rect, border_radius=7)

        handle_x = rect.x + fill_width
        pygame.draw.circle(self.screen, (240, 240, 250), (handle_x, rect.centery), 10)
        pygame.draw.circle(self.screen, (50, 50, 70), (handle_x, rect.centery), 10, width=2)

    def draw_settings_menu(self):
        """Draw settings menu screen."""
        self.draw_background()

        title = self.title_font.render("SETTINGS", True, (240, 240, 245))
        title_rect = title.get_rect(center=(self.width // 2, self.height // 6))
        self.screen.blit(title, title_rect)

        self.draw_slider(self.music_slider_rect, self.settings["music_volume"], "Music Volume")
        self.draw_slider(self.sound_slider_rect, self.settings["sound_volume"], "Sound FX Volume")

        self.draw_button(self.common_back_btn, "BACK")

    def handle_settings_event(self, event, audio_manager=None):
        """Handle dragging slider bars and saving settings to JSON."""
        audio = audio_manager or self.audio

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.music_slider_rect.inflate(16, 16).collidepoint(event.pos):
                self.dragging_music = True
            elif self.sound_slider_rect.inflate(16, 16).collidepoint(event.pos):
                self.dragging_sound = True
            elif self.common_back_btn.collidepoint(event.pos):
                save_settings(self.settings)
                return "back"

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_music or self.dragging_sound:
                save_settings(self.settings)
            self.dragging_music = False
            self.dragging_sound = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging_music:
                rel_x = max(0, min(self.slider_width, event.pos[0] - self.music_slider_rect.x))
                new_vol = round(rel_x / self.slider_width, 2)
                self.settings["music_volume"] = new_vol
                if audio:
                    audio.set_music_volume(new_vol)

            elif self.dragging_sound:
                rel_x = max(0, min(self.slider_width, event.pos[0] - self.sound_slider_rect.x))
                new_vol = round(rel_x / self.slider_width, 2)
                self.settings["sound_volume"] = new_vol
                if audio:
                    audio.set_sound_volume(new_vol)

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            save_settings(self.settings)
            return "back"

        return None
    