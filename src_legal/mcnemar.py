import os
import re
import json
import pandas as pd
import ast
from collections import defaultdict
from pathlib import Path
from statsmodels.stats.contingency_tables import mcnemar
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter

from domain_config import *

# ── 검증 대상 ──
language = "법률지표"
model_A = "gemma-4-26B-A4B-Legel"
model_B = "midm-legal"
# model_B = "llama-legal"
# model_B = "gemma-4-26B-A4B-it"
# model_B = "gpt-5.4-mini"
# model_B = "midm-250-pro-march26"

BENCHMARKS = LAW_BENCHMARKS
DOMAIN = LAW_DOMAIN

DOMAIN_SLUG = {
    "법률지표": "legal_benchmarks",
    "공통지표": "common_benchmarks",
}


def build_result_filename(model_A: str, model_B: str, lang: str) -> str:
    domain = DOMAIN_SLUG.get(lang, lang)
    return (
        f"{model_A}"
        f"__vs__{model_B}__{domain}.xlsx"
    )

# 정규화된 법률 데이터 루트 (cwd 무관하게 repo 루트 기준)
REPO_ROOT = Path(__file__).resolve().parent.parent
LEGAL_BASE = REPO_ROOT / "법률지표"

_TS_RE = re.compile(r"_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?$")


def resolve_bench_dirs(model, folder_name):
    """법률/{model}/**/{folder_name}/{run}/ 형태에서 samples 를 직접 담은 run 폴더들을 반환."""
    root = LEGAL_BASE / model
    hits = set()
    for r, _dirs, files in os.walk(root):
        if any(_is_sample_file(f) for f in files):
            if folder_name in str(r).split(os.sep):
                hits.add(r)
    return sorted(hits)


def _clean_task(name):
    """파일명 task 에서 legal_cot_ / legal_ / cot_ 접두어 제거."""
    for p in ("legal_cot_", "legal_", "cot_"):
        if name.startswith(p):
            return name[len(p):]
    return name


def norm_task_name(filename):
    """samples_ 접두어와 뒤쪽 타임스탬프 제거한 task 이름."""
    name = os.path.splitext(filename)[0]
    if name.startswith("samples_"):
        name = name[len("samples_"):]
    return _TS_RE.sub("", name)


def derive_category(bench_clean, task_norm):
    """모델 간 일치하는 clean 카테고리명 생성."""
    if bench_clean in SINGLE_FILE_BENCH:
        return bench_clean
    return _clean_task(task_norm)


def benchmark_display_name(benchmark_name: str) -> str:
    """엑셀 출력용 벤치마크 표시명."""
    if benchmark_name == KBL_BAR_EXAM_BENCHMARK:
        return KBL_BAR_EXAM_LABEL
    return benchmark_name


def kbl_bar_exam_group(final_df: pd.DataFrame, domain: str | None = None) -> pd.DataFrame:
    """kbl_bar_exam_em 벤치마크 전체 또는 분야(civil/...)별 서브셋."""
    sub = final_df[final_df["benchmark"] == KBL_BAR_EXAM_BENCHMARK]
    if domain is None:
        return sub
    token = f"_{domain}_"
    return sub[sub["category"].astype(str).str.contains(token, regex=False)]


def kbl_bar_exam_aggregate_labels() -> list[str]:
    labels = [KBL_BAR_EXAM_LABEL]
    labels.extend(f"{KBL_BAR_EXAM_LABEL}_{d}" for d in KBL_BAR_EXAM_DOMAINS)
    return labels


def kolbench_combined_group(final_df: pd.DataFrame) -> pd.DataFrame:
    """kolbench_qa + kolbench_reason + kolbench_dq 합산 서브셋."""
    present = set(final_df["benchmark"].unique())
    keys = [b for b in KOLBENCH_BENCHMARKS if b in present]
    if not keys:
        return final_df.iloc[0:0].copy()
    return final_df[final_df["benchmark"].isin(keys)].copy()


_TS_FIND = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?")


def _is_sample_file(filename: str) -> bool:
    return filename.startswith("samples") and (
        filename.endswith(".jsonl") or filename.endswith(".xlsx")
    )


def _pick_latest_per_task(files):
    """files: [(folder, filename)]. task 당 최신 1개.
    jsonl/xlsx 가 모두 있으면 jsonl 우선, jsonl 없을 때만 xlsx 사용."""
    by_task = defaultdict(list)
    for folder, fn in files:
        by_task[norm_task_name(fn)].append((folder, fn))

    picked = []
    for _task, items in by_task.items():
        jsonls = [(d, f) for d, f in items if f.endswith(".jsonl")]
        xlsxs = [(d, f) for d, f in items if f.endswith(".xlsx")]
        pool = jsonls if jsonls else xlsxs

        best = None
        for folder, fn in pool:
            m = _TS_FIND.search(fn)
            ts = m.group(0) if m else ""
            if best is None or ts > best[0]:
                best = (ts, folder, fn)
        picked.append((best[1], best[2]))
    return picked


