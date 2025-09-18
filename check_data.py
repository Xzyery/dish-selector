import json
import os

# 检查数据文件
data_file = "dishes.json"
if os.path.exists(data_file):
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print("dishes.json 内容:")
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"读取 dishes.json 失败: {e}")
else:
    print("dishes.json 文件不存在")

# 检查图片文件
images_dir = "images"
if os.path.exists(images_dir):
    print(f"\n图片目录 {images_dir} 中的文件:")
    for file in os.listdir(images_dir):
        file_path = os.path.join(images_dir, file)
        print(f"  {file} - {os.path.getsize(file_path)} bytes")
else:
    print(f"图片目录 {images_dir} 不存在")