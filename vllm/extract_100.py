import json

filename = 'extracted_file.json'  # 替换为你的文件名
new_filename = 'short_first.json'  # 你要写入的新文件名
json_objects = []

with open(filename, 'r') as file:
    data = json.load(file)

filtered_data = [item for item in data if 'human' in item]

json_objects = sorted(filtered_data, key=lambda x: len(x['human']), reverse=False)


# 写入新文件
with open(new_filename, 'w') as new_file:
    json.dump(json_objects, new_file, ensure_ascii=False, indent=4)
