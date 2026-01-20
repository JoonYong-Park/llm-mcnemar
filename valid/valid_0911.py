#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
McNemar χ² 검정 스크립트

─ 비교하려는 두 모델의 jsonl 결과 로그를 읽어 들여
  동일 샘플에 대한 정답‧오답 여부를 비교한 뒤
  맥네마(McNemar) 검정을 수행하고 요약 · 집계 리포트를 생성한다.

주요 처리 순서
────────────────────────────────────────
1. 루트 경로(root)에서 벤치마크 jsonl 파일을 탐색
2. 모델 쌍(PAIRS)에 대해 공통 벤치마크만 선별
3. 각 벤치마크에 대해 contingency table(2 × 2) 구성
4. χ² 통계량 · p-value 계산 → 유의성 여부 판정
5. diff<25 (모델 간 오답-교차 개수)인 경우
   → “need_test = 불필요” 로 표시하고 summary 집계에서 제외
6. 전체 결과를
   · pair_sig_mcnemar_*.csv           (자세한 결과)
   · dashboard_mcnemar_*.csv          (대시보드용 요약)
   · summary_report_*.csv             (display 기준 요약)
   · aggregated_summary_report_*.csv  (sub 기준 집계)
   · pair_sig_mcnemar_*.json          (머신 가독성용 JSON)
   로 저장
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
#    (baseline ↔ [sota1, sota2, ...]) 형태로 작성한다.
# ───────────────────────────────────────────────────────────────
PAIRS = {
    # "Llama-3.1-kt-74B-Chat-3.0": [
    #     "GPT4o-1120",
    #     "Llama-3.1-70B-Instruct",
    #     "Llama-3.3-70B-Instruct"
    # ],
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
    """
    • 앞뒤 공백 및 id_/ID_ 접두어 제거
    • 전부 숫자이면 0 채움을 없애고 int → str 변환 (ex. "00042" → "42")
    • 영문/숫자 혼합이면 소문자로 통일
    """
    s = re.sub(r"^(?:id_|ID_)", "", str(raw).strip())
    return str(int(s)) if s.isdigit() else s.lower()

# ───────────────────────────────────────────────────────────────
# 3. 벤치마크 메타데이터
#    (lang, major, sub, display) → summary·집계 리포트에 사용
# ───────────────────────────────────────────────────────────────
BENCHMARK_INFO = {
    # -------- English Benchmarks --------
    "aime2025":      {"lang": "English", "major": "영어 공통능력 지표", "sub": "수학",        "display": "AIME2025"},
    "aqua-rat":      {"lang": "English", "major": "영어 공통능력 지표", "sub": "수학",        "display": "AQUA-RAT"},
    "ifeval":     {"lang": "English", "major": "영어 공통능력 지표", "sub": "영어 지시이행", "display": "IFEval"},
    "winogrande": {"lang": "English", "major": "영어 공통능력 지표", "sub": "추론",        "display": "Winogrande"},
    "gsm8k":      {"lang": "English", "major": "영어 공통능력 지표", "sub": "수학",        "display": "GSM8K"},
    "bbh":        {"lang": "English", "major": "영어 공통능력 지표", "sub": "추론",        "display": "BBH"},
    "gpqa":       {"lang": "English", "major": "영어 공통능력 지표", "sub": "추론",        "display": "GPQA"},
    "musr":       {"lang": "English", "major": "영어 공통능력 지표", "sub": "추론",        "display": "MuSR"},
    "math":       {"lang": "English", "major": "영어 공통능력 지표", "sub": "수학",        "display": "MATH_hard"},
    "mmlu_pro":   {"lang": "English", "major": "영어 공통능력 지표", "sub": "전문지식",    "display": "MMLU PRO"},

    # -------- Korean Benchmarks --------
    "koifeval":   {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 지시이행", "display": "Ko-IFEval"},
    "k_lexicon":  {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해",     "display": "K-Pragmatics"},
    "k_implicature": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해",  "display": "K-Pragmatics"},
    "k_honorifics":  {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해",  "display": "K-Pragmatics"},
    "k_lexicon_hard":    {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "K-Pragmatics-Hard"},
    "k_implicature_hard": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "K-Pragmatics-Hard"},
    "k_honorifics_hard": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "K-Pragmatics-Hard"},
    "kobest_boolq":      {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "KoBest(BoolQ)"},
    "kobest_sentineg":   {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "KoBest(SentiNeg)"},
    "ko_sovereign_language_literature": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "KoSovereign(언어 및 문학 영역)"},
    "ko_comprehensivegen":      {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 생성", "display": "Ko-ComprehensiveGen"},
    "ko_comprehensivegen_hard": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 생성", "display": "Ko-ComprehensiveGen-hard"},
    "ko_winogrande":     {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 추론", "display": "Ko-Winogrande"},
    "kobest_copa":       {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 추론", "display": "KoBest(COPA)"},
    "kobest_hellaswag":  {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 추론", "display": "KoBest(HellaSwag)"},
    "kobest_wic":        {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 추론", "display": "KoBest(Wic)"},
    "k_referential":     {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "K-Referential"},
    "k_referential_hard": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "K-Referential-hard"},
    "ko_sovereign_culture_folklore": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화",
                                      "display": "KoSovereign(문화 및 민속, 사회 영역)"},
    "ko_sovereign_society": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화",
                                      "display": "KoSovereign(문화 및 민속, 사회 영역)"},
    "kmmlu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식", "display": "KMMLU"},
    "ko_sovereign_history": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식",
                                      "display": "KoSovereign(역사, 법, 경제 및 금융, 정치, 교육, 지리 영역)"},
    "ko_sovereign_law": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식",
                                      "display": "KoSovereign(역사, 법, 경제 및 금융, 정치, 교육, 지리 영역)"},
    "ko_sovereign_economics_finance": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식",
                                      "display": "KoSovereign(역사, 법, 경제 및 금융, 정치, 교육, 지리 영역)"},
    "ko_sovereign_politics": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식",
                                      "display": "KoSovereign(역사, 법, 경제 및 금융, 정치, 교육, 지리 영역)"},
    "ko_sovereign_education": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식",
                                      "display": "KoSovereign(역사, 법, 경제 및 금융, 정치, 교육, 지리 영역)"},
    "ko_sovereign_geography": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 전문지식",
                                      "display": "KoSovereign(역사, 법, 경제 및 금융, 정치, 교육, 지리 영역)"},
    "kobalt_700": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "Kobalt-700"},
    "click_functional_csat": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "click_functional_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"}, 
    "click_functional_pse": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "click_grammar_csat": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "click_grammar_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "click_grammar_topik": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "click_textual_csat": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "click_textual_topik": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 이해", "display": "CLIck(언어)"},
    "ko_commongen_v2": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 생성", "display": "Ko-CommonGen_V2"},
    "hrmcr": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 추론", "display": "HRMCR"},
    "click_economy_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_economy_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_geography_csat": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_geography_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_geography_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_history_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_history_khb": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_history_pse": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_law_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_law_psat": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_politics_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_politics_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_popular_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_populary_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_society_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_society_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_tradition_kedu": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "click_tradition_kiip": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "CLIck(문화)"},
    "haerae": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 사회/문화", "display": "HAERAE_Bench1.1"},
    "hrm8k": {"lang": "Korean", "major": "한국어 AI 지표", "sub": "한국어 수학", "display": "HRM8K"},
}

