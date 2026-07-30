"""
kolbench (qa / dq / reason) 세부 도메인별 정답률 집계 → 모델 비교 CSV/엑셀.

집계 축:
  kolbench_qa     : sub_domain, sub_category, difficulty
  kolbench_dq     : sub_domain, sub_category, difficulty
  kolbench_reason : sub_domain, difficulty

사용 예:
  python kolbench_detail_scores.py                  # 전체 모델 비교 CSV
  python kolbench_detail_scores.py --model gemma-4-26B-A4B-it  # 단일 모델
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGAL_BASE = REPO_ROOT / "법률"
DEFAULT_OUT = REPO_ROOT / "result"

# (표시명, 폴더명) — 사용자 예시 컬럼 순서
MODELS = [
    ("gemma-4-26B-A4B-Legal", "gemma-4-26B-A4B-Legel"),
    ("gemma-4-26B-A4B-it", "gemma-4-26B-A4B-it"),
    ("GPT5.4mini", "gpt-5.4-mini"),
    ("midm-250-pro-march26", "midm-250-pro-march26"),
    ("Llama3.1-kt-3.0-Legal-74B-1.1", "llama-legal"),
    ("Midm-2.3.1-Base-Legal-1.0", "midm-legal"),
]

BENCH_CONFIG = {
    "kolbench_qa": {
        "group_by": ["sub_domain", "sub_category", "difficulty"],
        "csv_title": "KoLBench_QA",
        "label": "법률지식QA",
    },
    "kolbench_dq": {
        "group_by": ["sub_domain", "sub_category", "difficulty"],
        "csv_title": "KoLBench_DQ",
        "label": "법률문서해석",
    },
    "kolbench_reason": {
        "group_by": ["sub_domain", "difficulty"],
        "csv_title": "KoLBench_Reason",
        "label": "법률추론",
    },
}

ORDER = {
    "sub_domain": ["공법", "민사", "형사"],
    "sub_category": ["기관", "절차", "제도", "조문", "직무", "판례", "법적결론 추론"],
    "difficulty": ["하", "중", "상", "하중", "중상"],
}

AXIS_LABEL = {
    "overall": "전체",
    "sub_domain": "sub_domain",
    "sub_category": "sub_category",
    "difficulty": "difficulty",
}

_TS_FIND = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?")
_TS_RE = re.compile(r"_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?$")


def _is_sample_file(filename: str) -> bool:
    return filename.startswith("samples") and (
        filename.endswith(".jsonl") or filename.endswith(".xlsx")
    )


def norm_task_name(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    if name.startswith("samples_"):
        name = name[len("samples_"):]
    return _TS_RE.sub("", name)


def _pick_latest(files: list[tuple[str, str]]) -> tuple[str, str] | None:
    """[(folder, filename), ...] 중 최신 1개. jsonl 우선."""
    if not files:
        return None
    jsonls = [(d, f) for d, f in files if f.endswith(".jsonl")]
    pool = jsonls if jsonls else files
    best = None
    for folder, fn in pool:
        m = _TS_FIND.search(fn)
        ts = m.group(0) if m else ""
        if best is None or ts > best[0]:
            best = (ts, folder, fn)
    return best[1], best[2]


def find_sample_file(model: str, bench: str) -> Path | None:
    root = LEGAL_BASE / model
    if not root.is_dir():
        return None
    hits: list[tuple[str, str]] = []
    for r, _dirs, files in os.walk(root):
        if bench not in Path(r).parts:
            continue
        for f in files:
            if _is_sample_file(f) and not f.startswith("._"):
                if norm_task_name(f) == bench or bench in f:
                    hits.append((r, f))
    picked = _pick_latest(hits)
    if picked is None:
        return None
    folder, fn = picked
    return Path(folder) / fn


def _parse_doc(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s or s in ("nan", "None", "null"):
            return {}
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return {}
    return {}


def load_samples(path: Path) -> pd.DataFrame:
    if path.suffix == ".jsonl":
        rows = []
        with open(path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        df = pd.DataFrame(rows)
    elif path.suffix == ".xlsx":
        try:
            df = pd.read_excel(path, engine="openpyxl")
        except Exception as e:
            # 손상된 xlsx 대비: 동일 stem jsonl 시도
            alt = path.with_suffix(".jsonl")
            if alt.exists():
                return load_samples(alt)
            raise ValueError(f"xlsx 로드 실패: {path} ({e})") from e
    else:
        raise ValueError(f"지원하지 않는 형식: {path}")

    if "doc" in df.columns:
        docs = df["doc"].map(_parse_doc)
        doc_df = pd.json_normalize(docs)
        for col in ("sub_domain", "sub_category", "difficulty", "category", "index"):
            if col in doc_df.columns and col not in df.columns:
                df[col] = doc_df[col]

    if "exact_match" not in df.columns:
        raise KeyError(f"exact_match 컬럼 없음: {path}")

    df["exact_match"] = pd.to_numeric(df["exact_match"], errors="coerce")
    return df


def _sort_key(field: str, value):
    order = ORDER.get(field, [])
    try:
        return (0, order.index(value))
    except ValueError:
        return (1, str(value))


def score_map(df: pd.DataFrame, group_by: list[str]) -> dict[tuple[str, str], dict]:
    """(축, 구분) → {문항수, 정답수, 정답률}."""
    out: dict[tuple[str, str], dict] = {}
    n = len(df)
    correct = float(df["exact_match"].sum())
    out[("전체", "전체")] = {
        "문항수": n,
        "정답수": int(correct),
        "정답률": (correct / n) if n else 0.0,
    }
    for field in group_by:
        if field not in df.columns:
            raise KeyError(f"필드 없음: {field}")
        for key, g in df.groupby(field, dropna=False):
            label = key if pd.notna(key) else "(결측)"
            nn = len(g)
            cc = float(g["exact_match"].sum())
            out[(field, str(label))] = {
                "문항수": nn,
                "정답수": int(cc),
                "정답률": (cc / nn) if nn else 0.0,
            }
    return out


def collect_row_keys(
    group_by: list[str],
    model_scores: dict[str, dict[tuple[str, str], dict]],
) -> list[tuple[str, str]]:
    """실제 데이터가 있는 (축, 구분)만, 고정 순서대로 반환."""
    present: set[tuple[str, str]] = set()
    for scores in model_scores.values():
        present |= set(scores.keys())

    rows: list[tuple[str, str]] = []
    if ("전체", "전체") in present:
        rows.append(("전체", "전체"))

    for field in group_by:
        # 고정 순서 먼저
        for v in ORDER.get(field, []):
            key = (field, v)
            if key in present:
                rows.append(key)
        # ORDER에 없는 값
        extras = sorted(
            (k for k in present if k[0] == field and k not in rows),
            key=lambda k: _sort_key(k[0], k[1]),
        )
        rows.extend(extras)
    return rows


def pct1(x: float | None) -> float | None:
    if x is None:
        return None
    return round(x * 100, 1)


def build_compare_table(
    bench: str,
    model_scores: dict[str, dict[tuple[str, str], dict]],
    display_names: list[str],
) -> pd.DataFrame:
    """
    컬럼: 축 | 구분 | 문항수 | model1 | model2 | ...
    점수는 % (소수 1자리). 문항수는 첫 번째 유효 모델 기준.
    """
    cfg = BENCH_CONFIG[bench]
    final_order = collect_row_keys(cfg["group_by"], model_scores)

    rows = []
    for axis, label in final_order:
        # 문항수: 모델 간 동일하면 단일값, 다르면 n1/n2/...
        counts = []
        for name in display_names:
            sc = model_scores.get(name, {}).get((axis, label))
            if sc is not None:
                counts.append(sc["문항수"])
        if not counts:
            continue
        if len(set(counts)) == 1:
            n_display: int | str = counts[0]
        else:
            n_display = "/".join(str(c) for c in counts)

        row = {
            "축": AXIS_LABEL.get(axis, axis),
            "구분": label,
            "문항수": n_display,
        }
        for name in display_names:
            sc = model_scores.get(name, {}).get((axis, label))
            row[name] = pct1(sc["정답률"]) if sc is not None else None
        rows.append(row)

    return pd.DataFrame(rows)


def write_compare_excel(
    tables: dict[str, pd.DataFrame],
    out_path: Path,
    display_names: list[str],
):
    """벤치마크를 한 시트로 합쳐 저장 (CSV 합본과 동일 구조)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)

    parts = []
    for bench, table in tables.items():
        t = table.copy()
        t.insert(0, "벤치마크", BENCH_CONFIG[bench]["csv_title"])
        cols = ["벤치마크", "구분", "축", "문항수"] + display_names
        parts.append(t[cols])
    combined = pd.concat(parts, ignore_index=True)

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        combined.to_excel(writer, sheet_name="kolbench", index=False)

    wb = load_workbook(out_path)
    ws = wb["kolbench"]
    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(color="FFFFFF", bold=True)
    pct_fill = PatternFill("solid", fgColor="CCECFF")
    axis_fill = PatternFill("solid", fgColor="F2F2F2")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    headers = [c.value for c in ws[1]]
    model_cols = [i + 1 for i, h in enumerate(headers) if h in display_names]
    for col_idx in model_cols:
        for row in range(2, ws.max_row + 1):
            cell = ws.cell(row=row, column=col_idx)
            if isinstance(cell.value, (int, float)):
                cell.fill = pct_fill

    if "축" in headers:
        ax_idx = headers.index("축") + 1
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=ax_idx).fill = axis_fill

    for cols in ws.columns:
        max_len = 0
        letter = get_column_letter(cols[0].column)
        for cell in cols:
            val = "" if cell.value is None else str(cell.value)
            max_len = max(max_len, len(val))
        ws.column_dimensions[letter].width = min(max_len + 3, 40)

    wb.save(out_path)