def _list_sample_files(dirs):
    """run 폴더에서 samples*.jsonl / samples*.xlsx 수집 후 task 당 최신 1개."""
    all_files = [
        (d, f) for d in dirs for f in os.listdir(d)
        if _is_sample_file(f) and not f.startswith("._")
    ]
    return _pick_latest_per_task(all_files)


def read_sample_dataframe(file_path: str) -> pd.DataFrame:
    """samples jsonl/xlsx → DataFrame."""
    if file_path.endswith(".jsonl"):
        return pd.read_json(file_path, lines=True, encoding="utf-8-sig")
    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path, engine="openpyxl")
    raise ValueError(f"[❌ 오류] 지원하지 않는 samples 형식: {file_path}")

# 정답률 점수 열 파란색 칠하기.
def color_accuracy_columns(file_path: str, sheet_name: str, model_A: str, model_B: str):
    wb = load_workbook(file_path)
    ws = wb[sheet_name]

    # 하늘색 채움 스타일 (Hex: #CCFFFF)
    fill = PatternFill(start_color="CCECFF", end_color="CCECFF", fill_type="solid")

    # 헤더에서 대상 열 인덱스 찾기
    header = [cell.value for cell in ws[1]]
    target_cols = []
    for col_idx, col_name in enumerate(header, start=1):
        if col_name in [f"{model_A}_정답률", f"{model_B}_정답률"]:
            target_cols.append(col_idx)

    # 해당 열에 색칠
    for col_idx in target_cols:
        for row in ws.iter_rows(min_row=2, min_col=col_idx, max_col=col_idx):
            for cell in row:
                cell.fill = fill

    wb.save(file_path)

# 엑셀 칸 늘리기    
def autofit_excel_columns(file_path: str, sheet_name: str):
    wb = load_workbook(file_path)
    ws = wb[sheet_name]

    for column_cells in ws.columns:
        max_length = 0
        column = column_cells[0].column  # Get the column index (1-based)
        column_letter = get_column_letter(column)

        for cell in column_cells:
            try:
                cell_value = str(cell.value) if cell.value is not None else ""
                max_length = max(max_length, len(cell_value))
            except:
                pass

        adjusted_width = max_length + 5  # 여유 공간 추가
        ws.column_dimensions[column_letter].width = adjusted_width

    wb.save(file_path)

# 유의함 행 빨간색 칠하기.
def highlight_significant_rows_for_all_benchmarks(file_path: str, category_benchmarks: list[str]):
    wb = load_workbook(file_path)
    red_fill = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")
    target_sheet_names = []

    # 맥네마 시트 이름 자동 생성
    for benchmark in category_benchmarks:
        target_sheet_names.extend([
            f"benchmark_mcnemar",
            f"{benchmark}",
            f"지표_mcnemar"
        ])

    for sheet_name in target_sheet_names:
        if sheet_name not in wb.sheetnames:
            continue

        ws = wb[sheet_name]
        header = [cell.value for cell in ws[1]]

        # 유의성 컬럼 찾기
        significance_col = None
        for idx, col_name in enumerate(header):
            if str(col_name).strip() in ["유의성 판단"]:
                significance_col = idx + 1
                break

        if significance_col is None:
            continue

        count = 0
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            cell = row[significance_col - 1]
            if str(cell.value).strip() == "유의함":
                for c in row:
                    c.fill = red_fill
                count += 1

    wb.save(file_path)

# 유의함 칸만 빨간색 칠하기.    
def highlight_significance_column(ws, sig_col_name="유의성 판단"):
    # 색상 정의
    red_fill = PatternFill(start_color="FF9999", end_color="FF9999", fill_type="solid")

    # 첫 번째 행에서 해당 컬럼 인덱스를 찾음
    headers = [cell.value for cell in ws[1]]
    try:
        sig_col_idx = headers.index(sig_col_name) + 1  # 1-based index
    except ValueError:
        return  # 컬럼 없으면 스킵

    # 두 번째 행부터 쭉 내려가면서 "유의함"이면 빨강 채우기
    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=sig_col_idx)
        if str(cell.value).strip() == "유의함":
            cell.fill = red_fill

# ifbench true, false 불러오기
def _to_bool(v):
    # TRUE/FALSE/True/False/1/0/문자열/NaN 모두 안전 변환
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "y", "yes"):
        return True
    if s in ("false", "0", "n", "no", "", "nan", "none", "null"):
        return False
    # 그 외는 literal_eval 시도
    try:
        return bool(ast.literal_eval(s))
    except Exception:
        return False
