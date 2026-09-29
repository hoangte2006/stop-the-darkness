import sys

import pygame

from core.constants import *
from core.game_state import GameState
from entities.building import TowerOfLight
from services.storage import save_game, load_game


def main():
    pygame.init()  # Khởi tạo Pygame
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Stop The Darkness - Python Prototype")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    title_font = pygame.font.SysFont("Arial", 20, bold=True)

    game = GameState()

    # Thiết lập Timer: Mỗi 1 giây cộng tài nguyên, mỗi 3 giây bóng tối lan
    RESOURCE_EVENT = pygame.USEREVENT + 1
    DARKNESS_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(RESOURCE_EVENT, 1000)  # 1 giây
    pygame.time.set_timer(DARKNESS_EVENT, 3000)  # 3 giây

    running = True
    while running:
        # --- 1. BẮT SỰ KIỆN CHUỘT VÀ PHÍM ---
        for event in pygame.event.get():
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
                if event.button == 1:  # Chuột trái: chọn ô
                    mx, my = pygame.mouse.get_pos() # Lấy vị trí chuột
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
        sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(screen, COLOR_SIDEBAR, sidebar_rect)

        # Hiển thị tài nguyên
        res_text = (
            f"Wood: {game.resources['wood']} | Stone: {game.resources['stone']} | "
            f"Light: {game.resources['light']}"
        )
        screen.blit(title_font.render("RESOURCES", True, (255, 255, 255)), (SIDEBAR_X + 20, 20))
        screen.blit(font.render(res_text, True, (200, 220, 200)), (SIDEBAR_X + 20, 50))

        # Trạng thái Pause
        pause_status = "PAUSED (Space to resume)" if game.is_paused else "RUNNING (Space to pause)"
        screen.blit(font.render(pause_status, True, (255, 200, 100)), (SIDEBAR_X + 20, 80))

        # Thông tin ô đang chọn
        screen.blit(title_font.render("SELECTED TILE", True, (255, 255, 255)), (SIDEBAR_X + 20, 130))
        if game.selected_tile:
            st = game.selected_tile
            building_name = st.building.name if st.building else "None"
            screen.blit(font.render(f"Coordinates: ({st.row}, {st.col})", True, (220, 220, 220)), (SIDEBAR_X + 20, 160))
            screen.blit(font.render(f"Terrain: {st.terrain.capitalize()}", True, (220, 220, 220)), (SIDEBAR_X + 20, 185))
            screen.blit(font.render(f"Building: {building_name}", True, (220, 220, 220)), (SIDEBAR_X + 20, 210))
            screen.blit(
                font.render(
                    f"Status: {'DARKNESS' if st.is_dark else 'Safe'}",
                    True,
                    (255, 100, 100) if st.is_dark else (100, 255, 100),
                ),
                (SIDEBAR_X + 20, 235),
            )

            cost_text = ", ".join(f"{amt} {res}" for res, amt in TowerOfLight.base_cost.items())
            screen.blit(
                font.render(f"[Right Click] to build Tower (Cost: {cost_text})", True, (240, 240, 150)),
                (SIDEBAR_X + 20, 280),
            )
        else:
            screen.blit(font.render("Click any tile on the board...", True, (150, 150, 150)), (SIDEBAR_X + 20, 160))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()