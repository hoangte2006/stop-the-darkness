import pygame
import random

# Khởi tạo pygame ẩn (không cần mở cửa sổ)
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

# Tạo một bức tranh trống kích thước 240x40 (6 ô, mỗi ô 40x40)
sheet = pygame.Surface((240, 40))

def draw_pixel_block(x, y, color, size=4):
    """Hàm vẽ các khối vuông nhỏ để tạo cảm giác Pixel Art"""
    pygame.draw.rect(sheet, color, (x, y, size, size))

# ==========================================
# 0: ĐẤT (Dirt) - Nền nâu với các hạt sạn
# ==========================================
pygame.draw.rect(sheet, (139, 69, 19), (0, 0, 40, 40))
for _ in range(20):
    px = random.randint(0, 9) * 4
    py = random.randint(0, 9) * 4
    draw_pixel_block(px, py, (101, 51, 15)) # Chấm nâu đậm
    
# ==========================================
# 1: RỪNG (Forest) - Nền cỏ và tán cây thông
# ==========================================
pygame.draw.rect(sheet, (85, 127, 43), (40, 0, 40, 40)) 
pygame.draw.polygon(sheet, (20, 80, 20), [(60, 8), (45, 35), (75, 35)]) # Tán lá sau
pygame.draw.polygon(sheet, (34, 139, 34), [(60, 15), (50, 35), (70, 35)]) # Tán lá trước
pygame.draw.rect(sheet, (90, 50, 20), (58, 35, 4, 5)) # Gốc cây

# ==========================================
# 2: NÚI (Mountain) - Đá xám có chóp tuyết
# ==========================================
pygame.draw.rect(sheet, (100, 140, 170), (80, 0, 40, 40)) # Màu nền (bầu trời mờ)
pygame.draw.polygon(sheet, (100, 100, 100), [(100, 5), (80, 40), (120, 40)]) # Thân núi
pygame.draw.polygon(sheet, (140, 140, 140), [(100, 5), (90, 40), (105, 40)]) # Đổ bóng núi
pygame.draw.polygon(sheet, (255, 255, 255), [(100, 5), (93, 18), (100, 22), (107, 18)]) # Tuyết

# ==========================================
# 3: NƯỚC (Water) - Nước xanh dương có gợn sóng biển
# ==========================================
pygame.draw.rect(sheet, (30, 144, 255), (120, 0, 40, 40))
for y in [10, 20, 30]:
    for x in range(120, 160, 8):
        if random.random() > 0.3:
            # Vẽ các đường gợn sóng sáng màu
            pygame.draw.line(sheet, (135, 206, 250), (x, y), (x+4, y), 2)

# ==========================================
# 4: CÔNG TRÌNH (Structure) - Tường gạch cổ điển
# ==========================================
pygame.draw.rect(sheet, (178, 34, 34), (160, 0, 40, 40)) # Nền gạch đỏ
for y in range(0, 40, 10):
    pygame.draw.line(sheet, (200, 200, 200), (160, y), (200, y), 2) # Xi măng ngang
    offset = 5 if (y // 10) % 2 == 0 else 0 # Xếp gạch so le
    for x in range(160, 200, 10):
        pygame.draw.line(sheet, (200, 200, 200), (x + offset, y), (x + offset, y+10), 2)

# ==========================================
# 5: BÓNG TỐI (Darkness) - Đen tuyền có viền mờ
# ==========================================
pygame.draw.rect(sheet, (10, 10, 15), (200, 0, 40, 40))
# Thêm vài chấm "sao" hoặc viền để không bị chìm hoàn toàn
for _ in range(5):
    draw_pixel_block(200 + random.randint(0, 9)*4, random.randint(0, 9)*4, (30, 30, 40), size=2)

# Xuất ra file PNG
pygame.image.save(sheet, "spritesheet.png")
print("🎉 Đã tạo thành công file 'spritesheet.png' trong thư mục hiện tại!")
print("Bây giờ bạn có thể chạy lại file code vẽ bản đồ trước đó để xem thành quả.")
pygame.quit()