def print_table(bench: str, table: pd.DataFrame, display_names: list[str]):
    cfg = BENCH_CONFIG[bench]
    print(f"\n{'=' * 72}")
    print(f"{cfg['csv_title']} ({cfg['label']})")
    header = f"{'구분':<10} {'축':<14} {'n':>5}"
    for name in display_names:
        short = name if len(name) <= 18 else name[:16] + ".."
        header += f"  {short:>18}"
    print(header)
    print("-" * len(header))
    for _, r in table.iterrows():
        line = f"{str(r['구분']):<10} {str(r['축']):<14} {str(r['문항수']):>5}"
        for name in display_names:
            v = r[name]
            line += f"  {v:>18.1f}" if pd.notna(v) else f"  {'':>18}"
        print(line)


def run_compare(out_dir: Path) -> Path:
    display_names = [d for d, _ in MODELS]
    tables: dict[str, pd.DataFrame] = {}

    for bench, cfg in BENCH_CONFIG.items():
        model_scores: dict[str, dict[tuple[str, str], dict]] = {}
        for display, folder in MODELS:
            path = find_sample_file(folder, bench)
            if path is None:
                print(f"[경고] {display} / {bench} samples 없음")
                continue
            try:
                df = load_samples(path)
                model_scores[display] = score_map(df, cfg["group_by"])
                print(f"[로드] {display:<32} {bench}: {path.name} (n={len(df)})")
            except Exception as e:
                print(f"[오류] {display} / {bench}: {e}")

        if not model_scores:
            print(f"[경고] {bench} 집계 불가 — 모델 데이터 없음")
            continue

        table = build_compare_table(bench, model_scores, display_names)
        tables[bench] = table
        print_table(bench, table, display_names)

    if not tables:
        raise SystemExit("[오류] 집계할 벤치마크가 없습니다.")

    out_dir.mkdir(parents=True, exist_ok=True)
    xlsx_path = out_dir / "kolbench_세부도메인_모델비교.xlsx"
    write_compare_excel(tables, xlsx_path, display_names)
    print(f"\n[저장] {xlsx_path}")
    return xlsx_path


