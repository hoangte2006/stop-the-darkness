"""Right-side game control panel."""
"""
UI Package - File: sidebar.py
Quản lý thanh điều khiển bên phải màn hình.
Hiển thị kho tài nguyên, thông tin ô đất được chọn và xử lý logic các nút bấm xây dựng/nâng cấp.
"""

import pygame
from core.constants import SIDEBAR_X, SIDEBAR_WIDTH, SCREEN_HEIGHT
from entities.building import BUILDING_TYPES
from ui.button import Button

class Sidebar:
    """
    Lớp Sidebar chứa các thành phần giao diện hiển thị thông tin trò chơi.
    Liên kết dữ liệu tĩnh từ GameState và thao tác người dùng xuống hệ thống.
    """

    def __init__(self):
        """
        Khởi tạo thanh Sidebar, thiết lập font chữ, màu sắc và tạo danh sách các nút bấm.
        Tham số nhận vào: Không có.
        Trả về: Không có (None).
        """
        self.sidebar_rect = pygame.Rect(SIDEBAR_X, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        
        self.font_title = pygame.font.SysFont("Verdana", 16, bold=True)
        self.font_normal = pygame.font.SysFont("Verdana", 12)
        self.font_small = pygame.font.SysFont("Verdana", 10)
        
        self.bg_color = (15, 18, 22)
        self.text_color = (200, 200, 205)
        
        # Khởi tạo nút nâng cấp mặc định
        self.upgrade_button = Button(
            rect=(self.sidebar_rect.x + 20, 400, self.sidebar_rect.width - 40, 35),
            text="Nâng cấp công trình",
            font=self.font_normal
        )
        
        self.build_buttons: dict[str, Button] = {}
        self._initialize_build_buttons()

    def _initialize_build_buttons(self) -> None:
        """
        Hàm nội bộ: Khởi tạo linh động danh sách nút xây dựng dựa trên BUILDING_TYPES.
        Tham số nhận vào: Không có.
        Trả về: Không có (None).
        """
        start_y_position = 220
        # Duyệt qua danh sách công trình từ entity để tạo nút tự động
        for index, (building_key, building_class) in enumerate(BUILDING_TYPES.items()):
            button_y = start_y_position + index * 45
            self.build_buttons[building_key] = Button(
                rect=(self.sidebar_rect.x + 20, button_y, self.sidebar_rect.width - 40, 35),
                text=f"Xây {building_class.name}",
                font=self.font_normal
            )

    def _has_enough_resources(self, required_cost: dict[str, int], current_resources: dict[str, int]) -> bool:
        """
        Hàm nội bộ: So sánh tài nguyên hiện có với chi phí yêu cầu.
        Tham số nhận vào: required_cost (giá tiền), current_resources (tài nguyên đang có).
        Trả về: True nếu người chơi đủ mọi loại tài nguyên yêu cầu, ngược lại False.
        """
        # Kiểm tra mọi loại tài nguyên yêu cầu đều phải nhỏ hơn hoặc bằng tài nguyên đang có
        return all(current_resources.get(resource_name, 0) >= required_amount 
                   for resource_name, required_amount in required_cost.items())

    def handle_event(self, event: pygame.event.Event, game_state) -> None:
        """
        Bắt sự kiện click chuột trên giao diện thanh bên và gửi lệnh thực thi xuống GameState.
        Tham số nhận vào: event (sự kiện của pygame), game_state (đối tượng quản lý trạng thái).
        Trả về: Không có (None).
        """
        selected_tile = game_state.selected_tile
        if not selected_tile:
            return

        # Nhánh 1: Nếu ô đã có công trình, chỉ kiểm tra nút nâng cấp
        if selected_tile.building:
            if self.upgrade_button.handle_event(event):
                game_state.upgrade_building(selected_tile.row, selected_tile.col)
                
        # Nhánh 2: Nếu ô trống và chưa bị bóng tối chiếm, kiểm tra các nút xây dựng
        elif not selected_tile.is_dark:
            for building_key, button in self.build_buttons.items():
                if button.handle_event(event):
                    game_state.add_building(selected_tile.row, selected_tile.col, building_key)
                    break

    def update(self, game_state) -> None:
        """
        Cập nhật trạng thái bật/tắt (is_enabled) của các nút dựa trên lượng tài nguyên mỗi frame.
        Tham số nhận vào: game_state (để đọc lượng tài nguyên hiện tại).
        Trả về: Không có (None).
        """
        mouse_position = pygame.mouse.get_pos()
        selected_tile = game_state.selected_tile
        
        # Cập nhật logic hiển thị cho nút nâng cấp
        if selected_tile and selected_tile.building and not selected_tile.is_dark:
            current_building = selected_tile.building
            is_max_level = current_building.level >= current_building.max_level
            can_afford_upgrade = self._has_enough_resources(current_building.cost_for_next_level(), game_state.resources)
            
            self.upgrade_button.is_enabled = (not is_max_level) and can_afford_upgrade
            self.upgrade_button.is_hovered = self.upgrade_button.rect.collidepoint(mouse_position)
        else:
            self.upgrade_button.is_enabled = False

        # Cập nhật logic hiển thị cho danh sách nút xây dựng
        for building_key, button in self.build_buttons.items():
            button.is_hovered = button.rect.collidepoint(mouse_position)
            
            if selected_tile and selected_tile.building is None and not selected_tile.is_dark:
                building_class = BUILDING_TYPES[building_key]
                button.is_enabled = self._has_enough_resources(building_class.base_cost, game_state.resources)
            else:
                button.is_enabled = False

    def draw(self, screen: pygame.Surface, game_state) -> None:
        """
        Vẽ toàn bộ khung Sidebar bao gồm chỉ số tài nguyên, thông tin ô và các nút bấm.
        Tham số nhận vào: screen (bề mặt để vẽ), game_state (dữ liệu trò chơi).
        Trả về: Không có (None).
        """
        # 1. Vẽ nền và đường viền phân cách
        pygame.draw.rect(screen, self.bg_color, self.sidebar_rect)
        pygame.draw.line(screen, (60, 65, 75), (self.sidebar_rect.x, 0), (self.sidebar_rect.x, SCREEN_HEIGHT), 2)

        # 2. Render Khu vực Kho Tài Nguyên
        title_surface = self.font_title.render("KHO TÀI NGUYÊN", True, (240, 200, 100))
        screen.blit(title_surface, (self.sidebar_rect.x + 15, 15))
        
        resource_texts = [
            f"🪵 Gỗ: {game_state.resources.get('wood', 0)}",
            f"🪨 Đá: {game_state.resources.get('stone', 0)}",
            f"💡 Sáng: {game_state.resources.get('light', 0)}"
        ]
        for index, text in enumerate(resource_texts):
            text_surface = self.font_normal.render(text, True, self.text_color)
            screen.blit(text_surface, (self.sidebar_rect.x + 20, 45 + index * 22))

        # 3. Render Thông tin chi tiết của Ô đất (Tile)
        pygame.draw.line(screen, (40, 45, 55), (self.sidebar_rect.x + 10, 120), (self.sidebar_rect.right - 10, 120))
        selected_tile = game_state.selected_tile
        
        if not selected_tile:
            empty_surface = self.font_normal.render("Chọn 1 ô trên bản đồ...", True, (120, 120, 120))
            screen.blit(empty_surface, (self.sidebar_rect.x + 15, 135))
            return

        # Tô màu tên địa hình cho dễ nhìn
        terrain_color = (150, 255, 150) if selected_tile.terrain == "grass" else (100, 200, 255)
        terrain_text = f"Ô [{selected_tile.row}, {selected_tile.col}] - {selected_tile.terrain.upper()}"
        screen.blit(self.font_title.render(terrain_text, True, terrain_color), (self.sidebar_rect.x + 15, 135))
        
        # Đánh giá trạng thái ô đất
        status_text = "Bị Nuốt Chửng!" if selected_tile.is_dark else ("Được Chiếu Sáng" if selected_tile.is_lighted else "Trong Bóng Tối")
        status_color = (255, 80, 80) if selected_tile.is_dark else ((255, 255, 100) if selected_tile.is_lighted else (150, 150, 150))
        screen.blit(self.font_normal.render(f"Trạng thái: {status_text}", True, status_color), (self.sidebar_rect.x + 15, 160))

        # 4. Render Menu Xây dựng hoặc Menu Nâng cấp
        if selected_tile.building:
            current_building = selected_tile.building
            building_title = f"{current_building.name} (Lv {current_building.level}/{current_building.max_level})"
            screen.blit(self.font_title.render(building_title, True, (100, 220, 255)), (self.sidebar_rect.x + 15, 200))
            
            self.upgrade_button.draw(screen)
        elif not selected_tile.is_dark:
            screen.blit(self.font_title.render("CÔNG TRÌNH", True, (240, 200, 100)), (self.sidebar_rect.x + 15, 195))
            for building_key, button in self.build_buttons.items():
                button.draw(screen)