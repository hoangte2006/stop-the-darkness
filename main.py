import sys
import os
import time 
import pygame

from core.constants import *
from core.game_state import GameState

from services.storage import save_game, load_game, SAVE_FILES
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

    menu = Menu(screen)
    menu.audio = audio                                      # thanh trượt Settings đổi được âm lượng thật
    audio.set_music_volume(menu.settings["music_volume"])   # áp dụng âm lượng đã lưu
    audio.set_sound_volume(menu.settings["sound_volume"])
    audio.play_music("bgm.ogg")                             # phát nhạc SAU khi đã đặt âm lượng


    renderer = TileMapRenderer(TILE_SIZE)
    renderer.load_sprites()


    RESOURCE_EVENT = pygame.USEREVENT + 1
    DARKNESS_EVENT = pygame.USEREVENT + 2

    SAVE_KEYS = {pygame.K_q: 1, pygame.K_w: 2, pygame.K_e: 3}   # Q/W/E luu vao slot 1/2/3
    LOAD_KEYS = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}   # 1/2/3 nap tu slot 1/2/3

    # Trang thai man hinh: "start_menu" | "playing" | "game_over"
    screen_state = "start_menu"
    game = None 
    sidebar = None
    current_speed = 1

    def start_new_game(difficulty="normal"):
        nonlocal game, sidebar, current_speed 
        game = GameState(difficulty=difficulty)
        sidebar = Sidebar()
        current_speed = 1
        pygame.time.set_timer(RESOURCE_EVENT, 1000)
        pygame.time.set_timer(DARKNESS_EVENT, game.darkness_interval_ms)

    def get_slot_infos():
        """Danh sách 3 phần tử: None nếu slot trống, hoặc dict mô tả cho màn Save/Load của TV5."""
        infos = []
        for slot in (1, 2, 3):
            path = SAVE_FILES[slot]
            if os.path.exists(path):
                when = time.strftime("%H:%M %d/%m", time.localtime(os.path.getmtime(path)))
                infos.append({"display_text": f"Saved {when}"})
            else:
                infos.append(None)
        return infos

    def load_slot(slot):
        """Nạp slot vào ván hiện tại. Trả True nếu thành công."""
        data = load_game(slot)
        if not data:
            print(f"Slot {slot} chưa có save.")
            return False
        try:
            game.load_from_dict(data)
            pygame.time.set_timer(DARKNESS_EVENT, int(game.darkness_interval_ms / current_speed)) 

        except Exception as e:
            print(f"Load game thất bại: {e}")
            return False
        print(f"Game loaded! File: {SAVE_FILES[slot]}")
        return True


    running = True
    while running:
        # --- 1. BAT SU KIEN CHUOT VA PHIM ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                continue

            if screen_state == "start_menu": 
                result = menu.handle_event(event)
                if result == "quit":
                    running = False
                elif result in ("easy", "normal", "hard"):
                    audio.play_sound("button")
                    start_new_game(result)
                    screen_state = "playing"
                elif isinstance(result, tuple) and result[0] == "load":
                    start_new_game()                 # tạo ván sạch rồi nạp save lên (save sẽ khôi phục đúng độ khó)
                    if load_slot(result[1]):
                        screen_state = "playing"


            elif screen_state == "playing":
                sidebar.handle_event(event, game, audio)  # nut Pause/1x/2x/3x, Upgrade, Demolish, Build

                if sidebar.open_save_load:                # nut "Menu" tren sidebar: mo man Save/Load
                    sidebar.open_save_load = False
                    screen_state = "save_load"

                if game.speed_multiplier != current_speed:
                    current_speed = game.speed_multiplier
                    pygame.time.set_timer(RESOURCE_EVENT, int(1000 / current_speed))
                    pygame.time.set_timer(DARKNESS_EVENT, int(game.darkness_interval_ms / current_speed))

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

                    elif event.key == pygame.K_ESCAPE:
                        screen_state = "save_load"

                    elif event.key == pygame.K_F1:
                        # DEV: +100 moi tai nguyen de thu thang nhanh. XOA truoc ngay thuyet trinh.
                        for res in game.resources:
                            game.resources[res] += 100

                    elif event.key in SAVE_KEYS:
                        slot = SAVE_KEYS[event.key]
                        if save_game(game.to_dict(), slot):
                            print(f"Game saved! File: saves/save-slot{slot}.json")

                    elif event.key in LOAD_KEYS:
                        slot = LOAD_KEYS[event.key]
                        loaded_data = load_game(slot)
                        if not loaded_data:
                            print(f"Slot {slot} chưa có save. Nhấn Q/W/E để lưu vào slot 1/2/3.")
                        else:
                            try:
                                game.load_from_dict(loaded_data)
                                print(f"Game loaded! File: saves/save-slot{slot}.json")
                            except Exception as e:
                                print(f"Load game thất bại: {e}")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        mx, my = pygame.mouse.get_pos()
                        if mx < SIDEBAR_X:
                            row = my // TILE_SIZE
                            col = mx // TILE_SIZE
                            game.selected_tile = game.get_tile(row, col)


            elif screen_state == "game_over":
                action = menu.handle_game_over_event(event)
                if action == "restart":
                    audio.play_sound("button")
                    start_new_game(game.difficulty)
                    screen_state = "playing"
                    
            elif screen_state == "save_load":
                action = menu.handle_save_load_event(event)
                if action == "back":
                    screen_state = "playing"
                elif isinstance(action, tuple):
                    kind, slot = action
                    if kind == "save":
                        if save_game(game.to_dict(), slot):
                            print(f"Game saved! File: {SAVE_FILES[slot]}")
                    elif kind == "load":
                        if load_slot(slot):
                            screen_state = "playing"


        # --- 2. VE TOAN BO MAN HINH ---
        if screen_state == "start_menu":
            menu.update()
            menu.draw(get_slot_infos())

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

        elif screen_state == "save_load":
            menu.update()
            menu.draw_save_load_menu(get_slot_infos(), can_save=True)



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
