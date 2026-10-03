"""User interface button components."""
"""
UI Package - File: button.py
Đảm nhận việc tạo và quản lý tương tác của các nút bấm trên giao diện.
Tuân thủ chuẩn interface: handle_event(event) -> bool và is_clicked(mouse_pos) -> bool.
"""

import pygame

class Button:
    """
    Lớp Button đại diện cho một nút bấm tĩnh trên màn hình.
    Xử lý các trạng thái bình thường, di chuột (hover) và vô hiệu hóa (disabled).
    """

    def __init__(
        self,
        rect: tuple[int, int, int, int],
        text: str,
        font: pygame.font.Font,
        bg_color: tuple[int, int, int] = (45, 50, 60),
        hover_color: tuple[int, int, int] = (65, 75, 90),
        text_color: tuple[int, int, int] = (240, 240, 240),
        disabled_color: tuple[int, int, int] = (25, 27, 30),
        disabled_text_color: tuple[int, int, int] = (100, 100, 100)
    ):
        """
        Khởi tạo đối tượng Button với các thông số kích thước và màu sắc.
        Tham số nhận vào: Tọa độ (rect), văn bản (text), font chữ và các mã màu (RGB).
        Trả về: Không có (None).
        """
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.disabled_color = disabled_color
        self.disabled_text_color = disabled_text_color

        self.is_hovered: bool = False
        self.is_enabled: bool = True

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        """
        Kiểm tra xem tọa độ chuột hiện tại có nằm trong vùng của nút hay không.
        Tham số nhận vào: Tọa độ chuột hiện tại dạng (x, y).
        Trả về: True nếu nút đang được bật và chuột nằm trong nút, ngược lại False.
        """
        # Điều kiện: Nút phải ở trạng thái is_enabled và tọa độ chuột chạm vào rect
        return self.is_enabled and self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Lắng nghe và xử lý sự kiện di chuột hoặc click chuột trái từ hệ thống.
        Tham số nhận vào: Đối tượng sự kiện (pygame.event.Event) từ vòng lặp chính.
        Trả về: True nếu người dùng vừa click chuột trái vào nút, ngược lại False.
        """
        if event.type == pygame.MOUSEMOTION:
            # Cập nhật trạng thái hover khi chuột di chuyển qua nút
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Kiểm tra nếu nhấn chuột trái (button == 1) và tọa độ hợp lệ
            if self.is_clicked(event.pos):
                return True
                
        return False

    def draw(self, screen: pygame.Surface) -> None:
        """
        Vẽ hình ảnh của nút lên bề mặt màn hình tùy thuộc vào trạng thái hiện tại.
        Tham số nhận vào: Bề mặt màn hình chính (pygame.Surface).
        Trả về: Không có (None).
        """
        # Xác định màu nền và màu chữ dựa trên trạng thái kích hoạt hoặc hover
        if not self.is_enabled:
            current_bg_color = self.disabled_color
            current_text_color = self.disabled_text_color
        else:
            current_bg_color = self.hover_color if self.is_hovered else self.bg_color
            current_text_color = self.text_color

        # Vẽ hình chữ nhật bo góc 4 pixel
        pygame.draw.rect(screen, current_bg_color, self.rect, border_radius=4)
        
        # Vẽ viền mỏng bao quanh nút
        border_color = (80, 85, 95) if self.is_enabled else (40, 40, 45)
        pygame.draw.rect(screen, border_color, self.rect, width=1, border_radius=4)

        # Căn giữa và render văn bản
        text_surface = self.font.render(self.text, True, current_text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)