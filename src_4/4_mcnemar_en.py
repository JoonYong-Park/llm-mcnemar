import os
import pandas as pd
from statsmodels.stats.contingency_tables import mcnemar
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
import sys
import json

model_A = "midm"
model_B = "qwen"

### 전체 벤치마크
# BENCHMARKS = ['aime2025','aqua-rat','bbh','gpqa','gsm8k','humaneval','ifeval','livecodebench','math','mbpp','mmlu_pro','musr','winogrande']
# DOMAIN = ['추론','전문지식','지시이행도','수학','코딩']

### 수학 벤치마크
BENCHMARKS = ['aime2025','gsm8k','humaneval','livecodebench','math','mbpp']
DOMAIN = ['코딩']

### sm
# BENCHMARKS = ['bbh','boolq','drop','gpqa','gsm8k','ifeval','mmlu_pro','winogrande','openbookqa','piqa']
# DOMAIN = ['전문지식-CKP','지시이행도-CKP','수학-CKP']

BENCHMARKS_LIST = ['bbh','boolq','drop','gpqa','gsm8k','ifeval','mmlu_pro','musr','openbookqa','piqa','winogrande','math','mbpp','aqua-rat','aime2025','humaneval','mbpp','livecodebench','HLE']
DOMAIN_TO_BENCHMARKS = {
    '지시이행도-CKP': ['ifeval'],
    '추론-CKP': ['musr','gpqa','winogrande','bbh','openbookqa','drop', 'boolq','piqa'],
    '수학-CKP': ['math'],
    '전문지식-CKP': ['mmlu_pro'],

    '추론': ['musr','gpqa','winogrande','bbh'],
    '전문지식': ['mmlu_pro'],
    '지시이행도': ['ifeval'],
    '수학': ['gsm8k','math','aqua-rat','aime2025'],
    '코딩': ['humaneval','mbpp','livecodebench'],
    # 'HLE': ['HLE'],
}
HIERARCHY = {
    "ifeval": {
        # 'ifeval':['ifeval_illa','ifeval_ilsa','ifeval_plla','ifeval_plsa']
        'ifeval':['ifeval_ilsa','ifeval_plla']
    },
    "bbh":{
        'bbh':["bbh_"]
    },
    "gpqa":{
        'gpqa':["gpqa_"]
    },
    "musr":{
        'musr':["musr_"]
    },
    "mmlu_pro":{
        'mmlu_pro':["mmlu_pro_"]
    },
    "math":{
        'math':["math_"]
    },
}

def load_ifeval_result(model, benchmark_name):
    folder_path = f"./영어지표/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(".jsonl")]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .jsonl 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            score = data["score"] if "score" in data else data

            # rows.append({"id": f"{i}_plsa", "category": "ifeval_plsa", f"{model}_EM": score["prompt_level_strict_acc"]})
            for j, val in enumerate(score["inst_level_strict_acc"], 1):
                rows.append({"id": f"{i}-{j}_ilsa", "category": "ifeval_ilsa", f"{model}_EM": val})
            rows.append({"id": f"{i}_plla", "category": "ifeval_plla", f"{model}_EM": score["prompt_level_loose_acc"]})
            # for j, val in enumerate(score["inst_level_loose_acc"], 1):
            #     rows.append({"id": f"{i}-{j}_illa", "category": "ifeval_illa", f"{model}_EM": val})
    
    return pd.DataFrame(rows)

def load_drop_result(model, benchmark_name):
    folder_path = f"./영어지표/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(".jsonl")]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .jsonl 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            score = data["em"]

            rows.append({"id": f"{i}_drop", "category": "drop", f"{model}_EM": score})
    
    return pd.DataFrame(rows)

def load_mbpp_result(model, benchmark_name):
    folder_path = f"./영어지표/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(".jsonl")]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .jsonl 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            score = data["pass_at_1"]

            rows.append({"id": f"{i}_mbpp", "category": "mbpp", f"{model}_EM": score})
    
    return pd.DataFrame(rows)

