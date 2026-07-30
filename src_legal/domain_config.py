# ─────────────────────────────────────────────────────────────
# 법률 유의성 검증 설정 (지표목록.csv 기반)
#
# 폴더 구조(정규화됨): 법률/{model}/{공통지표|법률지표}/{benchmark}/{run}/samples_*_<TS>.jsonl
# mcnemar.py 는 LAW_BENCH_FOLDERS 로 실제 폴더를 찾고, LAW_CATEGORY 규칙으로 카테고리명을 만든다.
# ─────────────────────────────────────────────────────────────

# clean 벤치마크명  ->  실제 폴더명 (법률/{model}/**/ 아래)
LAW_BENCH_FOLDERS = {
    # 법률지표
    'kbl_bar_exam_em':     'kbl_bar_exam_em',
    'kbl_knowledge_em':    'kbl_knowledge_em',
    'kbl_reasoning_em':    'kbl_reasoning_em',
    'kolbench_qa':         'kolbench_qa',
    'kolbench_reason':     'kolbench_reason',
    'kolbench_dq':         'kolbench_dq',
    'kmmlu':               'legal_cot_kmmlu',
    'ko_sovereign_law':    'legal_cot_ko_sovereign_law',
    'kmmlu_pro':           'legal_kmmlu-pro',
    # 공통지표
    'koifeval':            'legal_koifeval_new',
    'gsm8k':               'legal_cot_gsm8k_zeroshot',
    'ko_comprehensivegen': 'legal_cot_ko_comprehensivegen_golden',
    'kobalt_700':          'legal_kobalt_700',
    'k_pragmatics':        'legal_pragmatics',
    'ko_winogrande':       'legal_cot_ko-winogrande_zeroshot',
    'ko_sovereign':        'legal_cot_ko_sovereign_etc',
}

# 파일 1개짜리 벤치마크: category = 벤치마크명 (아래 이외는 파일명 기반 카테고리)
SINGLE_FILE_BENCH = {
    'kolbench_qa', 'kolbench_reason', 'kolbench_dq',
    'ko_sovereign_law', 'kmmlu_pro', 'gsm8k',
    'ko_comprehensivegen', 'kobalt_700', 'ko_winogrande',
}

# ifeval 형식(prompt_level_*_acc) 로더를 써야 하는 벤치마크
IFEVAL_BENCH = {'koifeval'}

LAW_BENCHMARKS = list(LAW_BENCH_FOLDERS.keys())

# kbl_bar_exam_em → benchmark_mcnemar / 정답률 시트에 노출할 집계 키
KBL_BAR_EXAM_BENCHMARK = 'kbl_bar_exam_em'
KBL_BAR_EXAM_LABEL = 'kbl_bar_exam'
KBL_BAR_EXAM_DOMAINS = ['civil', 'criminal', 'public', 'responsibility']

# kolbench_qa / reason / dq → 개별 + 합산(kolbench) 유의성 검증
KOLBENCH_BENCHMARKS = ['kolbench_qa', 'kolbench_reason', 'kolbench_dq']
KOLBENCH_LABEL = 'kolbench'

# 카테고리(서브테스크)별 유의성 시트를 만들 벤치마크 = 서브테스크가 2개 이상인 벤치마크
CATEGORY_BENCHMARKS = [
    'kbl_bar_exam_em',    # 56개 (civil/criminal/public/responsibility × 연도)
    'kbl_knowledge_em',   # 7개
    'kbl_reasoning_em',   # 4개
    'kmmlu',              # 2개 (law / criminal_law)
    'ko_sovereign',       # 8개 (문학/사회/역사/법 제외 전문지식 등)
    'k_pragmatics',       # 3개 (honorifics / implicature / lexicon)
    'koifeval',           # 4개 (plsa / ilsa / plla / illa)
]

# ─────────────────────────────────────────────────────────────
# 지표(도메인) → 벤치마크/카테고리  (문제 수 기반 가중평균)
#   지표목록.csv 의 평가요소 그룹과 1:1 대응 (CSV 미포함 지표는 없음)
# ─────────────────────────────────────────────────────────────
DOMAIN_TO_BENCHMARKS = {
    # ── 법률지표 ──
    '법률_지식QA(일반QA)':   ['ko_sovereign_law', 'kolbench_qa', 'kmmlu_law', 'kmmlu_criminal_law', 'kmmlu_pro', 'kbl_knowledge_em'],
    '법률_추론':     ['kolbench_reason', 'kbl_reasoning_em'],
    '법률_문서_해석(문서QA)': ['kolbench_dq'],
    '법률_지식QA':  ['kbl_bar_exam_em'],
    # ── 공통지표 ──
    '한국어_지시이행도':    ['koifeval'],
    '한국어_수학':          ['gsm8k'],
    '한국어_생성':    ['ko_comprehensivegen'],
    '한국어_이해':    ['kobalt_700', 'k_pragmatics'],
    '한국어_추론':    ['ko_winogrande'],
    '한국_전문지식':  ['ko_sovereign_culture_folklore', 'ko_sovereign_economics_finance',
                     'ko_sovereign_education', 'ko_sovereign_geography', 'ko_sovereign_history',
                     'ko_sovereign_language_literature', 'ko_sovereign_politics', 'ko_sovereign_society'],
}

LAW_DOMAIN = list(DOMAIN_TO_BENCHMARKS.keys())

# 단순 평균 방식 지표 (여기선 사용 안 함 → 전부 가중평균)
DOMAIN_AVERAGE = {}
