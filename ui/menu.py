import pygame
import math
import random


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

        # Start button
        button_width = 260
        button_height = 60

        center_x = self.width // 2

        self.start_button = pygame.Rect(
            center_x - button_width // 2,
            self.height // 2 + 30,
            button_width,
            button_height
        )

        # Quit button
        self.quit_button = pygame.Rect(
            center_x - button_width // 2,
            self.height // 2 + 110,
            button_width,
            button_height
        )

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

    def draw_game_over(self):
        """
        Draw the game over screen.
        """
        self.draw_background()

        # Game over title
        title = self.title_font.render(
            "GAME OVER",
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

        # Game over message
        message = self.subtitle_font.render(
            "The darkness has taken over.",
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


# ---------------------------------------------------------
# Standalone menu test
# Run: python ui/menu.py
# ---------------------------------------------------------

if __name__ == "__main__":

    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption(
        "Stop the Darkness - Menu Test"
    )

    menu = Menu(screen)

    clock = pygame.time.Clock()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        menu.update()
        menu.draw_start_menu()

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()