# ───────────────────────────────────────────────────────────────
# 4. 벤치마크 분류 헬퍼
# ───────────────────────────────────────────────────────────────
# def bench_key(p: Path) -> str:
#     """파일명에서 확장자를 제거해 벤치마크 key 반환 (예: ifeval.jsonl → 'ifeval')"""
#     return re.sub(r"\.jsonl?$", "", p.name, flags=re.I)
def bench_key(p: Path) -> str:
    # livecodebench의 경우 파일명이 다르므로 bench_key를 직접 반환하도록 수정
    if 'livecodebench' in p.name.lower():
        return "livecodebench"
    return re.sub(r"\.jsonl?$", "", p.name, flags=re.I)

def bench_category(bench: str) -> str:
    """벤치 이름 → 대분류 키"""
    if bench.startswith("bbh"):                 return "bbh"
    if bench.startswith("gpqa"):                return "gpqa"
    if bench.startswith("gsm8k"):               return "gsm8k"
    if bench.startswith("ifeval"):              return "ifeval"
    if bench.startswith(("k_", "cot_k_")):      return "k_benchmarks"
    if bench.startswith("kmmlu"):               return "kmmlu"
    if bench.startswith("ko_comprehensivegen"): return "ko_comprehensivegen"
    if bench.startswith("ko_sovereign"):        return "ko_sovereign"
    if bench.startswith("ko_winogrande"):       return "ko_winogrande"
    if bench.startswith("kobest"):              return "kobest"
    if bench.startswith("koifeval"):            return "koifeval"
    if bench.startswith("math"):                return "math"
    if bench.startswith("mmlu_pro"):            return "mmlu_pro"
    if bench.startswith("musr"):                return "musr"
    if bench.startswith("winogrande"):          return "winogrande"
    if bench.startswith("aqua-rat"):          return "aqua-rat"
    if bench.startswith("aime2025"):          return "aime2025"
    if bench.startswith("kobalt_700"):          return "kobalt_700"
    if bench.startswith("ko_commongen_v2"):          return "ko_commongen_v2"
    if bench.startswith("hrmcr"):          return "hrmcr"
    if bench.startswith("haerae"):          return "haerae"
    if bench.startswith("hrm8k"):          return "hrm8k"
    if bench.startswith("click"):          return "click"
    return bench.split("_")[0]

