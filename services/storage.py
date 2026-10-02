"""JSON or SQLite game save and load services."""

import json
import os


def save_game(data_dict, filename="saves/save.json"):
    """Ghi `data_dict` (từ GameState.to_dict()) ra file JSON. Trả về True nếu thành công."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)

    return True


def load_game(filename):
    """Đọc file JSON, trả về dict để truyền vào GameState.load_from_dict()."""
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