def load_humaneval_result(model, benchmark_name):
    folder_path = f"./영어지표/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(".jsonl")]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .jsonl 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            score = data["pass_at_k"]

            rows.append({"id": f"{i}_humaneval", "category": "humaneval", f"{model}_EM": score})
    
    return pd.DataFrame(rows)

def load_livecodebench_result(model, benchmark_name):
    folder_path = f"./영어지표/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .json 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    
    # JSON 파일 읽기
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # pass@1 값들 추출
    pass_at_1_values = [item.get("pass@1", 0.0) for item in data]
    
    df_result = pd.DataFrame({
        "id": [f"{i}_livecodebench" for i in range(len(data))],
        "category": "livecodebench",
        f"{model}_EM": pass_at_1_values
    })

    return df_result

def rename_and_filter_em_column(df: pd.DataFrame, model_name: str) -> pd.DataFrame:
    if 'exact_match' in df.columns:
        df = df.rename(columns={'exact_match': f'{model_name}_EM'})
    elif 'acc' in df.columns:
        df = df.rename(columns={'acc': f'{model_name}_EM'})
    elif 'q_eval' in df.columns:
        df['q_eval'] = df['q_eval'].astype(str).str.lower().str.strip().map({'true': 1, 'false': 0})
        df = df.rename(columns={'q_eval': f'{model_name}_EM'})    
    else:
        raise ValueError(f"[ERROR] {model_name} 결과에 정확도 컬럼이 없습니다.")

    if 'filter' in df.columns:
        filter_values = df['filter'].unique()
        if 'custom-answer' in filter_values:
            df = df[df['filter'] == 'custom-answer']
        elif 'strict-match' in filter_values:
            df = df[df['filter'] == 'strict-match']
        elif 'none' in filter_values:
            df = df[df['filter'] == 'none']
        elif 'get-answer' in filter_values:
            df = df[df['filter'] == 'get-answer']
        elif 'flexible-extract' in filter_values:
            df = df[df['filter'] == 'flexible-extract']
        elif 'custom-extract' in filter_values:
            df = df[df['filter'] == 'custom-extract']
        else:
            pass

    return df

def load_model_result(benchmark_name, model):
    if benchmark_name == "ifeval":
        return load_ifeval_result(model, benchmark_name)
    if benchmark_name == "drop":
        return load_drop_result(model, benchmark_name)
    if benchmark_name == "mbpp":
        return load_mbpp_result(model, benchmark_name)
    if benchmark_name == "humaneval":
        return load_humaneval_result(model, benchmark_name)
    if benchmark_name == "livecodebench":
        return load_livecodebench_result(model, benchmark_name)
    
    df_list = []
    categories = []
    folder_paths = [f"./영어지표/{model}/{benchmark_name}/"]
    for folder_path in folder_paths:
        jsonl_files = [f for f in os.listdir(folder_path) if f.endswith(('.json', '.jsonl', '.xlsx'))]
        for file in jsonl_files:
            file_path = os.path.join(folder_path, file)
            if file.endswith('.json'):
                df = pd.read_json(file_path)
            elif file.endswith('.jsonl'):
                df = pd.read_json(file_path, lines=True, encoding="utf-8-sig")
            elif file.endswith('.xlsx'):
                df = pd.read_excel(file_path)

            base_filename = os.path.splitext(file)[0]
            df['category'] = base_filename
            df = rename_and_filter_em_column(df, model)
            df = df.reset_index(drop=True)
            df['row_idx'] = df.groupby('category').cumcount()
            df['id'] = df['category'] + "_" + df['row_idx'].astype(str)
            # df['id'] = df.apply(lambda x: file.replace('.jsonl', '').replace('.xlsx', '') + str(x.name), axis=1)
            
            
            df_list.append(df)
            categories.append(base_filename)
    full_df = pd.concat(df_list, ignore_index=True, sort=False)
    return full_df

