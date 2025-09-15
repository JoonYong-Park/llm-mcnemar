### ifeval, koifeval의 경우 들어가는 지표 문제 때문에 

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
McNemar χ² 검정 스크립트 (IFEval/KoIFEval 전용)

─ IFEval, KoIFEval 벤치마크의 jsonl 결과 로그를 읽어 들여
  4가지 평가지표(strict/loose, prompt/inst)의 정확도를 평균내고,
  이를 바탕으로 맥네마(McNemar) 검정을 수행하여 리포트를 생성한다.

주요 처리 순서
────────────────────────────────────────
1. 루트 경로(root)에서 벤치마크 jsonl 파일을 탐색
2. 모델 쌍(PAIRS)에 대해 공통 벤치마크만 선별
3. 대표 지표(prompt_level_strict_acc) 기준으로 contingency table(2 × 2) 구성
4. χ² 통계량 · p-value 계산 → 유의성 여부 판정
5. 4가지 지표의 정확도를 각각 계산한 뒤 평균값을 최종 정확도로 사용
6. 전체 결과를 CSV 및 JSON 파일로 저장
"""

import csv
import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict

from statsmodels.stats.contingency_tables import mcnemar

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

# 베이스·SOTA 전체 집합 (파일 탐색·필터링용)
BASE_MODELS = set(PAIRS.keys())
SOTA_MODELS = {m for lst in PAIRS.values() for m in lst}
ALL_MODELS  = BASE_MODELS | SOTA_MODELS

# ───────────────────────────────────────────────────────────────
# 2. 샘플 ID 정규화 헬퍼
# ───────────────────────────────────────────────────────────────
def _norm_id(raw: Any) -> str:
    s = re.sub(r"^(?:id_|ID_)", "", str(raw).strip())
    return str(int(s)) if s.isdigit() else s.lower()

# ───────────────────────────────────────────────────────────────
# 3. 벤치마크 메타데이터 (IFEval/KoIFEval 전용)
# ───────────────────────────────────────────────────────────────
BENCHMARK_INFO = {
    "ifeval":   {"lang": "English", "major": "영어 공통능력 지표", "sub": "영어 지시이행", "display": "IFEval"},
    "koifeval_new": {"lang": "Korean",  "major": "한국어 AI 지표", "sub": "한국어 지시이행", "display": "Ko-IFEval"},
}

# ───────────────────────────────────────────────────────────────
# 4. 평균을 계산할 정확도(ACC) 지표 목록
#    - 유의성 검정은 이 목록의 첫 번째 지표를 기준으로 수행됩니다.
# ───────────────────────────────────────────────────────────────
TARGET_ACC_FOR_AVG = [
    "prompt_level_strict_acc",
    "inst_level_strict_acc",
    "prompt_level_loose_acc",
    "inst_level_loose_acc"
]

# ───────────────────────────────────────────────────────────────
# 5. jsonl 로드 → {sample_id: correct(0/1)} 생성
#    - 특정 acc_key의 값만 읽어오도록 수정됨
# ───────────────────────────────────────────────────────────────
ID_KEYS  = ["doc_id", "problem_id", "id", "idx", "qid"]

def load_em(fp: Path, bench: str, acc_key: str) -> Dict[str, int]:
    out: Dict[str, int] = {}
    with fp.open("r", encoding="utf-8-sig") as f:
        for ln, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"⚠ JSON 오류 {fp} L{ln}: {e}", file=sys.stderr)
                continue

            flat = {**obj, **obj.get("doc", {})} if isinstance(obj.get("doc"), dict) else obj

            sid_raw = next((flat.get(k) for k in ID_KEYS if k in flat), None)
            if sid_raw is None:
                continue
            sid = _norm_id(sid_raw)

            acc_raw = flat.get(acc_key)
            if acc_raw is None:
                continue
           
            # inst_level_acc는 [true] 형태이므로, 리스트인 경우 첫 요소 사용
            if isinstance(acc_raw, list):
                if not acc_raw: continue
                acc_val = acc_raw[0]
            else:
                acc_val = acc_raw

            acc = int(round(float(acc_val)))
            out[sid] = acc
    return out

# ───────────────────────────────────────────────────────────────
# 6. McNemar 통계 계산 및 기타 헬퍼
# ───────────────────────────────────────────────────────────────
def mcnemar_stats(tbl: List[List[int]]) -> Tuple[float, str]:
    only_a, only_b = tbl[0][1], tbl[1][0]
    if only_a + only_b == 0:
        return 1.0, "유의하지 않음"
    res = mcnemar(tbl, exact=False, correction=True)
    p = res.pvalue
    return p, ("유의함" if p < 0.05 else "유의하지 않음")

pct = lambda c, n: round(c / n * 100, 2) if n else 0.0

# 파일명에서 벤치마크 key 반환 (ifeval.jsonl → 'ifeval')
bench_key = lambda p: re.sub(r"\.jsonl?$", "", p.name, flags=re.I)

# ───────────────────────────────────────────────────────────────
# 7. 메인 흐름
# ───────────────────────────────────────────────────────────────
def main(root: Path):
    # 1) 루트 경로 아래에서 *.jsonl 탐색
    bench2files: Dict[str, Dict[str, Path]] = {}
    for fp in root.rglob("*.jsonl"):
        if fp.name.startswith('.'):
            continue
        model = fp.relative_to(root).parts[0]
        if model not in ALL_MODELS:
            continue
       
        bench = bench_key(fp)
        if bench not in BENCHMARK_INFO:
            continue

        m2f = bench2files.setdefault(bench, {})
        if model not in m2f or fp.stat().st_mtime > m2f[model].stat().st_mtime:
            m2f[model] = fp

    # 2) 모델 쌍별로 McNemar 검정 및 평균 정확도 계산 수행
    for base, sota_list in PAIRS.items():
        for sota in sota_list:
            print(f"\n{'='*22}\n📊 비교 시작: {base} ↔ {sota}\n{'='*22}")

            all_results = []
            handled = False

            for bench, m2f in sorted(bench2files.items()):
                if base not in m2f or sota not in m2f:
                    continue
                handled = True

                # --- 핵심 수정 로직 시작 ---

                # 2-1. 유의성 검정은 대표 지표(목록의 첫 번째)로 수행
                primary_metric = TARGET_ACC_FOR_AVG[0]
                em_b_primary = load_em(m2f[base], bench, primary_metric)
                em_s_primary = load_em(m2f[sota], bench, primary_metric)
               
                common_ids = em_b_primary.keys() & em_s_primary.keys()
                if not common_ids:
                    print(f"— {bench:45} (공통 샘플 없음)")
                    continue

                bc = oa = ob = bw = 0
                for sid in common_ids:
                    a, b = em_b_primary[sid], em_s_primary[sid]
                    if a and b:   bc += 1
                    elif a:       oa += 1
                    elif b:       ob += 1
                    else:         bw += 1
               
                n = len(common_ids)
                tbl = [[bc, oa], [ob, bw]]
                diff_cnt = oa + ob
               
                # 2-2. 리포트에 기록할 최종 acc는 4개 지표의 평균으로 계산
                base_acc_scores = []
                sota_acc_scores = []

                for metric in TARGET_ACC_FOR_AVG:
                    em_b = load_em(m2f[base], bench, metric)
                    em_s = load_em(m2f[sota], bench, metric)
                   
                    metric_common_ids = em_b.keys() & em_s.keys()
                    if not metric_common_ids: continue

                    b_correct = sum(em_b[sid] for sid in metric_common_ids)
                    s_correct = sum(em_s[sid] for sid in metric_common_ids)
                   
                    base_acc_scores.append(pct(b_correct, len(metric_common_ids)))
                    sota_acc_scores.append(pct(s_correct, len(metric_common_ids)))

                # 평균 계산
                acc_b = sum(base_acc_scores) / len(base_acc_scores) if base_acc_scores else 0.0
                acc_s = sum(sota_acc_scores) / len(sota_acc_scores) if sota_acc_scores else 0.0

                # 2-3. 유의성 검정 및 결과 출력
                chi2_res = mcnemar(tbl, exact=False, correction=True)
                p_val, sig_text = mcnemar_stats(tbl)
                chi2  = chi2_res.statistic
                need_test = "불필요" if diff_cnt < 25 else "필요"
                final_sig = sig_text if need_test == '필요' else '검정 제외'
               
                print(f"✅ {bench:45} N={n:<5} avg_acc={acc_b:>5.2f}↔{acc_s:<5.2f} "
                      f"diff={diff_cnt:<3} p={p_val:.4g} → {final_sig}")

                # --- 핵심 수정 로직 종료 ---

                all_results.append(dict(
                    baseline=base, sota=sota, benchmark=bench, n_total=n,
                    p_value=p_val, chi2_stat=chi2,
                    only_base=oa, only_sota=ob,
                    both_correct=bc, both_wrong=bw,
                    acc_base=acc_b, acc_sota=acc_s, # 평균 정확도 사용
                    significant=final_sig,
                    need_test=need_test
                ))

            if not handled:
                print("— 처리할 공통 벤치마크 파일이 없습니다.")
                continue

            # 3) 결과 파일 저장
            if all_results:
                pair_csv = root / f"ifeval_pair_sig_mcnemar_{base}_vs_{sota}.csv"
                with pair_csv.open("w", newline="", encoding="utf-8-sig") as f:
                    w = csv.DictWriter(f, fieldnames=all_results[0].keys())
                    w.writeheader()
                    w.writerows(all_results)
                print(f"\n🗂️ 상세 결과 저장: {pair_csv}")


# ───────────────────────────────────────────────────────────────
# 8. 실행 엔트리포인트
# ───────────────────────────────────────────────────────────────    
if __name__ == "__main__":
    default_root = Path("../4-1차결과_유의성검증").resolve()
    parser = argparse.ArgumentParser(description="McNemar Test Runner")
    parser.add_argument("--root", type=Path, default=default_root,
                        help=f"Root directory containing model logs (default: {default_root})")
    args = parser.parse_args()
    main(args.root.expanduser().resolve())
