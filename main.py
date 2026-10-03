import sys

import pygame

from core.constants import *
from core.game_state import GameState
from entities.building import TowerOfLight
from services.storage import save_game, load_game
from services.audio import AudioManager
from ui import renderer
from ui.sidebar import Sidebar
from ui.menu import Menu
from ui.renderer import TileMapRenderer


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stop The Darkness - Python Prototype")
    clock = pygame.time.Clock()

    audio = AudioManager()
    audio.load_default_sounds()
    audio.play_music("bgm.ogg")

    menu = Menu(screen)

    renderer = TileMapRenderer(TILE_SIZE)
    renderer.load_sprites()


    RESOURCE_EVENT = pygame.USEREVENT + 1
    DARKNESS_EVENT = pygame.USEREVENT + 2

    # Trang thai man hinh: "start_menu" | "playing" | "game_over"
    screen_state = "start_menu"
    game = None
    sidebar = None
    current_speed = 1

    def start_new_game():
        nonlocal game, sidebar, current_speed
        game = GameState()
        sidebar = Sidebar()
        current_speed = 1
        pygame.time.set_timer(RESOURCE_EVENT, 1000)
        pygame.time.set_timer(DARKNESS_EVENT, 3000)

    running = True
    while running:
        # --- 1. BAT SU KIEN CHUOT VA PHIM ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if screen_state == "start_menu":
                action = menu.handle_start_menu_event(event)
                if action == "start":
                    audio.play_sound("button")
                    start_new_game()
                    screen_state = "playing"
                elif action == "quit":
                    running = False

            elif screen_state == "playing":
                sidebar.handle_event(event, game, audio)  # nut Pause/1x/2x/3x, Upgrade, Demolish, Build

                if game.speed_multiplier != current_speed:
                    current_speed = game.speed_multiplier
                    pygame.time.set_timer(RESOURCE_EVENT, int(1000 / current_speed))
                    pygame.time.set_timer(DARKNESS_EVENT, int(3000 / current_speed))

                # là sự kiện cộng tài nguyên
                if event.type == RESOURCE_EVENT:
                    game.tick_resources()
                    if game.game_won:
                        game.is_paused = True
                        audio.play_sound("bell")
                        screen_state = "game_over"


                elif event.type == DARKNESS_EVENT:
                    game.spread_darkness()
                    if game.game_over:
                        game.is_paused = True  # Tạm dừng game khi thua
                        audio.play_sound("bell")
                        screen_state = "game_over"

                # Là sự kiện nhấn phím Space để tạm dừng / tiếp tục game
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.is_paused = not game.is_paused

                    elif event.key == pygame.K_s:
                        save_game(game.to_dict())
                        print("Game saved!")
                        print("File: saves/save.json")

                    elif event.key == pygame.K_l:
                        try:
                            loaded_data = load_game("saves/save.json")
                            game.load_from_dict(loaded_data)
                            print("Game loaded!")
                            print("File: saves/save.json")

                        except FileNotFoundError:
                            print("Không tìm thấy save game!")
                            print("Hãy nhấn S để lưu game trước.")

                        except Exception as e:
                            print(f"Load game thất bại: {e}")

                # là sự kiện nhấn chuột trái / phải để chọn ô hoặc xây Tháp Ánh Sáng
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Chuột trái: chọn ô (chỉ tính click trong vùng bàn cờ)
                        mx, my = pygame.mouse.get_pos()
                        if mx < SIDEBAR_X:
                            row = my // TILE_SIZE
                            col = mx // TILE_SIZE
                            game.selected_tile = game.get_tile(row, col)

                    elif event.button == 3:  # Chuột phải: xây Tháp Ánh Sáng thử nghiệm
                        if game.selected_tile:
                            built = game.add_building(
                                game.selected_tile.row, game.selected_tile.col, TowerOfLight.key
                            )
                            if built:
                                audio.play_sound("build")

            elif screen_state == "game_over":
                action = menu.handle_game_over_event(event)
                if action == "restart":
                    audio.play_sound("button")
                    start_new_game()
                    screen_state = "playing"

        # --- 2. VE TOAN BO MAN HINH ---
        if screen_state == "start_menu":
            menu.update()
            menu.draw_start_menu()

        elif screen_state == "playing":
            screen.fill(COLOR_BG)

            game.update_light()

            # Vẽ bàn cờ GRID_ROWS x GRID_COLS
            renderer.draw(screen, game)


            # Vẽ viền vàng cho ô đang được chọn
            if game.selected_tile:
                sel_rect = pygame.Rect(
                    game.selected_tile.col * TILE_SIZE,
                    game.selected_tile.row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                pygame.draw.rect(screen, (255, 255, 0), sel_rect, 3)

            # --- 3. VẼ BẢNG THÔNG TIN BÊN PHẢI (SIDEBAR) ---
            sidebar.update(game)
            sidebar.draw(screen, game)

        elif screen_state == "game_over":
            menu.update()
            menu.draw_game_over(won=game.game_won)


        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
