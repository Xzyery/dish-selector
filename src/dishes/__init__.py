from PIL import Image

class Dish:
    def __init__(self, name, image_path):
        self.name = name
        self.image_path = image_path

    def to_dict(self):
        return {
            "name": self.name,
            "image_path": self.image_path
        }