def _to_list_bool(v):
    if isinstance(v, list):
        return [_to_bool(x) for x in v]

    s = str(v).strip()

    if s in ("", "nan", "none", "null"):
        return []

    # JSON 소문자 → Python 대문자 변환
    s2 = (
        s.replace("true", "True")
          .replace("false", "False")
          .replace("null", "None")
    )

    try:
        x = ast.literal_eval(s2)
        if isinstance(x, list):
            return [_to_bool(i) for i in x]
    except Exception:
        pass

    # 단일 스칼라 fallback
    return [_to_bool(s)]

def _ifeval_rows_from_record(data, benchmark_name: str, model: str, row_idx: int) -> list[dict]:
    score = data["score"] if "score" in data else data

    def _as_list(val):
        if isinstance(val, list):
            return val
        if isinstance(val, str):
            try:
                parsed = ast.literal_eval(val)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
        return [val]

    rows = [
        {
            "id": f"{benchmark_name}_{row_idx}_plsa",
            "benchmark": benchmark_name,
            "category": f"{benchmark_name}_plsa",
            f"{model}_EM": score["prompt_level_strict_acc"],
        }
    ]
    for j, val in enumerate(_as_list(score["inst_level_strict_acc"]), 1):
        rows.append({
            "id": f"{benchmark_name}_{row_idx}-{j}_ilsa",
            "benchmark": benchmark_name,
            "category": f"{benchmark_name}_ilsa",
            f"{model}_EM": val,
        })
    rows.append({
        "id": f"{benchmark_name}_{row_idx}_plla",
        "benchmark": benchmark_name,
        "category": f"{benchmark_name}_plla",
        f"{model}_EM": score["prompt_level_loose_acc"],
    })
    for j, val in enumerate(_as_list(score["inst_level_loose_acc"]), 1):
        rows.append({
            "id": f"{benchmark_name}_{row_idx}-{j}_illa",
            "benchmark": benchmark_name,
            "category": f"{benchmark_name}_illa",
            f"{model}_EM": val,
        })
    return rows


# 특정 벤치마크 점수 불러오기 (koifeval 등 ifeval 형식)
def load_ifeval_result(model, benchmark_name):
    dirs = resolve_bench_dirs(model, LAW_BENCH_FOLDERS[benchmark_name])
    files = _list_sample_files(dirs)
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {benchmark_name}: samples jsonl/xlsx 파일이 없습니다.")

    folder, fn = files[0]
    filepath = os.path.join(folder, fn)
    rows = []

    if fn.endswith(".jsonl"):
        with open(filepath, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                rows.extend(_ifeval_rows_from_record(json.loads(line), benchmark_name, model, i))
    else:
        df = read_sample_dataframe(filepath)
        for i, record in df.iterrows():
            rows.extend(_ifeval_rows_from_record(record.to_dict(), benchmark_name, model, i))

    return pd.DataFrame(rows)
def load_ifbench_result(model, benchmark_name):
    folder_path = f"./{language}/{model}/{benchmark_name}/"
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"[❌ 폴더없음] {folder_path}")

    # 엑셀/CSV/TSV 우선순위로 탐색
    cand = [f for f in os.listdir(folder_path)
            if f.lower().endswith((".xlsx", ".csv", ".tsv", ".txt"))]
    if not cand:
        raise FileNotFoundError(f"[❌ 파일없음] {folder_path} 내 .xlsx/.csv/.tsv/.txt")

    path = os.path.join(folder_path, cand[0])

    # 1) 표 읽기 (구분자 자동 감지)
    if path.lower().endswith(".xlsx"):
        src = pd.read_excel(path)  # 첫 시트 사용
    else:
        src = pd.read_csv(path, sep=None, engine="python")  # 콤마/탭 자동감지

    # 2) 필수 컬럼 체크 & 정규화
    needed = ["prompt_level_strict_acc", "inst_level_strict_acc",
              "prompt_level_loose_acc", "inst_level_loose_acc"]
    missing = [c for c in needed if c not in src.columns]
    if missing:
        raise ValueError(f"[❌ 컬럼없음] {missing} (파일: {path})")

    sP = src["prompt_level_strict_acc"].map(_to_bool)
    sI = src["inst_level_strict_acc"].map(_to_list_bool)
    lP = src["prompt_level_loose_acc"].map(_to_bool)
    lI = src["inst_level_loose_acc"].map(_to_list_bool)

    # 3) 납작 구조로 변환 (ifeval과 동일 포맷)
    rows = []
    for i in range(len(src)):
        rows.append({
            "id": f"{benchmark_name}_{i}_plsa",
            "benchmark": benchmark_name,
            "category": f"{benchmark_name}_plsa",
            f"{model}_EM": sP.iloc[i],
        })
        for j, val in enumerate(sI.iloc[i], 1):
            rows.append({
                "id": f"{benchmark_name}_{i}-{j}_ilsa",
                "benchmark": benchmark_name,
                "category": f"{benchmark_name}_ilsa",
                f"{model}_EM": val,
            })
        rows.append({
            "id": f"{benchmark_name}_{i}_plla",
            "benchmark": benchmark_name,
            "category": f"{benchmark_name}_plla",
            f"{model}_EM": lP.iloc[i],
        })
        for j, val in enumerate(lI.iloc[i], 1):
            rows.append({
                "id": f"{benchmark_name}_{i}-{j}_illa",
                "benchmark": benchmark_name,
                "category": f"{benchmark_name}_illa",
                f"{model}_EM": val,
            })

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
            # score = data["pass_at_1"]
            score = data["pass_at_1_model"]

            rows.append({
                "id": f"{i}_mbpp",
                "benchmark": benchmark_name,
                "category": "mbpp",
                f"{model}_EM": score
            })
    
    return pd.DataFrame(rows)
