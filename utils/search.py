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

# kmmlu 폴더 경로 설정
base_dir = "한국어지표"
folder1 = os.path.join(base_dir, "Midm-Pro-v2.4", "kmmlu")
folder2 = os.path.join(base_dir, "Midm-Pro-v2.3", "kmmlu")

print("=== KMMLU subset별 행 개수 비교 ===")
print(f"폴더1 (v2.4): {folder1}")
print(f"폴더2 (v2.3): {folder2}")
print()

# 각 폴더의 파일 목록 가져오기
files1 = [f for f in os.listdir(folder1) if f.endswith(".jsonl")]
files2 = [f for f in os.listdir(folder2) if f.endswith(".jsonl")]

# 공통 파일 찾기
common_files = set(files1) & set(files2)
only_in_v24 = set(files1) - set(files2)
only_in_v23 = set(files2) - set(files1)

print(f"📊 파일 개수 통계:")
print(f"  - v2.4에만 있는 파일: {len(only_in_v24)}개")
print(f"  - v2.3에만 있는 파일: {len(only_in_v23)}개")
print(f"  - 공통 파일: {len(common_files)}개")
print()

# v2.4에만 있는 파일들
if only_in_v24:
    print("🔍 v2.4에만 있는 파일들:")
    for file in sorted(only_in_v24):
        file_path = os.path.join(folder1, file)
        count = count_lines(file_path)
        print(f"  - {file}: {count}행")
    print()

# v2.3에만 있는 파일들
if only_in_v23:
    print("🔍 v2.3에만 있는 파일들:")
    for file in sorted(only_in_v23):
        file_path = os.path.join(folder2, file)
        count = count_lines(file_path)
        print(f"  - {file}: {count}행")
    print()

# 공통 파일들의 행 개수 비교
mismatches = []
matches = []

print("📋 공통 파일들의 행 개수 비교:")
for file in sorted(common_files):
    path1 = os.path.join(folder1, file)
    path2 = os.path.join(folder2, file)
    
    count1 = count_lines(path1)
    count2 = count_lines(path2)
    
    if count1 != count2:
        mismatches.append((file, count1, count2))
        print(f"  ❌ {file}: v2.4={count1}행, v2.3={count2}행 (차이: {count1-count2:+d})")
    else:
        matches.append((file, count1))
        print(f"  ✅ {file}: {count1}행")

print()
print(f"📈 요약:")
print(f"  - 일치하는 파일: {len(matches)}개")
print(f"  - 불일치하는 파일: {len(mismatches)}개")

if mismatches:
    print(f"\n🔍 불일치 파일 상세:")
    for file, count1, count2 in mismatches:
        print(f"  - {file}: v2.4={count1}행, v2.3={count2}행 (차이: {count1-count2:+d})")