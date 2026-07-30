import os
import re
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# 법률 4개 모델의 각 벤치마크/문항(jsonl 라인) 수가 모델 간 일치하는지 점검.
#   - 벤치마크 폴더 경로는 4개 모델 모두 정규화돼 동일 (공통지표/…, 법률지표/…)
#   - 파일명 task 는 모델마다 타임스탬프/`legal_` 접두어/run 폴더명이 달라
#     아래 norm_task() 로 정규화해서 매칭한다.
#   - midm 은 일부 벤치마크가 없거나 같은 task 가 여러 번(run) 존재할 수 있다.
# ─────────────────────────────────────────────────────────────

# repo 루트 기준 법률 폴더 (src_legal/ 의 부모가 repo 루트)
BASE_DIR = Path(__file__).resolve().parent.parent / "법률"

# (표시용 짧은 라벨, 실제 폴더명)  — 기준 모델을 맨 앞에.
MODELS = [
    ("gemma-legal", "gemma-4-26B-A4B-Legel"),
    ("gpt-mini",    "gpt-5.4-mini"),
    ("gemma-it",    "gemma-4-26B-A4B-it"),
    ("midm",        "midm-250-pro-march26"),
]

TS_RE = re.compile(r"_2026-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+$")


def count_lines(file_path):
    """jsonl 문항(라인) 수."""
    with open(file_path, "r", encoding="utf-8-sig") as f:
        return sum(1 for _ in f)


def norm_task(filename):
    """sample 파일명 → 모델 간 비교 가능한 task 키.
    samples_ 접두어, 뒤쪽 타임스탬프, 앞쪽 legal_ 접두어를 제거한다."""
    name = os.path.splitext(filename)[0]
    if name.startswith("samples_"):
        name = name[len("samples_"):]
    name = TS_RE.sub("", name)          # 타임스탬프 제거
    if name.startswith("legal_"):       # midm 은 legal_ 접두어가 없는 경우가 있음
        name = name[len("legal_"):]
    return name


def bench_path_of(file_path, model_dir):
    """모델 루트 기준, run 폴더/파일명을 뗀 벤치마크 폴더 경로."""
    rel = os.path.relpath(file_path, model_dir)
    parts = rel.split(os.sep)
    # 파일은 항상 …/<벤치마크>/<run>/samples_*.jsonl 구조 → 뒤 2개(run, 파일) 제거
    return os.sep.join(parts[:-2])


def scan_model(model_dir):
    """key=(bench_path, task) → 문항수 집합(set). 같은 key 에 여러 run 이 있으면 여러 값이 모임."""
    result = defaultdict(set)
    if not model_dir.is_dir():
        return result
    for root, _, files in os.walk(model_dir):
        for fn in files:
            if not fn.endswith(".jsonl") or fn.startswith("._"):
                continue
            fpath = os.path.join(root, fn)
            key = (bench_path_of(fpath, model_dir), norm_task(fn))
            result[key].add(count_lines(fpath))
    return result


# ── 모델별 스캔 ──
scans = {}
for label, folder in MODELS:
    scans[label] = scan_model(BASE_DIR / folder)
    n_tasks = len(scans[label])
    print(f"[스캔] {label:<12} ({folder}) : task {n_tasks}개")

labels = [l for l, _ in MODELS]

# ── 전체 key 합집합 ──
all_keys = set()
for s in scans.values():
    all_keys |= set(s.keys())

mismatch_rows = []      # 존재하는 모델 간 문항수가 다른 경우
coverage_rows = []      # 일부 모델에만 존재하는 경우 (문항수는 일치)
internal_rows = []      # 한 모델 내부에서 run 간 문항수가 다른 경우
ok_count = 0

for key in sorted(all_keys):
    bench, task = key
    per_model = {}          # label -> 대표 문항수 (int) or None
    internal_bad = []       # 내부 불일치 모델
    for label in labels:
        counts = scans[label].get(key)
        if not counts:
            per_model[label] = None
        elif len(counts) == 1:
            per_model[label] = next(iter(counts))
        else:
            per_model[label] = sorted(counts)   # list = 내부 불일치
            internal_bad.append(label)

    present = {l: v for l, v in per_model.items() if v is not None}
    # 내부 불일치가 있으면 별도 보고
    if internal_bad:
        internal_rows.append((bench, task, per_model, internal_bad))
        continue

    present_vals = set(present.values())
    if len(present) == len(labels) and len(present_vals) == 1:
        ok_count += 1                                   # 4개 모델 모두 존재 + 일치
    elif len(present_vals) > 1:
        mismatch_rows.append((bench, task, per_model))  # 값이 서로 다름
    else:
        coverage_rows.append((bench, task, per_model))  # 값은 같은데 일부 모델 없음


def fmt_row(bench, task, per_model):
    cells = "  ".join(
        f"{l}={'-' if per_model[l] is None else per_model[l]}" for l in labels
    )
    return f"  [{bench}] {task}\n      {cells}"


print("\n" + "=" * 70)
print(f"총 task(합집합): {len(all_keys)}개   |   4개 모델 모두 존재+문항수 일치: {ok_count}개")
print("=" * 70)

print(f"\n❌ 문항수 불일치 (존재하는 모델 간 라인수가 다름) : {len(mismatch_rows)}개")
if mismatch_rows:
    for bench, task, pm in mismatch_rows:
        print(fmt_row(bench, task, pm))
else:
    print("  (없음)")

print(f"\n⚠️ 모델 내부 다중 run 문항수 불일치 : {len(internal_rows)}개")
if internal_rows:
    for bench, task, pm, bad in internal_rows:
        print(fmt_row(bench, task, pm) + f"   << 내부불일치: {bad}")
else:
    print("  (없음)")

print(f"\n⚠️ 커버리지 차이 (일부 모델에만 존재, 문항수는 일치) : {len(coverage_rows)}개")
if coverage_rows:
    for bench, task, pm in coverage_rows:
        missing = [l for l in labels if pm[l] is None]
        print(fmt_row(bench, task, pm) + f"   << 없음: {missing}")
else:
    print("  (없음)")

# ── 최종 요약 ──
print("\n" + "=" * 70)
if not mismatch_rows and not internal_rows:
    print("✅ 모든 공통 task 의 문항 수가 4개 모델 간 일치합니다"
          + (" (커버리지 차이만 존재)." if coverage_rows else "."))
else:
    print(f"❗ 문항수 불일치 {len(mismatch_rows)}개, 내부 불일치 {len(internal_rows)}개 발견 — 위 목록 확인 필요")
print("=" * 70)
