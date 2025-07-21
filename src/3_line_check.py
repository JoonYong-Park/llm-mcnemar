import os
import pandas as pd

def count_lines(file_path):
    if file_path.endswith(".jsonl"):
        with open(file_path, "r", encoding="utf-8-sig") as f:
            return sum(1 for _ in f)
    elif file_path.endswith(".xlsx"):
        df = pd.read_excel(file_path)
        return len(df)
    return None

base_dir = os.path.join("영어지표")
folder1 = os.path.join(base_dir, "Llama-74B")
folder2 = os.path.join(base_dir, "GPT4o")

file_dict_1 = {}
for root, _, files in os.walk(folder1):
    for file in files:
        if file.endswith((".jsonl", ".xlsx")):
            name_wo_ext = os.path.splitext(file)[0]
            rel_path = os.path.relpath(os.path.join(root, file), folder1)
            folder = os.path.dirname(rel_path)
            file_dict_1[(folder, name_wo_ext)] = os.path.join(root, file)

file_dict_2 = {}
for root, _, files in os.walk(folder2):
    for file in files:
        if file.endswith((".jsonl", ".xlsx")):
            name_wo_ext = os.path.splitext(file)[0]
            rel_path = os.path.relpath(os.path.join(root, file), folder2)
            folder = os.path.dirname(rel_path)
            file_dict_2[(folder, name_wo_ext)] = os.path.join(root, file)

common_keys = sorted(set(file_dict_1.keys()) & set(file_dict_2.keys()))

mismatch_results = []

for idx, key in enumerate(common_keys, 1):
    rel_folder, base_name = key
    path1 = file_dict_1[key]
    path2 = file_dict_2[key]

    count1 = count_lines(path1)
    count2 = count_lines(path2)

    if count1 is None or count2 is None:
        continue  # 지원 안 하는 파일은 무시
    if count1 != count2:
        display_path = os.path.join(rel_folder, base_name)
        mismatch_results.append(f"{len(mismatch_results)+1}. {display_path} - 문항 수 불일치, 폴더1: {count1}, 폴더2: {count2}")

if mismatch_results:
    for line in mismatch_results:
        print(line)
else:
    print(f"- {folder1}\n- {folder2}\n불일치 없음\n")