def calculate_mcnemar(group: pd.DataFrame, model_A: str, model_B: str, alpha: float = 0.05):
    a_only = ((group[f"{model_A}_EM"] == 1) & (group[f"{model_B}_EM"] == 0)).sum()
    b_only = ((group[f"{model_A}_EM"] == 0) & (group[f"{model_B}_EM"] == 1)).sum()
    both_correct = ((group[f"{model_A}_EM"] == 1) & (group[f"{model_B}_EM"] == 1)).sum()
    both_wrong = ((group[f"{model_A}_EM"] == 0) & (group[f"{model_B}_EM"] == 0)).sum()

    table = [[both_correct, a_only], [b_only, both_wrong]]
    result = mcnemar(table, exact=False, correction=True)
    p_value = result.pvalue
    statistic = result.statistic
    sig = "-" if (a_only + b_only) < 25 else ("유의함" if p_value < alpha else "유의하지 않음")

    return {
        "A (둘 다 정답)": both_correct,
        f"B ({model_A}만 정답)": a_only,
        f"C ({model_B}만 정답)": b_only,
        "D (둘 다 오답)": both_wrong,
        "통계량": statistic,
        "p값": p_value,
        "유의성 판단": sig
    }

def highlight_significant_cells(ws, 판단_col_name="유의성 판단", 색상="FF9999"):

    header = [cell.value for cell in ws[1]]
    if 판단_col_name not in header:
        print(f"[경고] 헤더에 '{판단_col_name}' 없음 → 색상 적용 생략")
        return
    
    judge_col = header.index(판단_col_name) + 1
    red_fill = PatternFill(start_color=색상, end_color=색상, fill_type="solid")

    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=judge_col)
        if cell.value == "유의함":
            for col in range(1, ws.max_column + 1):
                ws.cell(row=row, column=col).fill = red_fill

def run_category_mcnemar(df: pd.DataFrame, benchmark_name: str, file_path: str):
    """
    특정 벤치마크 내 카테고리별 유의성 검정을 수행하고 엑셀 저장
    """
    print(f"\n[INFO] {benchmark_name} 카테고리별 유의성 검정 시작")
    # print(df[df['benchmark']])
    sub_df = df[df['benchmark'] == benchmark_name]
    sub_df = df[df['category'].str.startswith(f"{benchmark_name}_")]

    results = []
    for category, group in sub_df.groupby("category"):
        row = calculate_mcnemar(group, model_A, model_B)
        row = {"카테고리": category, **row}
        results.append(row)

    result_df = pd.DataFrame(results)

    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        result_df.to_excel(writer, sheet_name=f"{benchmark_name}_by_category", index=False)

    wb = load_workbook(file_path)
    ws = wb[f"{benchmark_name}_by_category"]
    highlight_significant_cells(ws)
    wb.save(file_path)

    print(f"[OK] {benchmark_name} 카테고리별 유의성 검정 완료 → sheet: {benchmark_name}_by_category")

def autofit_column_width(ws):
    """
    워크시트의 각 열 너비를 자동 조정해주는 함수
    """
    for col in ws.columns:
        max_length = 0
        column = col[0].column  # 열 인덱스 (숫자)
        column_letter = get_column_letter(column)  # 열 이름 (예: 'A', 'B', ...)

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        adjusted_width = max_length + 2  # 여유 공간 포함
        ws.column_dimensions[column_letter].width = adjusted_width

def compute_accuracy_by_category(df: pd.DataFrame, model_list: list[str], file_path: str):
    print("\n[INFO] category별 모델 정답률 계산 시작")

    results = []
    categories = set(df['category'].unique())
    general_categories = set(df['benchmark'].unique()) - {"ifeval"}

    # 🔹 평가 대상은: category + (category - category)
    total_categories = categories.union(general_categories - categories)
    category_only_rows = set()

    for category in sorted(total_categories):
        row = {"category": category}
        if category in df['category'].values:
            sub_df = df[df['category'] == category]
        else:
            sub_df = df[df['benchmark'] == category]
            category_only_rows.add(category)
        
        for model in model_list:
            col_name = f"{model}_EM"
            if col_name in sub_df.columns:
                acc = sub_df[col_name].mean() * 100
                row[model] = round(acc, 2)

        results.append(row)

    acc_df = pd.DataFrame(results)

    # 엑셀에 저장
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        acc_df.to_excel(writer, sheet_name="정답률_by_category", index=False)

    # 열 너비 자동 조정 및 저장
    wb = load_workbook(file_path)
    ws = wb["정답률_by_category"]

    # 열 너비 자동 조정 함수
    autofit_column_width(ws)

    wb.save(file_path)
    print(f"[OK] category별 모델 정답률 저장 완료 → sheet: 정답률_by_category")