def load_humaneval_result(model, benchmark_name):
    # folder_path = f"./영어지표/{model}/{benchmark_name}/"
    folder_path = f"./{language}/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(".jsonl")]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .jsonl 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    rows = []

    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            score = data["pass_at_k"]

            rows.append({"id": f"{i}_humaneval", "benchmark": benchmark_name, "category": "humaneval", f"{model}_EM": score})
    
    return pd.DataFrame(rows)
def load_livecodebench_result(model, benchmark_name):
    folder_path = f"./영어지표/{model}/{benchmark_name}/"
    files = [f for f in os.listdir(folder_path) if f.endswith(('.xlsx', '.json', '.jsonl'))]
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {folder_path}에 .xlsx, .json, .jsonl 파일이 없습니다.")
    
    filepath = os.path.join(folder_path, files[0])
    
    # 확장자에 따라 다른 방식으로 로딩
    if filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    elif filepath.endswith(".json"):
        df = pd.read_json(filepath)
    elif filepath.endswith(".jsonl"):
        df = pd.read_json(filepath, lines=True)
    else:
        raise ValueError(f"[❌ 오류] 지원하지 않는 파일 형식: {filepath}")

    if "pass@1" not in df.columns:
        raise KeyError(f"[❌ 오류] {filepath} 파일에 'pass@1' 컬럼이 없습니다.")

    df_result = pd.DataFrame({
        "id": [f"{i}_livecodebench" for i in range(len(df))],
        "benchmark": benchmark_name,
        "category": "livecodebench",
        f"{model}_EM": df["pass@1"]
    })

    return df_result
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

            rows.append({"id": f"{i}_drop", "benchmark": benchmark_name, "category": "drop", f"{model}_EM": score})
    
    return pd.DataFrame(rows)

# exact_match 종류 구분
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

# model 결과 불러오기
def load_model_result(benchmark_name, model):
    # ifeval 형식 (koifeval)
    if benchmark_name in IFEVAL_BENCH:
        return load_ifeval_result(model, benchmark_name)

    # 정규화 구조에서 실제 run 폴더들을 찾음
    dirs = resolve_bench_dirs(model, LAW_BENCH_FOLDERS[benchmark_name])
    if not dirs:
        raise FileNotFoundError(f"[❌ 폴더없음] {model} / {benchmark_name}")

    # jsonl/xlsx 수집 후 같은 task(재실행)면 최신 run 만 사용
    files = _list_sample_files(dirs)
    if not files:
        raise FileNotFoundError(f"[❌ 없음] {model} / {benchmark_name}: samples jsonl/xlsx 없음")

    df_list = []
    for folder_path, file in files:
        file_path = os.path.join(folder_path, file)
        try:
            df = read_sample_dataframe(file_path)
        except Exception as e:
            raise ValueError(f"[❌ xlsx읽기실패] {file_path}: {e}") from e

        category = derive_category(benchmark_name, norm_task_name(file))
        df['benchmark'] = benchmark_name
        df['category'] = category
        df = rename_and_filter_em_column(df, model)
        df = df.reset_index(drop=True)  # 행 번호 재설정 (파일 단위)
        df['id_idx'] = df.index.astype(str)
        df['id'] = df['category'].astype(str) + '_' + df['id_idx']
        df = df.drop(columns=['id_idx'])
        df_list.append(df)

    full_df = pd.concat(df_list, ignore_index=True, sort=False)
    return full_df

# 유의성 검증
def mcnemar_test(group: pd.DataFrame, model_A: str, model_B: str, alpha: float = 0.05):
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

