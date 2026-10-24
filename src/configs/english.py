# ─────────────────────────────────────────────────────────────
# English benchmarks
#
# Layout: data/english/{model}/{benchmark}/samples_*_<TS>.jsonl
# ─────────────────────────────────────────────────────────────

DATA_DIR = "english"
RESULT_SLUG = "english_benchmarks"

BENCHMARKS = [
    'musr', 'gpqa', 'winogrande', 'bbh', 'mmlu_pro', 'ifeval',
    'gsm8k', 'math_hard', 'aqua_rat', 'aime2025',
    'mbpp', 'livecodebench', 'humaneval',
]

# Benchmarks that get a per-category (sub-task) sheet
CATEGORY_BENCHMARKS = ['bbh', 'gpqa', 'ifeval', 'mmlu_pro', 'musr']

# Domain -> benchmarks/categories (question-weighted; used for domain_mcnemar)
DOMAIN_TO_BENCHMARKS = {
    'English Reasoning': ['musr', 'gpqa', 'winogrande', 'bbh'],
    'English Expert Knowledge': ['mmlu_pro'],
    'English Instruction Following': ['ifeval'],
    'English Math': ['gsm8k', 'math_hard', 'aqua_rat', 'aime2025'],
    'English Coding': ['humaneval', 'mbpp', 'livecodebench'],
}

DOMAINS = list(DOMAIN_TO_BENCHMARKS.keys())

# Domains whose accuracy is the simple mean of sub-item scores instead of question-weighted
DOMAIN_AVERAGE = {
    'English Reasoning': ['musr', 'gpqa', 'winogrande', 'bbh'],
    'English Expert Knowledge': ['mmlu_pro'],
    'English Instruction Following': ['ifeval'],
    'English Math': ['gsm8k', 'math_hard', 'aqua_rat', 'aime2025'],
    'English Coding': ['humaneval', 'mbpp', 'livecodebench'],
}
