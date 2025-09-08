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

# 기준 경로 설정
base_dir = os.path.join("영어지표")
folder1 = os.path.join(base_dir, "midm")
folder2 = os.path.join(base_dir, "qwen")

# 폴더1에서 모든 파일 상대 경로 기준으로 dict 생성 (확장자 제외)
file_dict_1 = {}
for root, _, files in os.walk(folder1):
    for file in files:
        if file.endswith((".jsonl", ".xlsx")):
            name_wo_ext = os.path.splitext(file)[0]
            rel_path = os.path.relpath(os.path.join(root, file), folder1)
            folder = os.path.dirname(rel_path)
            file_dict_1[(folder, name_wo_ext)] = os.path.join(root, file)

# 폴더2에서도 동일하게
file_dict_2 = {}
for root, _, files in os.walk(folder2):
    for file in files:
        if file.endswith((".jsonl", ".xlsx")):
            name_wo_ext = os.path.splitext(file)[0]
            rel_path = os.path.relpath(os.path.join(root, file), folder2)
            folder = os.path.dirname(rel_path)
            file_dict_2[(folder, name_wo_ext)] = os.path.join(root, file)

# 공통 이름 기준 비교
common_keys = sorted(set(file_dict_1.keys()) & set(file_dict_2.keys()))

# 불일치 결과 저장
total_compared = 0
mismatches = []
matches = []

for idx, key in enumerate(common_keys, 1):
    rel_folder, base_name = key
    path1 = file_dict_1[key]
    path2 = file_dict_2[key]

    count1 = count_lines(path1)
    count2 = count_lines(path2)

    if count1 is None or count2 is None:
        continue  # 지원 안 하는 파일은 무시
    total_compared += 1
    display_path = os.path.join(rel_folder, base_name)
    if count1 != count2:
        mismatches.append(f"{len(mismatches)+1}. {display_path} - ❌ 불일치, 폴더1: {count1}, 폴더2: {count2}")
    else:
        matches.append(f"{len(matches)+1}. {display_path} - ✅ 일치, 행 수: {count1}")

# 결과 출력
if mismatches:
    for line in mismatches:
        print(line)
else:
    print(f"✅ 모든 공통 파일의 문항 수가 일치합니다. (총 {total_compared}개 파일 비교됨)")