# 카테고리 별 유의성 검증
def run_category_mcnemar(df: pd.DataFrame, benchmark_name: str, file_path: str):
    """
    특정 벤치마크 내 카테고리별 유의성 검정을 수행하고 엑셀 저장
    """
    print(f"\n[INFO] {benchmark_name} 카테고리별 유의성 검정 시작")
    # 해당 벤치마크에 속한 행만 → 그 안의 카테고리(서브테스크)별로 검정
    # (benchmark 컬럼 기준이라 kmmlu↔kmmlu_pro, ko_sovereign↔ko_sovereign_law 오염 없음)
    sub_df = df[df['benchmark'] == benchmark_name]

    results = []
    for category, group in sub_df.groupby("category"):
        row = mcnemar_test(group, model_A, model_B)
        row = {"카테고리": category, **row}
        results.append(row)

    result_df = pd.DataFrame(results)

    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        result_df.to_excel(writer, sheet_name=f"{benchmark_name}", index=False)

    print(f"[OK] {benchmark_name} 카테고리별 유의성 검정 완료 → sheet: {benchmark_name}")

# 지표 별 유의성 검증
def run_domain_mcnemar(final_df: pd.DataFrame, file_path: str, model_A: str, model_B: str):
    """
    지표(DOMAIN) 단위로 유의성 검정 후 Excel에 저장
    """
    domain_results = []

    for domain_name in DOMAIN:
        keys = DOMAIN_TO_BENCHMARKS.get(domain_name, [])

        group_list = []
        for key in keys:
            if key in final_df["benchmark"].unique():
                g = final_df[final_df["benchmark"] == key]
            elif key in final_df["category"].unique():
                g = final_df[final_df["category"] == key]
            else:
                continue
            group_list.append(g)

        if not group_list:
            continue

        group = pd.concat(group_list, ignore_index=True).drop_duplicates(subset="id")

        if group.empty:
            continue

        row = mcnemar_test(group, model_A, model_B)
        row = {"지표": domain_name, **row}
        domain_results.append(row)

    # 결과 저장
    domain_df = pd.DataFrame(domain_results)

    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        domain_df.to_excel(writer, sheet_name="지표_mcnemar", index=False)

    autofit_excel_columns(file_path, sheet_name="지표_mcnemar")

    print(f"[OK] 지표별 유의성검정 저장 완료 → sheet: 지표_mcnemar")

# ifevla, ko_ifeval 정답률 계산
def compute_ifeval_score(final_df, base_name, model_A, model_B, label="벤치마크", domain_name=None):
    sub_categories = [f"{base_name}_{x}" for x in ["illa", "ilsa", "plla", "plsa"]]
    sub_groups = [
        final_df[final_df["category"] == c]
        for c in sub_categories
        if c in final_df["category"].unique()
    ]
    if not sub_groups:
        return None

    avg_a = sum(g[f"{model_A}_EM"].mean() for g in sub_groups) / len(sub_groups)
    avg_b = sum(g[f"{model_B}_EM"].mean() for g in sub_groups) / len(sub_groups)
    total = sum(len(g) for g in sub_groups)

    return {
        "구분": label,
        "이름": base_name if label == "벤치마크" else domain_name,
        "문제 수": total,
        f"{model_A}_정답수": round(avg_a * total),
        f"{model_A}_정답률": round(avg_a * 100, 2),
        f"{model_B}_정답수": round(avg_b * total),
        f"{model_B}_정답률": round(avg_b * 100, 2),
    }

# 정답률 계산
def compute_group_score(group, name, model_A, model_B, label):
    total = len(group)
    a_correct = group[f"{model_A}_EM"].sum()
    b_correct = group[f"{model_B}_EM"].sum()
    return {
        "구분": label,
        "이름": name,
        "문제 수": total,
        f"{model_A}_정답수": a_correct,
        f"{model_A}_정답률": round(a_correct / total * 100, 2),
        f"{model_B}_정답수": b_correct,
        f"{model_B}_정답률": round(b_correct / total * 100, 2),
    }

