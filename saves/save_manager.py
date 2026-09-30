import json
import os


def save_game(data: dict, filename: str = "saves/save.json") -> bool:
    try:
        directory = os.path.dirname(filename)

        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        return True

    except (OSError, TypeError, ValueError) as error:
        print(f"Lỗi khi lưu game: {error}")
        return False


def load_game(filename: str) -> dict:
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file save '{filename}'.")
        return {}

    except json.JSONDecodeError as error:
        print(f"Lỗi: File save không chứa JSON hợp lệ: {error}")
        return {}

    except OSError as error:
        print(f"Lỗi khi đọc file save: {error}")
        return {}