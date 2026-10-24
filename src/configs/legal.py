# ─────────────────────────────────────────────────────────────
# Legal domain
#
# Layout: data/legal/{model}/{common|legal}/{folder}/{run}/samples_*_<TS>.jsonl
# BENCH_FOLDERS locates the folders; category names come from the file names
# (with prefixes such as legal_cot_ removed).
# The folder names in BENCH_FOLDERS are the task names used at evaluation time; adjust them to your setup.
# ─────────────────────────────────────────────────────────────

DATA_DIR = "legal"
RESULT_SLUG = "legal_benchmarks"

# Benchmark name -> actual folder name (under data/legal/{model}/**/)
BENCH_FOLDERS = {
    # Legal benchmarks
    'kbl_bar_exam_em':     'kbl_bar_exam_em',
    'kbl_knowledge_em':    'kbl_knowledge_em',
    'kbl_reasoning_em':    'kbl_reasoning_em',
    'kolbench_qa':         'kolbench_qa',
    'kolbench_reason':     'kolbench_reason',
    'kolbench_dq':         'kolbench_dq',
    'kmmlu':               'legal_cot_kmmlu',
    'ko_sovereign_law':    'legal_cot_ko_sovereign_law',
    'kmmlu_pro':           'legal_kmmlu-pro',
    # Common Korean benchmarks
    'koifeval':            'legal_koifeval_new',
    'gsm8k':               'legal_cot_gsm8k_zeroshot',
    'ko_comprehensivegen': 'legal_cot_ko_comprehensivegen_golden',
    'kobalt_700':          'legal_kobalt_700',
    'k_pragmatics':        'legal_pragmatics',
    'ko_winogrande':       'legal_cot_ko-winogrande_zeroshot',
    'ko_sovereign':        'legal_cot_ko_sovereign_etc',
}

BENCHMARKS = list(BENCH_FOLDERS.keys())

# Single-file benchmarks: category = benchmark name (others take the category from the file name)
SINGLE_FILE_BENCH = {
    'kolbench_qa', 'kolbench_reason', 'kolbench_dq',
    'ko_sovereign_law', 'kmmlu_pro', 'gsm8k',
    'ko_comprehensivegen', 'kobalt_700', 'ko_winogrande',
}

# kbl_bar_exam_em is shown as kbl_bar_exam in the report
BENCHMARK_LABELS = {'kbl_bar_exam_em': 'kbl_bar_exam'}

# Extra aggregates: kbl_bar_exam per field + kolbench combined (qa + reason + dq)
KBL_BAR_EXAM_DOMAINS = ['civil', 'criminal', 'public', 'responsibility']
EXTRA_GROUPS = {
    **{
        f'kbl_bar_exam_{d}': {'benchmarks': ['kbl_bar_exam_em'], 'category_contains': f'_{d}_'}
        for d in KBL_BAR_EXAM_DOMAINS
    },
    'kolbench': {'benchmarks': ['kolbench_qa', 'kolbench_reason', 'kolbench_dq']},
}

# Benchmarks that get a per-category sheet = benchmarks with 2+ sub-tasks
CATEGORY_BENCHMARKS = [
    'kbl_bar_exam_em',    # 56 (civil/criminal/public/responsibility x year)
    'kbl_knowledge_em',   # 7
    'kbl_reasoning_em',   # 4
    'kmmlu',              # 2 (law / criminal_law)
    'ko_sovereign',       # 8 (all subjects except law)
    'k_pragmatics',       # 3 (honorifics / implicature / lexicon)
    'koifeval',           # 4 (plsa / ilsa / plla / illa)
]

# ─────────────────────────────────────────────────────────────
# Domain -> benchmarks/categories (question-weighted)
#   comments: source benchmark (question count)
# ─────────────────────────────────────────────────────────────
DOMAIN_TO_BENCHMARKS = {
    # ── Legal ──
    # ko-sovereign law (250), KoLBench_QA (1,263), kmmlu law/criminal law (1,179),
    # kmmlu-pro law (696), KBL legal knowledge (510)
    'Legal Knowledge QA (General)': ['ko_sovereign_law', 'kolbench_qa', 'kmmlu_law', 'kmmlu_criminal_law',
                                     'kmmlu_pro', 'kbl_knowledge_em'],
    # KoLBench_Reasoning (187), KBL legal reasoning (288)
    'Legal Reasoning': ['kolbench_reason', 'kbl_reasoning_em'],
    # KoLBench_DQ (365)
    'Legal Document QA': ['kolbench_dq'],
    # KBL_BarExam (2,658)
    'Legal Knowledge QA (Bar Exam)': ['kbl_bar_exam_em'],
    # ── Common Korean ──
    # KoIFEval (506)
    'Korean Instruction Following': ['koifeval'],
    # gsm8k (1,319)
    'Korean Math': ['gsm8k'],
    # Ko-ComprehensiveGen_golden (1,360)
    'Korean Generation': ['ko_comprehensivegen'],
    # KoBALT-700 (700), K-pragmatics (1,500)
    'Korean Understanding': ['kobalt_700', 'k_pragmatics'],
    # Ko-winogrande (1,638)
    'Korean Reasoning': ['ko_winogrande'],
    # Ko-sovereign, all subjects except law (1,750)
    'Korean Expert Knowledge': ['ko_sovereign_culture_folklore', 'ko_sovereign_economics_finance',
                                'ko_sovereign_education', 'ko_sovereign_geography', 'ko_sovereign_history',
                                'ko_sovereign_language_literature', 'ko_sovereign_politics',
                                'ko_sovereign_society'],
}

DOMAINS = list(DOMAIN_TO_BENCHMARKS.keys())