# ───────────────────────────────────────────────────────────────
# 5. jsonl 로드 → {sample_id: correct(0/1)} 생성
# ───────────────────────────────────────────────────────────────
ID_KEYS  = ["doc_id", "problem_id", "id", "idx", "qid", "question_id"]
ACC_KEYS = [
    "exact_match", "em", "correct", "is_correct", "acc"
]

def load_em(fp: Path, bench: str) -> Dict[str, int]:
    """
    jsonl 파일에서 (샘플 ID → 정답(1)/오답(0)) dict 반환

    처리 단계
    ───────────────────────────────────────
    1) {"doc": {...}} 형태면 평탄화
    2) BBH strict-match 필터 샘플(oracle 등) 제거
    3) ID 필드 탐색 → _norm_id 로 정규화
    4) 정확도 필드 탐색 → 첫 번째 발견 값을 사용
    """
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
            
            if bench.startswith("bbh") and flat.get("filter") == "strict-match":
                continue

            sid_raw = next((flat.get(k) for k in ID_KEYS if k in flat), None)
            if sid_raw is None:
                continue
            sid = _norm_id(sid_raw)

            acc_raw = next((flat.get(k) for k in ACC_KEYS if k in flat), None)
            if acc_raw is None:
                continue
            acc = int(round(float(acc_raw)))

            out[sid] = acc
    return out

# ───────────────────────────────────────────────────────────────
# 6. McNemar 통계 계산 도우미
# ───────────────────────────────────────────────────────────────
def mcnemar_stats(tbl: List[List[int]]) -> Tuple[float, str]:
    """2×2 contingency table → (p-value, 유의성 문자열)"""
    only_a, only_b = tbl[0][1], tbl[1][0]
    if only_a + only_b == 0:
        return 1.0, "유의하지 않음"
    res = mcnemar(tbl, exact=False, correction=True)
    p = res.pvalue
    return p, ("유의함" if p < 0.05 else "유의하지 않음")

pct = lambda c, n: round(c / n * 100, 2) if n else 0.0