def highlight_accuracy_rows(ws, benchmarks: list[str], domains: list[str]):
    blue_fill = PatternFill(start_color="CCECFF", end_color="CCECFF", fill_type="solid")  # 파란색
    green_fill = PatternFill(start_color="CCFFCC", end_color="CCFFCC", fill_type="solid")  # 초록색

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):  # 헤더 제외
        category_cell = row[0]
        category_value = str(category_cell.value)

        if category_value in benchmarks:
            for cell in row:
                cell.fill = blue_fill
        elif any(category_value == d or category_value.startswith(d) for d in domains):
            for cell in row:
                cell.fill = green_fill

def append_domain_averages_to_accuracy_sheet(file_path: str, sheet_name: str, domain_to_benchmarks: dict, domain_filter: list[str]):
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    domain_rows = []
    for domain, benchmarks in domain_to_benchmarks.items():
        if domain not in domain_filter:
            continue  # 🔸 DOMAIN에 포함되지 않은 도메인은 스킵

        row = {"category": f"{domain}"}
        if domain == "지시이행도":
            # ifeval_subcats = ["ifeval_plsa", "ifeval_ilsa", "ifeval_plla", "ifeval_illa"]
            ifeval_subcats = ["ifeval_ilsa", "ifeval_plla"]
            for col in df.columns[1:]:
                scores = df[df['category'].isin(ifeval_subcats)][col].dropna().tolist()
                row[col] = round(sum(scores) / len(scores), 2) if scores else None

        else:
            for col in df.columns[1:]:  # 모델별 정답률 열
                scores = df[df['category'].isin(benchmarks)][col].dropna().tolist()
                row[col] = round(sum(scores) / len(scores), 2) if scores else None
        domain_rows.append(row)

    df_final = pd.concat([df, pd.DataFrame(domain_rows)], ignore_index=True)

    # 시트 저장
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_final.to_excel(writer, sheet_name=sheet_name, index=False)

    # 열 너비 조정
    wb = load_workbook(file_path)
    ws = wb[sheet_name]
    autofit_column_width(ws)
    for col in range(2, ws.max_column + 1):
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=col).number_format = '0.00'
    highlight_accuracy_rows(ws, benchmarks=BENCHMARKS, domains=domain_filter)
    wb.save(file_path)
    
    print(f"[OK] 도메인별 평균 정답률 추가 완료 → 시트: {sheet_name}")

def add_significance_to_accuracy_sheet(file_path):
    wb = load_workbook(file_path)
    all_sheetnames = wb.sheetnames

    # 유의성 판단 딕셔너리 초기화
    sig_dict = {}

    # 1. 시트 순회 (Sheet1, 정답률_by_category 제외)
    for sheet_name in all_sheetnames:
        if sheet_name in ['Sheet1', '정답률_by_category']:
            continue

        ws = wb[sheet_name]
        header = [cell.value for cell in ws[1]]

        # 어떤 이름 열이 있는지 확인
        if '카테고리' in header:
            key_col = header.index('카테고리') + 1
        elif '벤치마크' in header:
            key_col = header.index('벤치마크') + 1
        elif '지표' in header:
            key_col = header.index('지표') + 1
        else:
            continue  # 해당 시트는 건너뜀

        sig_col = header.index('유의성 판단') + 1 if '유의성 판단' in header else None
        if not sig_col:
            continue  # 판단값이 없으면 무시

        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            key = str(row[key_col - 1].value).strip()
            sig_value = row[sig_col - 1].value
            if key and sig_value:
                sig_dict[key] = sig_value  # 매핑 등록

    # 2. 정답률 시트에서 category 열과 매칭해서 추가
    acc_ws = wb["정답률_by_category"]
    acc_header = [cell.value for cell in acc_ws[1]]
    category_col = acc_header.index("category") + 1
    new_col_index = acc_ws.max_column + 1
    acc_ws.cell(row=1, column=new_col_index).value = "유의성 판단"

    for row in range(2, acc_ws.max_row + 1):
        category = str(acc_ws.cell(row=row, column=category_col).value).strip()
        sig = sig_dict.get(category)
        if sig:
            acc_ws.cell(row=row, column=new_col_index).value = sig
    
    red_fill = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")

    for row in range(2, acc_ws.max_row + 1):
        cell = acc_ws.cell(row=row, column=new_col_index)
        if str(cell.value).strip() == "유의함":
            cell.fill = red_fill

    # 저장
    wb.save(file_path)
    print(f"[OK] '정답률_by_category' 시트에 유의성 판단 열 추가 완료")

