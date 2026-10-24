"""Finding and loading model evaluation results (samples files).

Layout: {cfg.DATA_PATH}/{model}/**/{benchmark folder}/**/samples_*_<TS>.jsonl|xlsx
The benchmark folder is looked up in cfg.BENCH_FOLDERS; if absent, the benchmark name is the folder name.
"""
import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

# Benchmarks read with the ifeval-format loader (prompt_level_*_acc)
IFEVAL_BENCH = {"ifeval", "ko_ifeval", "koifeval"}

# Task-name prefixes stripped from category names (only the first match)
TASK_PREFIXES = ("legal_cot_", "legal_", "cot_")

_TS_RE = re.compile(r"_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?$")
_TS_FIND = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?")


# ── File discovery ──
def _is_sample_file(filename: str) -> bool:
    return (
        filename.startswith("samples")
        and filename.endswith((".jsonl", ".xlsx"))
        and not filename.startswith("._")
    )


def find_bench_dirs(cfg, model, benchmark, is_target=_is_sample_file):
    """Folders under {DATA_PATH}/{model}/ that lie inside the benchmark folder and directly contain target files."""
    root = cfg.DATA_PATH / model
    folder = cfg.BENCH_FOLDERS.get(benchmark, benchmark)
    hits = []
    for r, _dirs, files in os.walk(root):
        if folder in Path(r).relative_to(root).parts and any(is_target(f) for f in files):
            hits.append(r)
    return sorted(hits)


def _find_files(cfg, model, benchmark, exts):
    """For special loaders: files with the given extensions in the benchmark folder, as [(folder, filename)]."""
    def is_target(f):
        return f.lower().endswith(exts) and not f.startswith("._")

    dirs = find_bench_dirs(cfg, model, benchmark, is_target)
    files = [(d, f) for d in dirs for f in sorted(os.listdir(d)) if is_target(f)]
    if not files:
        raise FileNotFoundError(f"no {exts} files for {model} / {benchmark}")
    return files


def norm_task_name(filename):
    """Task name with the samples_ prefix and trailing timestamp removed."""
    name = os.path.splitext(filename)[0]
    if name.startswith("samples_"):
        name = name[len("samples_"):]
    return _TS_RE.sub("", name)


def _clean_task(name):
    """Strip the legal_cot_ / legal_ / cot_ prefix from a task name."""
    for p in TASK_PREFIXES:
        if name.startswith(p):
            return name[len(p):]
    return name


def derive_category(cfg, benchmark, task_norm):
    """Category name that is identical across models."""
    if benchmark in cfg.SINGLE_FILE_BENCH:
        return benchmark
    return _clean_task(task_norm)


def _pick_latest_per_task(files):
    """files: [(folder, filename)]. Keep the latest file per task.
    jsonl is preferred; xlsx is used only when a task has no jsonl."""
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


def list_sample_files(dirs):
    """Collect samples*.jsonl / samples*.xlsx from run folders, latest one per task."""
    all_files = [(d, f) for d in dirs for f in os.listdir(d) if _is_sample_file(f)]
    return _pick_latest_per_task(all_files)


def read_sample_dataframe(file_path: str) -> pd.DataFrame:
    """samples jsonl/xlsx -> DataFrame."""
    if file_path.endswith(".jsonl"):
        return pd.read_json(file_path, lines=True, encoding="utf-8-sig")
    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path, engine="openpyxl")
    raise ValueError(f"unsupported samples format: {file_path}")


# ── Value conversion ──
def _to_bool(v):
    # Safely converts TRUE/FALSE/True/False/1/0/strings/NaN
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    if s in ("true", "1", "y", "yes"):
        return True
    if s in ("false", "0", "n", "no", "", "nan", "none", "null"):
        return False
    # Otherwise try literal_eval
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

    # JSON lowercase literals -> Python
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

    # Fallback: single scalar
    return [_to_bool(s)]


def _question_keys(doc_ids, n):
    """Per-question pairing keys: doc_id when every row has a unique one, else the row number.

    Pairing on doc_id keeps the two models aligned even if their files list questions in a different order.
    """
    if doc_ids is not None and len(doc_ids) == n:
        keys = [str(d) for d in doc_ids]
        if all(d is not None and str(d) != "nan" for d in doc_ids) and len(set(keys)) == n:
            return keys
    return [str(i) for i in range(n)]


