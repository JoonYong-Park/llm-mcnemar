### code 영역은 livecodebench 때문에 별도로 진행함

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
집계 기능이 포함된 통합 유의성 검정 스크립트 (McNemar)

- HumanEval, MBPP는 McNemar, LiveCodeBench는 검정 결과를 'Coding_Overall'로 집계합니다.
- 모든 개별 및 집계 결과를 단일 CSV 파일로 저장합니다.
"""

import csv
import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import proportions_ztest
import numpy as np

# ───────────────────────────────────────────────────────────────
# 1. 비교 대상 모델 쌍 정의
# ───────────────────────────────────────────────────────────────
PAIRS = {
    "Midm-pro-v2.4": [
        "A.X-3.1",
        "EXAONE-4.0",
        "Solar-pro2",
        "Qwen-3-32B",
    ],
}
ALL_MODELS = set(PAIRS.keys()) | {m for lst in PAIRS.values() for m in lst}

# ───────────────────────────────────────────────────────────────
# 2. 분석할 벤치마크 및 검정 방식 정의
# ───────────────────────────────────────────────────────────────
BENCHMARKS_TO_TEST = {
    "humaneval": {
        "test_type": "mcnemar",
        "path": "./(new)humaneval/humaneval_instruct.jsonl"
    },
    "mbpp": {
        "test_type": "mcnemar",
        "path": "./(new)mbpp/mbpp_zeroshot.jsonl"
    },
    "livecodebench": {
        "test_type": "mcnemar",
        "path": "./(new)livecodebench/livecodebench_Scenario.codegeneration_eval_all.json"
    }
}

# ───────────────────────────────────────────────────────────────
# 3. 집계 그룹 정의 (McNemar 검정 대상만 가능)
# ───────────────────────────────────────────────────────────────
AGGREGATION_GROUPS = {
    "Coding_Overall (HE+MBPP)": ["humaneval", "mbpp"],
    "Coding_All_3": ["humaneval", "mbpp", "livecodebench"]
}

# ===============================================================
# 데이터 로더 (이전과 동일)
# ===============================================================
ID_KEYS = ["doc_id", "problem_id", "id", "idx", "qid", "task_id"]
ACC_KEYS = ["exact_match", "em", "correct", "is_correct", "pass", "passed", "pass_at_1", "pass_at_k"]

def _norm_id(raw: Any) -> str:
    s = re.sub(r"^(?:id_|ID_)", "", str(raw).strip())
    return str(int(s)) if s.isdigit() else s.lower()

def load_em(fp: Path) -> Dict[str, int]:
    out: Dict[str, int] = {}

    if fp.suffix == '.jsonl':
        with fp.open("r", encoding="utf-8-sig") as f:
            lines = [json.loads(line) for line in f if line.strip()]
    elif fp.suffix == '.json':
        with fp.open("r", encoding="utf-8-sig") as f:
            lines = json.load(f)
    else:
        print(f"❌ 지원되지 않는 형식: {fp}")
        return out

    for ln, obj in enumerate(lines, 1):
        try:
            flat = {**obj, **obj.get("doc", {})} if isinstance(obj.get("doc"), dict) else obj
            sid_raw = next((flat.get(k) for k in ID_KEYS if k in flat), None)
            if sid_raw is None:
                sid_raw = flat.get("question_id") or flat.get("id") or ln  # fallback

            sid = _norm_id(sid_raw)
            acc_raw = next((flat.get(k) for k in ACC_KEYS if k in flat), None)

            if acc_raw is None:
                acc_list = flat.get("graded_list")
                if isinstance(acc_list, list) and len(acc_list) > 0:
                    acc_raw = int(acc_list[0])
                else:
                    continue

            acc = int(round(float(acc_raw)))
            out[sid] = acc
        except Exception as e:
            print(f"⚠️  데이터 파싱 오류 ({fp} L{ln}): {e}")
            continue

    return out

def load_pass_list(fp: Path) -> List[int]:
    try:
        with fp.open('r', encoding='utf-8') as f: data = json.load(f)
        if isinstance(data, list) and data and isinstance(data[0], dict) and "graded_list" in data[0]:
            return [int(s["graded_list"][0]) for s in data if "graded_list" in s and s["graded_list"]]
        print(f"❌ Z-test 데이터 구조 오류: {fp} 파일의 형식을 인식할 수 없습니다.", file=sys.stderr)
        return None
    except FileNotFoundError: return None
    except (KeyError, TypeError, IndexError, json.JSONDecodeError) as e:
        print(f"❌ Z-test 데이터 처리 오류: {fp}. (오류: {e})", file=sys.stderr)
        return None

# ===============================================================
# 유의성 검정 수행 함수 (반환값에 원시 데이터 추가)
# ===============================================================
# ===============================================================
# 유의성 검정 수행 함수 (반환값에 원시 데이터 추가)
# ===============================================================
def perform_mcnemar_test(base_path: Path, sota_path: Path):
    em_b = load_em(base_path)
    em_s = load_em(sota_path)
    if not em_b or not em_s: return None
    common_ids = em_b.keys() & em_s.keys()
    if not common_ids: return None
   
    n = len(common_ids)
    bc = sum(1 for sid in common_ids if em_b[sid] and em_s[sid])
    oa = sum(1 for sid in common_ids if em_b[sid] and not em_s[sid])
    ob = sum(1 for sid in common_ids if not em_b[sid] and em_s[sid])
   
    # --- [수정] need_test 조건 추가 ---
    diff_cnt = oa + ob
    need_test = "필요" if diff_cnt >= 25 else "불필요"
    # ---------------------------------

    tbl = [[bc, oa], [ob, 0]]
    res = mcnemar(tbl, exact=False, correction=True)
    pval = res.pvalue
   
    # --- [수정] 유의성 결과에 need_test 조건 반영 ---
    significant_str = "Yes" if pval < 0.05 else "No"

    return {
        "stats": {
            "Baseline_Accuracy": (bc + oa) / n if n > 0 else 0,
            "Competitor_Accuracy": (bc + ob) / n if n > 0 else 0,
            "Baseline_Score": f"{bc + oa}/{n}",
            "Competitor_Score": f"{bc + ob}/{n}",
            "P_Value": pval,
            "Statistic": f"chi2={res.statistic:.4f}",
            "Significant": significant_str if need_test == "필요" else "검정 제외",
            "Need_Test": need_test # CSV 출력을 위해 필드 추가
        },
        "raw_counts": {"n": n, "bc": bc, "oa": oa, "ob": ob} # 집계를 위한 원시 데이터
    }

def perform_z_test(base_path: Path, sota_path: Path):
    base_passes = load_pass_list(base_path)
    sota_passes = load_pass_list(sota_path)
    if base_passes is None or sota_passes is None: return None
    nobs = np.array([len(base_passes), len(sota_passes)])
    if nobs[0] == 0 or nobs[1] == 0: return None
    counts = np.array([int(np.sum(base_passes)), int(np.sum(sota_passes))])
    stat, pval = proportions_ztest(counts, nobs, alternative='two-sided')
    return {
        "stats": {
            "Baseline_Accuracy": counts[0] / nobs[0],
            "Competitor_Accuracy": counts[1] / nobs[1],
            "Baseline_Score": f"{counts[0]}/{nobs[0]}",
            "Competitor_Score": f"{counts[1]}/{nobs[1]}",
            "P_Value": pval,
            "Statistic": f"z={stat:.4f}",
            "Significant": "Yes" if pval < 0.05 else "No"
        }
    }

# ===============================================================
# 메인 실행 블록 (집계 로직 추가)
# ===============================================================
def main(root: Path):
    individual_results = []
    # ───────────────────────────────────────────────────────────────
    # 📊 모델별 평균 정확도 출력
    # ───────────────────────────────────────────────────────────────
    print("\n--- 📊 모델별 평균 정확도 (%): ---")

    accuracy_table = defaultdict(dict)
    for bench, config in BENCHMARKS_TO_TEST.items():
        for model in ALL_MODELS:
            file_path = root / model / config['path']
            if not file_path.exists():
                continue

            acc_list = []
            if config["test_type"] == "mcnemar":
                acc_map = load_em(file_path)
                if acc_map:
                    acc_list = list(acc_map.values())
            elif config["test_type"] == "z-test":
                acc_list = load_pass_list(file_path)
           
            if not acc_list:
                acc_map = load_em(file_path)
                if acc_map:
                    acc_list = list(acc_map.values())

            if acc_list:
                acc = 100 * sum(acc_list) / len(acc_list)
                accuracy_table[model][bench] = acc

    models_sorted = sorted(ALL_MODELS)
    benchmarks_sorted = list(BENCHMARKS_TO_TEST.keys())
   
    # --- [수정] 평균 계산 로직 및 출력 테이블 수정 ---
    model_averages = {}
    benchmarks_for_avg = ['humaneval', 'mbpp', 'livecodebench']
    for model, scores in accuracy_table.items():
        if all(bench in scores for bench in benchmarks_for_avg):
            avg_score = sum(scores[bench] for bench in benchmarks_for_avg) / len(benchmarks_for_avg)
            model_averages[model] = avg_score

    header = ["Model"] + [f"{b}" for b in benchmarks_sorted] + ["Avg (HE+MBPP+LCB)"]
    print(" | ".join(f"{h:<20}" for h in header))
    print("-" * (23 * len(header)))

    for model in models_sorted:
        row = [f"{model:<20}"]
        for bench in benchmarks_sorted:
            acc = accuracy_table.get(model, {}).get(bench)
            row.append(f"{acc:6.2f}%" if acc is not None else "    -   ")
       
        avg = model_averages.get(model)
        row.append(f"{avg:6.2f}%" if avg is not None else "    -   ")
        print(" | ".join(row))
    # ----------------------------------------------------

    raw_counts_cache = {}

    print("\n--- 통합 유의성 검정 시작 (개별 분석) ---")
    for bench, config in BENCHMARKS_TO_TEST.items():
        print(f"\n--- 벤치마크: {bench} (방식: {config['test_type']}) ---")
        for base, competitors in PAIRS.items():
            for sota in competitors:
                pair_key = (base, sota)
                print(f"🔬 비교 중: {pair_key[0]} vs {pair_key[1]}")
                base_path, sota_path = root / base / config['path'], root / sota / config['path']

                if not base_path.exists() or not sota_path.exists():
                    print(f"  ❌ 파일 없음 (하나 이상): {base_path.name}")
                    continue

                result = None
                if config['test_type'] == 'mcnemar':
                    result = perform_mcnemar_test(base_path, sota_path)
                    if result:
                        raw_counts_cache[(pair_key, bench)] = result["raw_counts"]
                elif config['test_type'] == 'z-test':
                    result = perform_z_test(base_path, sota_path)
               
                if result:
                    full_result = {"Baseline": base, "Competitor": sota, "Benchmark": bench, "Test_Method": config['test_type'], **result["stats"]}
                    individual_results.append(full_result)
                    print(f"  - P-값: {full_result['P_Value']:.4f} ({full_result['Significant']})")
   
    all_results = individual_results.copy()
   
    print("\n--- McNemar 집계 그룹 분석 ---")
    for group_name, members in AGGREGATION_GROUPS.items():
        print(f"\n--- 집계 그룹: {group_name} ---")
        for base, competitors in PAIRS.items():
            for sota in competitors:
                pair_key = (base, sota)
                print(f"🔬 집계 중: {pair_key[0]} vs {pair_key[1]}")
               
                total_n, total_bc, total_oa, total_ob = 0, 0, 0, 0
                for bench in members:
                    counts = raw_counts_cache.get((pair_key, bench))
                    if counts:
                        total_n += counts["n"]
                        total_bc += counts["bc"]
                        total_oa += counts["oa"]
                        total_ob += counts["ob"]
               
                if total_n == 0:
                    print("  - 집계할 데이터 없음")
                    continue
               
                # --- [수정] 집계 로직에 need_test 조건 추가 ---
                total_diff_cnt = total_oa + total_ob
                need_test_agg = "필요" if total_diff_cnt >= 25 else "불필요"
               
                tbl = [[total_bc, total_oa], [total_ob, 0]]
                res = mcnemar(tbl, exact=False, correction=True)
                pval = res.pvalue

                significant_str_agg = "유의함" if pval < 0.05 else "유의하지 않음"

                agg_result = {
                    "Baseline": base, "Competitor": sota, "Benchmark": group_name, "Test_Method": "mcnemar (aggregated)",
                    "Baseline_Accuracy": (total_bc + total_oa) / total_n,
                    "Competitor_Accuracy": (total_bc + total_ob) / total_n,
                    "Baseline_Score": f"{total_bc + total_oa}/{total_n}",
                    "Competitor_Score": f"{total_bc + total_ob}/{total_n}",
                    "P_Value": pval,
                    "Statistic": f"chi2={res.statistic:.4f}",
                    "Significant": significant_str_agg if need_test_agg == "필요" else "검정 제외",
                    "Need_Test": need_test_agg
                }
                all_results.append(agg_result)
                print(f"  - P-값: {agg_result['P_Value']:.4f} ({agg_result['Significant']})")
                # ----------------------------------------------

    if not all_results:
        print("\n--- 처리된 결과가 없어 CSV 파일을 생성하지 않습니다. ---")
        return

    output_filename = "code_combined_results.csv"
    try:
        for res in all_results:
            res['P_Value'] = f"{res['P_Value']:.4f}"
            res['Baseline_Accuracy'] = f"{res['Baseline_Accuracy']:.4f}"
            res['Competitor_Accuracy'] = f"{res['Competitor_Accuracy']:.4f}"
       
        all_results.sort(key=lambda x: (x['Baseline'], x['Competitor'], x['Benchmark']))

        with open(output_filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)
        print(f"\n--- ✅ 모든 결과가 '{output_filename}' 파일에 저장되었습니다. ---")
    except (IOError, IndexError) as e:
        print(f"\n--- ❌ 파일 저장 중 오류 발생: {e} ---")

if __name__ == "__main__":
    default_root = Path("./").resolve()
    parser = argparse.ArgumentParser(description="Aggregated Significance Test Runner")
    parser.add_argument("--root", type=Path, default=default_root, help=f"Root directory (default: {default_root})")
    args = parser.parse_args()
    main(args.root.expanduser().resolve())