def add_hierarchy_columns_to_accuracy_sheet_prefix(file_path: str, hierarchy: dict):
    wb = load_workbook(file_path)
    ws = wb["정답률_by_category"]
    header = [cell.value for cell in ws[1]]
    category_col_idx = header.index("category") + 1

    # 🔹 열 추가
    ws.insert_cols(1, amount=2)
    ws.cell(row=1, column=1).value = "대분류"
    ws.cell(row=1, column=2).value = "중분류"

    # 🔹 카테고리 기반 대분류/중분류 매핑
    for row in range(2, ws.max_row + 1):
        category_value = str(ws.cell(row=row, column=category_col_idx + 2).value).strip()
        matched = False

        for big_class, sub_dict in hierarchy.items():
            for mid_class, targets in sub_dict.items():
                for target in targets:
                    if big_class == "ifeval":
                        if category_value == target:
                            ws.cell(row=row, column=1).value = big_class
                            ws.cell(row=row, column=2).value = mid_class
                            matched = True
                            break
                    else:
                        if category_value.startswith(target):
                            ws.cell(row=row, column=1).value = big_class
                            ws.cell(row=row, column=2).value = mid_class
                            matched = True
                            break
                if matched:
                    break
            if matched:
                break

        if not matched:
            ws.cell(row=row, column=1).value = category_value
            ws.cell(row=row, column=2).value = category_value

    # 🔹 모든 셀 숫자 포맷: 소수점 둘째 자리
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
        for cell in row[2:]:  # 대/중분류 제외
            if isinstance(cell.value, float):
                cell.number_format = "0.00"

    # 🔹 유의함 빨간색 표시
    sig_col = None
    for i, val in enumerate(ws[1], start=1):
        if val.value == "유의성 판단":
            sig_col = i
            break

    if sig_col:
        red_fill = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")
        for row in range(2, ws.max_row + 1):
            sig_val = ws.cell(row=row, column=sig_col).value
            if sig_val == "유의함":
                ws.cell(row=row, column=sig_col).fill = red_fill

    # 🔹 정렬: 대분류 → 중분류
    data_rows = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        data_rows.append(list(row))

    data_rows.sort(key=lambda x: (x[0], x[1]))  # 대분류, 중분류 기준

    for i, row_vals in enumerate(data_rows, start=2):
        for j, val in enumerate(row_vals, start=1):
            ws.cell(row=i, column=j).value = val
            if isinstance(val, float):
                ws.cell(row=i, column=j).number_format = "0.00"

    ws.column_dimensions['A'].width = 20  # 대분류
    ws.column_dimensions['B'].width = 20  # 중분류
    wb.save(file_path)
    print(f"[✅ 완료] 정답률_by_category 시트에 대분류/중분류 추가 + 정렬 + 소수점 포맷 + 유의함 색상 표시")

all_results = []

for benchmark in BENCHMARKS:
    try:
        df_A = load_model_result(benchmark, model_A)
        df_B = load_model_result(benchmark, model_B)

        if len(df_A) != len(df_B):
            raise ValueError(f"[❌ 행 개수 불일치] {benchmark}: A={len(df_A)}행, B={len(df_B)}행")

        raw_df = df_A[['id', 'category']].copy()
        raw_df['benchmark'] = benchmark

        merged = pd.merge(raw_df, df_A[['id', f"{model_A}_EM"]], on="id", how="left")
        merged = pd.merge(merged, df_B[['id', f"{model_B}_EM"]], on="id", how="left")

        all_results.append(merged)
        print(f"[OK] {benchmark}: {merged.shape[0]} rows")
    except Exception as e:
        print(f"[ERROR] {benchmark}: {e}")
        sys.exit(1)


