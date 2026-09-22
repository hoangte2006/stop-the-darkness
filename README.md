3. NGUYÊN TẮC LÀM VIỆC CHỐNG XUNG ĐỘT (TEAM RULES)
Nguyên tắc "Ranh giới thư mục" (Directory Ownership):

Mỗi thành viên chỉ viết code trong file/thư mục được phân công.

Tuyệt đối không tự ý sửa main.py và game_state.py. Nếu một thành viên cần dữ liệu gì, người đó phải báo cho bạn (Leader) để bạn viết sẵn một hàm giao tiếp (API nội bộ).

Quy tắc phân nhánh Git (Branching Workflow):

Nhánh main là nhánh thiêng liêng, code phải luôn luôn chạy được (không bao giờ push trực tiếp vào main).

Mỗi thành viên tự tạo nhánh theo cú pháp:

TV2: feature/renderer-sprites

TV3: feature/ui-sidebar

TV4: feature/save-load-system

TV5: feature/audio-system

TV6: feature/map-generator

Khi làm xong và test chạy thử ổn định trên máy cá nhân, thành viên mở Pull Request (PR) trên GitHub. Chỉ có bạn (Leader) là người duyệt, kiểm tra và bấm nút Merge vào nhánh main.

Nguyên tắc Hợp đồng Giao tiếp (Interface Contract First):

Trước khi code, thống nhất rõ kiểu dữ liệu đầu vào và đầu ra.

Ví dụ cho TV3 (Làm nút bấm): Bạn chỉ yêu cầu TV3 cung cấp hàm btn.handle_event(event) -> bool.

Ví dụ cho TV4 (Làm Save/Load): Bạn chỉ yêu cầu TV4 viết hàm nhận vào một dictionary save_game(data: dict, filename: str) -> bool.

Họp đồng bộ tiến độ (Weekly Standup):

Mỗi tuần họp nhanh 15–20 phút (online qua Discord hoặc gặp trực tiếp trên trường) để từng người báo cáo:

Tuần qua đã làm xong file nào?

Đang bị kẹt (blocker) ở đâu?

Mục tiêu tuần tới là gì?# stop-the-darkness-A-
