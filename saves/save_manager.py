import json
import os


def save_game(data_dict, filename="saves/save.json"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data_dict, file, ensure_ascii=False, indent=4)


def load_game(filename):
    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    mock_data = {
        "grid": [
            [
                {
                    "terrain": "grass",
                    "is_dark": False,
                    "building": None
                }
                for _ in range(12)
            ]
            for _ in range(12)
        ],
        "resources": {
            "wood": 100,
            "stone": 50,
            "tech": 20,
            "light": 75
        }
    }

    save_game(mock_data)

    loaded_data = load_game("saves/save.json")

    assert loaded_data == mock_data

    assert len(loaded_data["grid"]) == 12
    assert len(loaded_data["grid"][0]) == 12

    assert loaded_data["resources"]["wood"] == 100
    assert loaded_data["resources"]["stone"] == 50
    assert loaded_data["resources"]["tech"] == 20
    assert loaded_data["resources"]["light"] == 75

    print("Save game thành công!")
    print("Load game thành công!")
    print("Dữ liệu toàn vẹn!")