def _ifeval_rows(benchmark_name, model, i, strict_p, strict_i, loose_p, loose_i):
    """One ifeval prompt -> flat rows for plsa / ilsa / plla / illa."""
    rows = [{
        "id": f"{benchmark_name}_{i}_plsa",
        "benchmark": benchmark_name,
        "category": f"{benchmark_name}_plsa",
        f"{model}_EM": strict_p,
    }]
    for j, val in enumerate(strict_i, 1):
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
        f"{model}_EM": loose_p,
    })
    for j, val in enumerate(loose_i, 1):
        rows.append({
            "id": f"{benchmark_name}_{i}-{j}_illa",
            "benchmark": benchmark_name,
            "category": f"{benchmark_name}_illa",
            f"{model}_EM": val,
        })
    return rows


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


# ── Benchmark-specific loaders ──
def load_ifeval_result(cfg, model, benchmark_name):
    """ifeval / ko_ifeval / koifeval (samples jsonl or xlsx)."""
    files = list_sample_files(find_bench_dirs(cfg, model, benchmark_name))
    if not files:
        raise FileNotFoundError(f"no samples jsonl/xlsx for {model} / {benchmark_name}")

    folder, fn = files[0]
    filepath = os.path.join(folder, fn)
    if fn.endswith(".jsonl"):
        with open(filepath, "r", encoding="utf-8") as f:
            records = [json.loads(line) for line in f]
    else:
        records = [r.to_dict() for _, r in read_sample_dataframe(filepath).iterrows()]

    keys = _question_keys([r.get("doc_id") for r in records], len(records))
    rows = []
    for key, data in zip(keys, records):
        score = data["score"] if "score" in data else data
        rows.extend(_ifeval_rows(
            benchmark_name, model, key,
            score["prompt_level_strict_acc"], _as_list(score["inst_level_strict_acc"]),
            score["prompt_level_loose_acc"], _as_list(score["inst_level_loose_acc"]),
        ))
    return pd.DataFrame(rows)


def load_ifbench_result(cfg, model, benchmark_name):
    folder, fn = _find_files(cfg, model, benchmark_name, (".xlsx", ".csv", ".tsv", ".txt"))[0]
    path = os.path.join(folder, fn)

    # Read the table (delimiter auto-detected)
    if path.lower().endswith(".xlsx"):
        src = pd.read_excel(path)  # first sheet
    else:
        src = pd.read_csv(path, sep=None, engine="python")  # comma/tab auto-detected

    needed = ["prompt_level_strict_acc", "inst_level_strict_acc",
              "prompt_level_loose_acc", "inst_level_loose_acc"]
    missing = [c for c in needed if c not in src.columns]
    if missing:
        raise ValueError(f"missing columns {missing} in {path}")

    sP = src["prompt_level_strict_acc"].map(_to_bool)
    sI = src["inst_level_strict_acc"].map(_to_list_bool)
    lP = src["prompt_level_loose_acc"].map(_to_bool)
    lI = src["inst_level_loose_acc"].map(_to_list_bool)

    rows = []
    for i in range(len(src)):
        rows.extend(_ifeval_rows(benchmark_name, model, i, sP.iloc[i], sI.iloc[i], lP.iloc[i], lI.iloc[i]))
    return pd.DataFrame(rows)


def _load_jsonl_score(cfg, model, benchmark_name, score_key):
    """Simple loader: per-question score (score_key) from one jsonl file."""
    folder, fn = _find_files(cfg, model, benchmark_name, (".jsonl",))[0]
    rows = []
    with open(os.path.join(folder, fn), "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            data = json.loads(line)
            rows.append({
                "id": f"{i}_{benchmark_name}",
                "benchmark": benchmark_name,
                "category": benchmark_name,
                f"{model}_EM": data[score_key],
            })
    return pd.DataFrame(rows)


def load_mbpp_result(cfg, model, benchmark_name):
    return _load_jsonl_score(cfg, model, benchmark_name, "pass_at_1_model")


def load_humaneval_result(cfg, model, benchmark_name):
    return _load_jsonl_score(cfg, model, benchmark_name, "pass_at_k")


def load_drop_result(cfg, model, benchmark_name):
    return _load_jsonl_score(cfg, model, benchmark_name, "em")


def load_livecodebench_result(cfg, model, benchmark_name):
    folder, fn = _find_files(cfg, model, benchmark_name, (".xlsx", ".json", ".jsonl"))[0]
    filepath = os.path.join(folder, fn)

    if filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)
    elif filepath.endswith(".jsonl"):
        df = pd.read_json(filepath, lines=True)
    else:
        df = pd.read_json(filepath)

    if "pass@1" not in df.columns:
        raise KeyError(f"no 'pass@1' column in {filepath}")

    return pd.DataFrame({
        "id": [f"{i}_livecodebench" for i in range(len(df))],
        "benchmark": benchmark_name,
        "category": "livecodebench",
        f"{model}_EM": df["pass@1"],
    })