if all_results:
    final_df = pd.concat(all_results, ignore_index=True)
    final_df = final_df[['id', 'benchmark', 'category', f'{model_A}_EM', f'{model_B}_EM']]
    os.makedirs("./result", exist_ok=True)
    file_path = f"./result/{model_A}_{model_B}_영어_통합결과.xlsx"
    final_df.to_excel(file_path, index=False)
    print(f"[완료] 저장됨 → {file_path}")

    ### ✅ 여기부터 유의성검정 코드 작성 시작 ###
    mcnemar_results = []

    for benchmark_name, group in final_df.groupby("benchmark"):
        row = calculate_mcnemar(group, model_A, model_B)
        row = {"벤치마크": benchmark_name, **row}

        mcnemar_results.append(row)

    mcnemar_df = pd.DataFrame(mcnemar_results)

    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        mcnemar_df.to_excel(writer, sheet_name="benchmark_mcnemar", index=False)

    print(f"[OK] 유의성검정 결과 저장 완료 → sheet: benchmark_mcnemar")

    wb = load_workbook(file_path)
    ws = wb["benchmark_mcnemar"]

    highlight_significant_cells(ws)
    autofit_column_width(ws)

    wb.save(file_path)
    print(f"[OK] '유의함' 셀 빨간색 색칠 완료 → {file_path}")

else:
    print("[경고] 결과 없음")

for bench in BENCHMARKS:
    if bench in ['bbh', 'gpqa', 'mmlu_pro', 'musr', 'ifeval', 'math']:
        run_category_mcnemar(final_df, bench, file_path)

domain_results = []

for domain_name in DOMAIN:
    benchmark = DOMAIN_TO_BENCHMARKS.get(domain_name, [])
    group = final_df[final_df['benchmark'].isin(benchmark)]

    if group.empty:
        continue

    row = calculate_mcnemar(group, model_A, model_B)
    row = {"지표": domain_name, **row}
    domain_results.append(row)

domain_df = pd.DataFrame(domain_results)

with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    domain_df.to_excel(writer, sheet_name="지표_mcnemar", index=False)

wb = load_workbook(file_path)
ws = wb["지표_mcnemar"]
highlight_significant_cells(ws)
autofit_column_width(ws)

wb.save(file_path)
print(f"[OK] 지표별(category 기준) 유의성 검정 완료 → sheet: 지표_mcnemar")

print("\n✅ 지표별 카테고리 구성 및 문제 수:")
for domain_name in DOMAIN:
    benchmarks = DOMAIN_TO_BENCHMARKS.get(domain_name, [])
    total_count = 0
    print(f"\n📌 지표: {domain_name}")
    for bench in benchmarks:
        count = final_df[final_df['benchmark'] == bench].shape[0]
        total_count += count
        print(f"   ├─ {bench:<35} : {count}개")
    print(f"   └─ 총합{'':<33} : {total_count}개")


model_list = [model_A, model_B]  
compute_accuracy_by_category(final_df, model_list, file_path)
append_domain_averages_to_accuracy_sheet(file_path, "정답률_by_category", DOMAIN_TO_BENCHMARKS, DOMAIN)
add_significance_to_accuracy_sheet(file_path)
add_hierarchy_columns_to_accuracy_sheet_prefix(file_path, HIERARCHY)
wb = load_workbook(file_path)

desired_order = ["Sheet1", "benchmark_mcnemar", "지표_mcnemar", "정답률_by_category"]
ordered_sheets = [ws for name in desired_order for ws in wb.worksheets if ws.title == name]
remaining_sheets = [ws for ws in wb.worksheets if ws.title not in desired_order]

wb._sheets = ordered_sheets + remaining_sheets

wb.save(file_path)
print("[OK] 시트 순서 정리 완료")