# 벤치마크, 카테고리, 지표 평균 정답률 저장
def save_accuracy_by_category(final_df: pd.DataFrame, file_path: str, model_A: str, model_B: str):
    score_cache = {}
    result_rows = []
    benchmark_names = set(final_df["benchmark"].unique())

    # ✅ 1. 벤치마크별
    for benchmark, group in final_df.groupby("benchmark"):
        if benchmark in ["ko_ifeval", "ifeval", "ifbench", "koifeval"]:
            row = compute_ifeval_score(final_df, benchmark, model_A, model_B, label="벤치마크")
            if row:
                result_rows.append(row)
                score_cache[benchmark] = (
                    row[f"{model_A}_정답률"],
                    row[f"{model_B}_정답률"],
                )
            continue
        display_name = benchmark_display_name(benchmark)
        row = compute_group_score(group, display_name, model_A, model_B, label="벤치마크")
        result_rows.append(row)
        score_cache[display_name] = (
            row[f"{model_A}_정답률"], row[f"{model_B}_정답률"]
        )
        if benchmark == KBL_BAR_EXAM_BENCHMARK:
            score_cache[benchmark] = score_cache[display_name]

    # ✅ 1-1. kbl_bar_exam 분야별 (civil / criminal / public / responsibility)
    if KBL_BAR_EXAM_BENCHMARK in benchmark_names:
        for domain in KBL_BAR_EXAM_DOMAINS:
            group = kbl_bar_exam_group(final_df, domain)
            if group.empty:
                continue
            label = f"{KBL_BAR_EXAM_LABEL}_{domain}"
            row = compute_group_score(group, label, model_A, model_B, label="벤치마크")
            result_rows.append(row)
            score_cache[label] = (
                row[f"{model_A}_정답률"], row[f"{model_B}_정답률"]
            )

    # ✅ 1-2. kolbench 합산 (qa + reason + dq)
    if any(b in benchmark_names for b in KOLBENCH_BENCHMARKS):
        group = kolbench_combined_group(final_df)
        if not group.empty:
            row = compute_group_score(
                group, KOLBENCH_LABEL, model_A, model_B, label="벤치마크"
            )
            result_rows.append(row)
            score_cache[KOLBENCH_LABEL] = (
                row[f"{model_A}_정답률"], row[f"{model_B}_정답률"]
            )

    # ✅ 2. 카테고리별 (벤치마크 이름과 겹치면 생략)
    for category, group in final_df.groupby("category"):
        if category in benchmark_names:
            continue
        row = compute_group_score(group, category, model_A, model_B, label="카테고리")
        result_rows.append(row)
        score_cache[category] = (
            row[f"{model_A}_정답률"], row[f"{model_B}_정답률"]
        )

    # ✅ 3. 지시이행도
    instruction_domains = ["한국어지시이행도", "영어지시이행도", "지시이행도"]

    for domain_name in instruction_domains:
        if domain_name not in DOMAIN:
            continue
        instruction_benchmarks = [
            b for b in ["ko_ifeval", "ifeval", "ifbench", "koifeval"]
            if b in final_df["benchmark"].unique()
        ]
        if not instruction_benchmarks:
            continue
        temp_scores_A = []
        temp_scores_B = []
        for bmk in instruction_benchmarks:
            if bmk not in score_cache:
                # 혹시 score_cache에 없으면 여기서라도 계산해둔다.
                row = compute_ifeval_score(final_df, bmk, model_A, model_B, label="벤치마크")
                score_cache[bmk] = (
                    row[f"{model_A}_정답률"],
                    row[f"{model_B}_정답률"]
                )

            a, b = score_cache[bmk]
            temp_scores_A.append(a)
            temp_scores_B.append(b)

        # ★ 지시이행도 도메인 단순평균 row 생성 (여기서 단 1줄!)
        row = {
            "구분": "지표",
            "이름": domain_name,
            "문제 수": "-",
            f"{model_A}_정답수": "-",
            f"{model_A}_정답률": round(sum(temp_scores_A) / len(temp_scores_A), 2),
            f"{model_B}_정답수": "-",
            f"{model_B}_정답률": round(sum(temp_scores_B) / len(temp_scores_B), 2),
        }
        result_rows.append(row)
      

    # ✅ 4. 문제 수 기반 가중 평균 지표 계산 (DOMAIN_TO_BENCHMARKS) ← 단순 평균 우선순위 예외 처리        
    for domain_name, keys in DOMAIN_TO_BENCHMARKS.items():
        if domain_name not in DOMAIN:
            continue
        if domain_name in DOMAIN_AVERAGE:
            continue
        if domain_name in ["한국어지시이행도", "영어지시이행도", "지시이행도"]:
            continue

        group_list = []
        for key in keys:
            if key in final_df["benchmark"].unique():
                group_list.append(final_df[final_df["benchmark"] == key])
            elif key in final_df["category"].unique():
                group_list.append(final_df[final_df["category"] == key])


        if not group_list:
            continue


        group = pd.concat(group_list, ignore_index=True).drop_duplicates(subset="id")
        if group.empty:
            continue


        row = compute_group_score(group, domain_name, model_A, model_B, label="지표")
        result_rows.append(row)
        score_cache[domain_name] = (row[f"{model_A}_정답률"], row[f"{model_B}_정답률"])
    
    # ✅ 5. 단순 평균 방식 지표 계산 (DOMAIN_AVERAGE)
    for domain_name, sub_items in DOMAIN_AVERAGE.items():
        if domain_name not in DOMAIN:
            continue
        if domain_name in ["한국어지시이행도", "영어지시이행도", "지시이행도"]:
            continue
        total_A, total_B, count = 0.0, 0.0, 0
        for item in sub_items:
            if item in score_cache:
                a, b = score_cache[item]
            else:
                if item in final_df["benchmark"].unique():
                    group = final_df[final_df["benchmark"] == item]
                elif item in final_df["category"].unique():
                        group = final_df[final_df["category"] == item]
                else:
                    continue
                if group.empty:
                    continue
                a = group[f"{model_A}_EM"].mean() * 100
                b = group[f"{model_B}_EM"].mean() * 100
            total_A += a
            total_B += b
            count += 1


        if count > 0:
            row = {
                "구분": "지표",
                "이름": domain_name,
                "문제 수": "-",
                f"{model_A}_정답수": "-",
                f"{model_A}_정답률": round(total_A / count, 2),
                f"{model_B}_정답수": "-",
                f"{model_B}_정답률": round(total_B / count, 2),
            }
            result_rows.append(row)
            score_cache[domain_name] = (row[f"{model_A}_정답률"], row[f"{model_B}_정답률"])

    # ✅ 저장
    acc_df = pd.DataFrame(result_rows).sort_values(by=["구분", "이름"])
    significance_dict = load_significance_from_mcnemar(
        file_path=file_path,
        category_benchmarks=CATEGORY_BENCHMARKS,  # ← 네가 정의해둔 카테고리 벤치마크 목록
    )
    acc_df["유의성 판단"] = acc_df.apply(
        lambda row: significance_dict.get((row["구분"], row["이름"]), ""), axis=1
    )
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        acc_df.to_excel(writer, sheet_name="정답률", index=False)

    autofit_excel_columns(file_path, sheet_name="정답률")
    color_accuracy_columns(file_path, sheet_name="정답률", model_A=model_A, model_B=model_B)

    # ✅ 유의성 판단 빨간색 적용
    wb = load_workbook(file_path)
    ws_accuracy = wb["정답률"]
    highlight_significance_column(ws_accuracy)
    wb.save(file_path)

    print("[OK] 정답률 시트 저장 완료 → sheet: 정답률")