def run_single(model_folder: str, out_dir: Path) -> Path:
    """단일 모델 상세 엑셀 (기존 동작)."""
    display = next((d for d, f in MODELS if f == model_folder), model_folder)
    all_tables = {}
    for bench, cfg in BENCH_CONFIG.items():
        path = find_sample_file(model_folder, bench)
        if path is None:
            print(f"[경고] {model_folder} / {bench} samples 없음")
            continue
        df = load_samples(path)
        scores = {display: score_map(df, cfg["group_by"])}
        table = build_compare_table(bench, scores, [display])
        all_tables[bench] = table
        print_table(bench, table, [display])

    if not all_tables:
        raise SystemExit(f"[오류] 집계할 벤치마크 없음: {model_folder}")

    out_path = out_dir / f"{model_folder}_kolbench_세부도메인_점수.xlsx"
    write_compare_excel(all_tables, out_path, [display])
    print(f"\n[저장] {out_path}")
    return out_path


def parse_args():
    p = argparse.ArgumentParser(description="kolbench 세부 도메인별 점수 집계")
    p.add_argument(
        "--model",
        default=None,
        help="단일 모델 폴더명. 생략 시 전체 모델 비교 CSV 생성",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help=f"출력 디렉터리 (default: {DEFAULT_OUT})",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.model:
        run_single(args.model, args.out)
    else:
        run_compare(args.out)