# ───────────────────────────────────────────────────────────────
# 7. summary_report (display 기준) 작성
# ───────────────────────────────────────────────────────────────
def write_combined_summary(base: str, sota: str, summary_data: List[Dict[str, Any]], root: Path):
    """
    summary_data: [{info, n, tbl, need_test}, ...] (display 단위)
    한국어 표를 위, 영어 표를 아래에 두고 두 표 사이에 공백 2줄 삽입
    """
    display_agg = defaultdict(lambda: {
        "n": 0, "tbl": [[0, 0], [0, 0]],
        "info": {}, "need_tests": []
    })

    # 1) display 단위로 합산
    for item in summary_data:
        info, disp = item["info"], item["info"]["display"]
        key = (info["lang"], disp)
        display_agg[key]["n"] += item["n"]
        display_agg[key]["info"] = info
        display_agg[key]["need_tests"].append(item["need_test"])
        tbl = display_agg[key]["tbl"]
        for i in range(2):
            for j in range(2):
                tbl[i][j] += item["tbl"][i][j]

    # 2) 언어별 행 생성
    rows_by_lang = defaultdict(list)
    for (lang, disp), data in display_agg.items():
        n, tbl, info, need_tests = data["n"], data["tbl"], data["info"], data["need_tests"]
        acc_b = pct(tbl[0][0] + tbl[0][1], n)
        acc_s = pct(tbl[0][0] + tbl[1][0], n)
        sig = "검정 제외" if all(nt == "불필요" for nt in need_tests) else mcnemar_stats(tbl)[1]
        rows_by_lang[lang].append((info["sub"], disp, acc_b, acc_s, sig))
    for lang in rows_by_lang:
        rows_by_lang[lang].sort(key=lambda r: (r[0], r[1]))

    # 3) CSV 작성
    out = root / f"summary_report_{base}_vs_{sota}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        first_block = True
        for lang in ["Korean", "English"]:
            if lang not in rows_by_lang:
                continue
            major_hdr = "한국어 AI 지표" if lang == "Korean" else "영어 공통능력 지표"
            header = [major_hdr, "벤치마크", base, sota, "유의성 검정"]
            if not first_block:
                w.writerow([]); w.writerow([])
            first_block = False
            w.writerow(header)
            for sub, disp, acc_b, acc_s, sig in rows_by_lang[lang]:
                w.writerow([sub, disp, acc_b, acc_s, sig])
    print(f"📊 통합 요약 : {out}")

# ───────────────────────────────────────────────────────────────
# 8. aggregated_summary_report (sub 기준) 작성
# ───────────────────────────────────────────────────────────────
# def write_combined_aggregated(base: str, sota: str, summary_data: List[Dict[str, Any]], root: Path):
#     """
#     summary_data: [{info, n, tbl, need_test}, ...] (display → sub mapping 후 합산)
#     한국어 표를 위, 영어 표를 아래에 두고 두 표 사이에 공백 2줄 삽입
#     """
#     sub_agg = defaultdict(lambda: {
#         "n": 0, "tbl": [[0, 0], [0, 0]],
#         "info": None, "need_tests": []
#     })

#     # 1) sub 단위 합산
#     for item in summary_data:
#         info, sub = item["info"], item["info"]["sub"]
#         key = (info["lang"], sub)
#         sub_agg[key]["n"] += item["n"]
#         sub_agg[key]["info"] = info
#         sub_agg[key]["need_tests"].append(item["need_test"])
#         tbl = sub_agg[key]["tbl"]
#         for i in range(2):
#             for j in range(2):
#                 tbl[i][j] += item["tbl"][i][j]

#     # 2) 언어별 행 정리
#     rows_by_lang = defaultdict(list)
#     for (lang, sub), data in sub_agg.items():
#         n, tbl, need_tests = data["n"], data["tbl"], data["need_tests"]
#         acc_b = pct(tbl[0][0] + tbl[0][1], n)
#         acc_s = pct(tbl[0][0] + tbl[1][0], n)
#         sig = "검정 제외" if all(nt == "불필요" for nt in need_tests) else mcnemar_stats(tbl)[1]
#         rows_by_lang[lang].append((sub, acc_b, acc_s, sig))
#     for lang in rows_by_lang:
#         rows_by_lang[lang].sort(key=lambda r: r[0])

