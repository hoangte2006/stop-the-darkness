import json
import os

SAVE_FILES = {
    1: "saves/save-slot1.json",
    2: "saves/save-slot2.json",
    3: "saves/save-slot3.json"
}


def save_game(data: dict, saveSlot: int = 1) -> bool:
    filename = SAVE_FILES.get(saveSlot)

    if filename is None:
        print("Không có save-slot tương ứng")
        return False

    try:
        directory = os.path.dirname(filename)
        os.makedirs(directory, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return True

    except (OSError, TypeError, ValueError) as error:
        print(f"Lỗi khi lưu game: {error}")
        return False


def load_game(saveSlot: int = 1) -> dict:
    filename = SAVE_FILES.get(saveSlot)

    if filename is None:
        print("Không có save-slot tương ứng")
        return {}

    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)

            if not isinstance(data, dict):
                print("Lỗi: Dữ liệu save không phải dictionary")
                return {}

            return data

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file save '{filename}'")
        return {}

    except json.JSONDecodeError as error:
        print(f"Lỗi: File save không chứa JSON hợp lệ: {error}")
        return {}

    except OSError as error:
        print(f"Lỗi khi đọc file save: {error}")
        return {}