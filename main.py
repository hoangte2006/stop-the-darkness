import sys

import pygame

from core.constants import *
from core.game_state import GameState
from entities.building import TowerOfLight
from services.storage import save_game, load_game
from ui.sidebar import Sidebar


def main():
    pygame.init()  # Khởi tạo Pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stop The Darkness - Python Prototype")
    clock = pygame.time.Clock()

    game = GameState()
    sidebar = Sidebar()

    # Thiết lập Timer: Mỗi 1 giây cộng tài nguyên, mỗi 3 giây bóng tối lan
    RESOURCE_EVENT = pygame.USEREVENT + 1
    DARKNESS_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(RESOURCE_EVENT, 1000)  # 1 giây
    pygame.time.set_timer(DARKNESS_EVENT, 3000)  # 3 giây
    current_speed = 1  # toc do hien tai

    running = True
    while running:
        # --- 1. BẮT SỰ KIỆN CHUỘT VÀ PHÍM ---
        for event in pygame.event.get():
            sidebar.handle_event(event, game)  # nut Pause/1x/2x/3x, Upgrade, Demolish, Build

            if game.speed_multiplier != current_speed:
                current_speed = game.speed_multiplier
                pygame.time.set_timer(RESOURCE_EVENT, int(1000 / current_speed))
                pygame.time.set_timer(DARKNESS_EVENT, int(3000 / current_speed))


            if event.type == pygame.QUIT:
                running = False

            # là sự kiện cộng tài nguyên
            elif event.type == RESOURCE_EVENT:
                game.tick_resources()

            elif event.type == DARKNESS_EVENT:
                game.spread_darkness()
                if game.game_over:
                    game.is_paused = True  # Tạm dừng game khi thua

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

                        # Khôi phục resources
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
                    mx, my = pygame.mouse.get_pos() # Lấy vị trí chuột
                    if mx < SIDEBAR_X:
                        row = my // TILE_SIZE # Tính hàng có nghĩa là chia vị trí y cho kích thước ô , ví dụ 150 // 50 = 3 được hàng thứ 3
                        col = mx // TILE_SIZE
                        game.selected_tile = game.get_tile(row, col)  # Lấy ô đã chọn

                elif event.button == 3:  # Chuột phải: xây Tháp Ánh Sáng thử nghiệm
                    if game.selected_tile:
                        game.add_building(
                            game.selected_tile.row, game.selected_tile.col, TowerOfLight.key
                        )
            # Crtl + S để lưu game, Ctrl + L để load game
            elif event.type == pygame.KEYDOWN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_s:
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
                        print("Hãy nhấn Ctrl + S để lưu game trước.")

                    except Exception as e:
                        print(f"Load game thất bại: {e}")

        # --- 2. VẼ TOÀN BỘ MÀN HÌNH ---
        screen.fill(COLOR_BG)

        # Vẽ bàn cờ GRID_ROWS x GRID_COLS
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                tile = game.grid[r][c]
                rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                # Chọn màu theo địa hình hoặc bóng tối
                if tile.is_dark:
                    color = COLOR_DARKNESS
                elif tile.building is not None:
                    color = COLOR_LIGHT_TOWER
                elif tile.terrain == "forest":
                    color = COLOR_FOREST
                elif tile.terrain == "rock":
                    color = COLOR_ROCK
                elif tile.terrain == "water":
                    color = COLOR_WATER
                else:
                    color = COLOR_GRASS

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 1)  # Viền ô

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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()