#     # 3) CSV 작성
#     out = root / f"aggregated_summary_report_{base}_vs_{sota}.csv"
#     with out.open("w", newline="", encoding="utf-8-sig") as f:
#         w = csv.writer(f)
#         first_block = True
#         for lang in ["Korean", "English"]:
#             if lang not in rows_by_lang:
#                 continue
#             major_hdr = "한국어 AI 지표" if lang == "Korean" else "영어 공통능력 지표"
#             header = [major_hdr, "평가 대상 모델_acc", "SOTA 모델_acc", "유의성 검정"]
#             sub_header = ["", base, sota, ""]
#             if not first_block:
#                 w.writerow([]); w.writerow([])
#             first_block = False
#             w.writerow(header); w.writerow(sub_header)
#             for sub, acc_b, acc_s, sig in rows_by_lang[lang]:
#                 w.writerow([sub, acc_b, acc_s, sig])
#     print(f"📊 통합 집계 : {out}")

# 8. aggregated_summary_report (sub 기준) 작성
# [수정됨] display 단위 가중 평균 → sub 단위 산술 평균의 2단계 집계
def write_combined_aggregated(base: str, sota: str, summary_data: List[Dict[str, Any]], root: Path):
    """
    [수정됨] 1. display 단위로 가중 평균을 계산.
             2. display 평균값들을 sub 단위로 묶어 산술 평균 계산.
             3. 유의성 검정은 전체 가중 평균 기반으로 계산.
    """
    # --- 유의성 검정을 위한 전체 sub 단위 가중 평균 데이터 (기존 방식) ---
    sub_agg_for_sig = defaultdict(lambda: {
        "n": 0, "tbl": [[0, 0], [0, 0]], "need_tests": []
    })
    for item in summary_data:
        info, sub = item["info"], item["info"]["sub"]
        key = (info["lang"], sub)
        sub_agg_for_sig[key]["n"] += item["n"]
        sub_agg_for_sig[key]["need_tests"].append(item["need_test"])
        tbl = sub_agg_for_sig[key]["tbl"]
        for i in range(2):
            for j in range(2):
                tbl[i][j] += item["tbl"][i][j]

    # --- 정확도 표시 값을 위한 2단계 집계 로직 ---
    # 1단계: display 단위로 그룹화 및 가중 평균 계산
    display_agg = defaultdict(lambda: {
        "n": 0, "tbl": [[0, 0], [0, 0]], "info": {}
    })
    for item in summary_data:
        info, disp = item["info"], item["info"]["display"]
        key = (info["lang"], disp)
        display_agg[key]["n"] += item["n"]
        display_agg[key]["info"] = info
        tbl = display_agg[key]["tbl"]
        for i in range(2):
            for j in range(2):
                tbl[i][j] += item["tbl"][i][j]
   
    # 계산된 display별 평균 정확도를 저장할 중간 데이터 구조
    display_accuracies = {}
    for (lang, disp), data in display_agg.items():
        n, tbl, info = data["n"], data["tbl"], data["info"]
        acc_b = pct(tbl[0][0] + tbl[0][1], n)
        acc_s = pct(tbl[0][0] + tbl[1][0], n)
        display_accuracies[(lang, disp)] = {"sub": info["sub"], "acc_b": acc_b, "acc_s": acc_s}

    # 2단계: sub 단위로 display 평균값들을 재그룹화
    sub_groups_for_acc = defaultdict(lambda: {"acc_b_list": [], "acc_s_list": []})
    for (lang, disp), data in display_accuracies.items():
        sub = data["sub"]
        key = (lang, sub)
        sub_groups_for_acc[key]["acc_b_list"].append(data["acc_b"])
        sub_groups_for_acc[key]["acc_s_list"].append(data["acc_s"])

    # --- 최종 결과 취합 및 CSV 작성 ---
    rows_by_lang = defaultdict(list)
    for (lang, sub), data in sub_groups_for_acc.items():
        # 3단계: 최종 산술 평균 계산 (표시될 정확도)
        acc_b_list = data["acc_b_list"]
        acc_s_list = data["acc_s_list"]
        final_acc_b = sum(acc_b_list) / len(acc_b_list) if acc_b_list else 0.0
        final_acc_s = sum(acc_s_list) / len(acc_s_list) if acc_s_list else 0.0

        # 유의성 검정 결과 가져오기 (전체 가중 평균 기반)
        sig_data = sub_agg_for_sig[(lang, sub)]
        sig = "검정 제외" if all(nt == "불필요" for nt in sig_data["need_tests"]) else mcnemar_stats(sig_data["tbl"])[1]
       
        rows_by_lang[lang].append((sub, round(final_acc_b, 2), round(final_acc_s, 2), sig))

    for lang in rows_by_lang:
        rows_by_lang[lang].sort(key=lambda r: r[0])

    # CSV 작성 부분 (기존과 동일)
    out = root / f"aggregated_summary_report_{base}_vs_{sota}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        first_block = True
        for lang in ["Korean", "English"]:
            if lang not in rows_by_lang:
                continue
            major_hdr = "한국어 AI 지표" if lang == "Korean" else "영어 공통능력 지표"
            header = [major_hdr, "평가 대상 모델_acc", "SOTA 모델_acc", "유의성 검정"]
            sub_header = ["", base, sota, ""]
            if not first_block:
                w.writerow([]); w.writerow([])
            first_block = False
            w.writerow(header); w.writerow(sub_header)
            for sub, acc_b, acc_s, sig in rows_by_lang[lang]:
                w.writerow([sub, acc_b, acc_s, sig])
    print(f"📊 통합 집계 (2단계 방식) : {out}")
    