# 정답률 시트에 유의성 결과 붙이기
def load_significance_from_mcnemar(file_path: str, category_benchmarks: list[str]) -> dict:
    wb = load_workbook(file_path, data_only=True)
    result_dict = {}

    # ✅ 1. 벤치마크: benchmark_mcnemar 시트
    if "benchmark_mcnemar" in wb.sheetnames:
        ws = wb["benchmark_mcnemar"]
        headers = [cell.value for cell in ws[1]]

        name_idx = headers.index("벤치마크") if "벤치마크" in headers else None
        sig_idx = headers.index("유의성 판단") if "유의성 판단" in headers else None

        if name_idx is not None and sig_idx is not None:
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                name = str(row[name_idx].value).strip()
                sig = str(row[sig_idx].value).strip()
                result_dict[("벤치마크", name)] = sig

    # ✅ 2. 카테고리: 각 벤치마크 시트에서
    for benchmark in category_benchmarks:
        if benchmark not in wb.sheetnames:
            continue

        ws = wb[benchmark]
        headers = [cell.value for cell in ws[1]]

        name_idx = headers.index("카테고리") if "카테고리" in headers else None
        sig_idx = headers.index("유의성 판단") if "유의성 판단" in headers else None

        if name_idx is not None and sig_idx is not None:
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                name = str(row[name_idx].value).strip()
                sig = str(row[sig_idx].value).strip()
                result_dict[("카테고리", name)] = sig

    # ✅ 3. 지표: 지표_mcnemar 시트에서
    if "지표_mcnemar" in wb.sheetnames:
        ws = wb["지표_mcnemar"]
        headers = [cell.value for cell in ws[1]]

        name_idx = headers.index("지표") if "지표" in headers else None
        sig_idx = headers.index("유의성 판단") if "유의성 판단" in headers else None

        if name_idx is not None and sig_idx is not None:
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                name = str(row[name_idx].value).strip()
                sig = str(row[sig_idx].value).strip()
                result_dict[("지표", name)] = sig

    return result_dict

# 시트 순서 재정렬
def reorder_sheets(file_path: str, priority_order: list[str]):
    wb = load_workbook(file_path)

    # 우선순위 있는 시트 → 순서대로
    new_order = []
    for sheet_name in priority_order:
        if sheet_name in wb.sheetnames:
            new_order.append(wb[sheet_name])

    # 나머지 시트 → 기존 순서 유지
    for sheet in wb.worksheets:
        if sheet not in new_order:
            new_order.append(sheet)

    wb._sheets = new_order
    wb.save(file_path)
    print(f"[OK] 시트 순서 재정렬 완료 → {priority_order} 우선")

# Main
print("\n" + "=" * 72)
print(f"■ 유의성 검증  기준={model_A}   vs   대상={model_B}")
print("=" * 72)

all_results = []
skipped = []

