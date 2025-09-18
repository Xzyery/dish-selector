import json
from dishes import Dish

def load_dishes(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Dish(d["name"], d["image_path"]) for d in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_dishes(dishes, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump([dish.to_dict() for dish in dishes], f, ensure_ascii=False, indent=2)