def load_functionchat_result(cfg, model, benchmark_name):
    rows = []
    for folder, file in _find_files(cfg, model, benchmark_name, (".jsonl",)):
        base_filename = os.path.splitext(file)[0]
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                data = json.loads(line)
                # is_pass lives under report_arguments
                is_pass = data.get("report_arguments", {}).get("is_pass", "fail")
                rows.append({
                    "id": f"{base_filename}_{i}",
                    "benchmark": benchmark_name,
                    "category": base_filename,
                    f"{model}_EM": 1 if is_pass.lower() == "pass" else 0,
                })
    return pd.DataFrame(rows)


def load_nestful_result(cfg, model, benchmark_name):
    rows = []
    for folder, file in _find_files(cfg, model, benchmark_name, (".jsonl",)):
        base_filename = os.path.splitext(file)[0]
        with open(os.path.join(folder, file), "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                metrics = json.loads(line).get("evaluation_metrics", {})
                # Each metric becomes its own category (no parsing_error counts as correct)
                scores = {
                    "win_score": metrics.get("win_score", False),
                    "full_match": metrics.get("full_match", False),
                    "intent_match": metrics.get("intent_match", False),
                    "no_parsing_error": not metrics.get("parsing_error", False),
                }
                for key, ok in scores.items():
                    rows.append({
                        "id": f"{base_filename}_{i}_{key}",
                        "benchmark": benchmark_name,
                        "category": f"{benchmark_name}_{key}",
                        f"{model}_EM": 1 if ok else 0,
                    })
    return pd.DataFrame(rows)


SPECIAL_LOADERS = {
    "ifbench": load_ifbench_result,
    "FunctionChat": load_functionchat_result,
    "NESTFul": load_nestful_result,
    "drop": load_drop_result,
    "mbpp": load_mbpp_result,
    "humaneval": load_humaneval_result,
    "livecodebench": load_livecodebench_result,
}


# ── Generic samples loader ──
_BOOL_STR_COLUMNS = {
    "q_eval": {"true": 1, "false": 0},
    "win_score": {"true": 1, "false": 0},
    "is_pass": {"pass": 1, "fail": 0},
    "valid": {"true": 1, "false": 0},
}

# When a filter column exists, keep only one filter, by this priority
_FILTER_PRIORITY = [
    "custom-answer", "strict-match", "none", "get-answer", "flexible-extract", "custom-extract",
]


def rename_and_filter_em_column(df: pd.DataFrame, model_name: str) -> pd.DataFrame:
    """Rename the correctness column to {model}_EM and narrow down to a single filter."""
    em_col = f"{model_name}_EM"
    if "exact_match" in df.columns:
        df = df.rename(columns={"exact_match": em_col})
    elif "acc" in df.columns:
        df = df.rename(columns={"acc": em_col})
    else:
        col = next((c for c in _BOOL_STR_COLUMNS if c in df.columns), None)
        if col is None:
            raise ValueError(f"no correctness column in {model_name} results")
        df[col] = df[col].astype(str).str.lower().str.strip().map(_BOOL_STR_COLUMNS[col])
        df = df.rename(columns={col: em_col})

    if "filter" in df.columns:
        filter_values = set(df["filter"].unique())
        chosen = next((f for f in _FILTER_PRIORITY if f in filter_values), None)
        if chosen is not None:
            df = df[df["filter"] == chosen]

    return df


def load_model_result(cfg, benchmark_name, model):
    """One model's results for one benchmark -> [id, benchmark, category, {model}_EM, ...]."""
    if benchmark_name in IFEVAL_BENCH:
        return load_ifeval_result(cfg, model, benchmark_name)
    if benchmark_name in SPECIAL_LOADERS:
        return SPECIAL_LOADERS[benchmark_name](cfg, model, benchmark_name)

    dirs = find_bench_dirs(cfg, model, benchmark_name)
    if not dirs:
        raise FileNotFoundError(f"folder not found: {model} / {benchmark_name}")

    # Collect jsonl/xlsx; for re-runs of the same task use only the latest
    files = list_sample_files(dirs)

    df_list = []
    for folder_path, file in files:
        file_path = os.path.join(folder_path, file)
        try:
            df = read_sample_dataframe(file_path)
        except Exception as e:
            raise ValueError(f"failed to read {file_path}: {e}") from e

        df["benchmark"] = benchmark_name
        df["category"] = derive_category(cfg, benchmark_name, norm_task_name(file))
        df = rename_and_filter_em_column(df, model)
        df = df.reset_index(drop=True)
        doc_ids = df["doc_id"].tolist() if "doc_id" in df.columns else None
        df["id"] = df["category"].astype(str) + "_" + pd.Series(_question_keys(doc_ids, len(df)))
        df_list.append(df)

    return pd.concat(df_list, ignore_index=True, sort=False)