for benchmark in BENCHMARKS:
    try:
        df_A = load_model_result(benchmark, model_A)
        df_B = load_model_result(benchmark, model_B)

        if len(df_A) != len(df_B):
            raise ValueError(f"행 개수 불일치 (A={len(df_A)}, B={len(df_B)})")

        raw_df = df_A[['id', 'category', 'benchmark']].copy()

        merged = pd.merge(raw_df, df_A[['id', f"{model_A}_EM"]], on="id", how="left")
        merged = pd.merge(merged, df_B[['id', f"{model_B}_EM"]], on="id", how="left")

        # 문항 대응(id 정렬) 불일치 방어
        if merged[f"{model_A}_EM"].isna().any() or merged[f"{model_B}_EM"].isna().any():
            raise ValueError("id 정렬 불일치 (카테고리/순서 상이)")

        all_results.append(merged)
        print(f"[OK]   {benchmark}: {merged.shape[0]} rows")
    except Exception as e:
        # 대상 모델에 없거나 문항수가 다른 벤치마크는 건너뜀
        print(f"[SKIP] {benchmark}: {e}")
        skipped.append(benchmark)
        continue


if all_results:
    final_df = pd.concat(all_results, ignore_index=True)
    final_df = final_df[['id', 'benchmark', 'category', f'{model_A}_EM', f'{model_B}_EM']]
    result_dir = REPO_ROOT / "result"
    os.makedirs(result_dir, exist_ok=True)
    file_path = str(result_dir / build_result_filename(model_A, model_B, language))
    final_df.to_excel(file_path, index=False)
    print(f"[완료] 저장됨 → {file_path}")

    ### ✅ 유의성 검증 ###
    mcnemar_results = []

    for benchmark_name, group in final_df.groupby("benchmark"):
        row = mcnemar_test(group, model_A, model_B)
        row = {"벤치마크": benchmark_display_name(benchmark_name), **row}
        mcnemar_results.append(row)

    if KBL_BAR_EXAM_BENCHMARK in final_df["benchmark"].unique():
        for domain in KBL_BAR_EXAM_DOMAINS:
            group = kbl_bar_exam_group(final_df, domain)
            if group.empty:
                continue
            row = mcnemar_test(group, model_A, model_B)
            row = {"벤치마크": f"{KBL_BAR_EXAM_LABEL}_{domain}", **row}
            mcnemar_results.append(row)

    if any(b in final_df["benchmark"].unique() for b in KOLBENCH_BENCHMARKS):
        group = kolbench_combined_group(final_df)
        if not group.empty:
            row = mcnemar_test(group, model_A, model_B)
            row = {"벤치마크": KOLBENCH_LABEL, **row}
            mcnemar_results.append(row)

    mcnemar_df = pd.DataFrame(mcnemar_results)

    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        mcnemar_df.to_excel(writer, sheet_name="benchmark_mcnemar", index=False)

    autofit_excel_columns(file_path, sheet_name="benchmark_mcnemar")

    print(f"[OK] 유의성검정 결과 저장 완료 → sheet: benchmark_mcnemar")


else:
    print("[경고] 결과 없음")

### ✅ 카테고리 유의성 검증 ###
for bench in BENCHMARKS:
    if bench in CATEGORY_BENCHMARKS:
        run_category_mcnemar(final_df, bench, file_path)

### ✅ 지표별 카테고리 구성 및 문제 수 출력 ###
print("\n✅ 지표별 카테고리 구성 및 문제 수:")
for domain_name in DOMAIN:
    categories = DOMAIN_TO_BENCHMARKS.get(domain_name, [])
    total_count = 0
    print(f"\n📌 지표: {domain_name}")
    for cat in categories:
        # cat이 benchmark에 해당하면 benchmark 기준으로, 아니면 category 기준으로 세기
        if cat in final_df["benchmark"].unique():
            count = final_df[final_df["benchmark"] == cat].shape[0]
        elif cat in final_df["category"].unique():
            count = final_df[final_df["category"] == cat].shape[0]
        else:
            count = 0  # 어느 곳에도 없으면 0
        total_count += count
        print(f"   ├─ {cat:<35} : {count}개")
    print(f"   └─ 총합{'':<33} : {total_count}개")

### ✅ 지표 유의성 검증 ###
run_domain_mcnemar(final_df, file_path, model_A, model_B)

### ✅ 정답률 ###
save_accuracy_by_category(final_df, file_path, model_A, model_B)

highlight_significant_rows_for_all_benchmarks(
    file_path=file_path,
    category_benchmarks=CATEGORY_BENCHMARKS
)

# ✅ 시트 순서 조정
priority_order = ["Sheet1", "benchmark_mcnemar", "지표_mcnemar", "정답률"]
reorder_sheets(file_path, priority_order)