# ───────────────────────────────────────────────────────────────
# 9. 메인 흐름
# ───────────────────────────────────────────────────────────────
def main(root: Path):
    # ----------------------------------------------------------------
    # 1) 루트 경로 아래에서 *.jsonl 탐색 → 모델별 최신 파일 선정
    # ----------------------------------------------------------------
    bench2files: Dict[str, Dict[str, Path]] = {}
    for fp in root.rglob("*.jsonl"):
        if fp.name.startswith('.'):
            continue
        model = fp.relative_to(root).parts[0]
        if model not in ALL_MODELS:
            continue

        bench = bench_key(fp)
        cat   = bench_category(bench)
        if bench not in BENCHMARK_INFO and cat not in BENCHMARK_INFO:
            continue

        m2f = bench2files.setdefault(bench, {})
        if model not in m2f or fp.stat().st_mtime > m2f[model].stat().st_mtime:
            m2f[model] = fp

    # ----------------------------------------------------------------
    # 2) 모델 쌍별로 McNemar 검정 수행
    # ----------------------------------------------------------------
    for base, sota_list in PAIRS.items():
        for sota in sota_list:
            print(f"\n{'='*22}\n📊 비교 시작: {base} ↔ {sota}\n{'='*22}")

            pair_rows, dash_rows, results_json = [], [], {}
            summary_data = []
            handled = False

            for bench, m2f in sorted(bench2files.items()):
                if base not in m2f or sota not in m2f:
                    continue
                handled = True

                em_b = load_em(m2f[base], bench)
                em_s = load_em(m2f[sota], bench)
                common_ids = em_b.keys() & em_s.keys()
                
                # assert len(em_b.keys()) == len(em_s.keys()), f"{m2f[base]}, {m2f[sota]} 모델의 데이터 개수가 불일치합니다. \nbase모델: {len(em_b.keys())}, 비교 모델: {len(em_s.keys())}"
                
                if not common_ids:
                    print(f"— {bench:45} (공통 샘플 없음)")
                    continue

                bc = oa = ob = bw = 0
                for sid in common_ids:
                    a, b = em_b[sid], em_s[sid]
                    if a and b:        bc += 1
                    elif a:            oa += 1
                    elif b:            ob += 1
                    else:              bw += 1
                n = len(common_ids)
                tbl = [[bc, oa], [ob, bw]]
                diff_cnt = oa + ob
                chi2_res = mcnemar(tbl, exact=False, correction=True)
                p_val = chi2_res.pvalue
                chi2  = chi2_res.statistic
                sig   = "유의함" if p_val < 0.05 else "유의하지 않음"
                need_test = "불필요" if diff_cnt < 25 else "필요"
                acc_b = pct(bc + oa, n)
                acc_s = pct(bc + ob, n)
                print(f"✅ {bench:45} N={n:<5} acc={acc_b:>5.2f}↔{acc_s:<5.2f} "
                      f"diff={diff_cnt:<3} p={p_val:.4g} → "
                      f"{sig if need_test=='필요' else '검정 제외'}")

                info_key = bench if bench in BENCHMARK_INFO else bench_category(bench)
                if info_key in BENCHMARK_INFO:
                    summary_data.append({
                        "info": BENCHMARK_INFO[info_key],
                        "n": n,
                        "tbl": tbl,
                        "need_test": need_test
                    })
                pair_rows.append(dict(
                    baseline=base, sota=sota, benchmark=bench, n_total=n,
                    p_value=p_val, chi2_stat=chi2,
                    only_base=oa, only_sota=ob,
                    both_correct=bc, both_wrong=bw,
                    acc_base=acc_b, acc_sota=acc_s,
                    significant=sig if need_test == "필요" else "검정 제외",
                    need_test=need_test
                ))
                dash_rows.append(dict(
                    benchmark=bench, baseline=base, sota=sota,
                    acc_base=acc_b, acc_sota=acc_s,
                    significant=sig if need_test == "필요" else "검정 제외"
                ))
                results_json.setdefault(base, {}).setdefault(sota, {})[bench] = {
                    "n": n, "table": tbl,
                    "only_base": oa, "only_sota": ob,
                    "acc_base": acc_b, "acc_sota": acc_s,
                    "chi2_stat": chi2, "p_value": p_val,
                    "significant": sig if need_test == "필요" else "검정 제외",
                    "need_test": need_test
                }

            if not handled:
                print("— 처리할 공통 벤치마크 파일이 없습니다.")
                continue

            # ----------------------------------------------------------------
            # 3) summary/aggregated CSV 생성
            # ----------------------------------------------------------------
            if summary_data:
                print("-"*40)
                write_combined_summary(base, sota, summary_data, root)
                write_combined_aggregated(base, sota, summary_data, root)
                print("-"*40)

            # ----------------------------------------------------------------
            # 4) pair/dash CSV & JSON 저장
            # ----------------------------------------------------------------
            if pair_rows:
                pair_csv = root / f"pair_sig_mcnemar_{base}_vs_{sota}.csv"
                dash_csv = root / f"dashboard_mcnemar_{base}_vs_{sota}.csv"
                json_out = root / f"pair_sig_mcnemar_{base}_vs_{sota}.json"

                json_out.write_text(json.dumps(results_json, indent=2, ensure_ascii=False), "utf-8")

                fieldnames = [
                    "baseline", "sota", "benchmark", "n_total",
                    "p_value", "chi2_stat",
                    "only_base", "only_sota",
                    "both_correct", "both_wrong",
                    "acc_base", "acc_sota",
                    "significant", "need_test"
                ]

                with pair_csv.open("w", newline="", encoding="utf-8-sig") as f:
                    w = csv.DictWriter(f, fieldnames=fieldnames)
                    w.writeheader()
                    w.writerows(pair_rows)

                with dash_csv.open("w", newline="", encoding="utf-8-sig") as f:
                    w = csv.DictWriter(f, fieldnames=dash_rows[0].keys())
                    w.writeheader()
                    w.writerows(dash_rows)

                print(f"\n🗂 JSON : {json_out}")
                print(f"🗂 Pair : {pair_csv}")
                print(f"🗂 Dash : {dash_csv}")

# ───────────────────────────────────────────────────────────────
# 10. 실행 엔트리포인트
# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    default_root = Path("../4-1차결과_유의성검증").resolve()
    parser = argparse.ArgumentParser(description="McNemar Test Runner")
    parser.add_argument("--root", type=Path, default=default_root,
                        help=f"Root directory containing model logs (default: {default_root})")
    args = parser.parse_args()
    main(args.root.expanduser().resolve())