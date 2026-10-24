# ─────────────────────────────────────────────────────────────
# Example config (for the synthetic data in data/example)
#
#   python src/mcnemar.py --config example -a model-a -b model-b
#
# What the example data covers:
#   kmmlu      folder name (cot_kmmlu) differs from the benchmark name -> BENCH_FOLDERS; 3 categories
#   gsm8k      strict-match and flexible-extract filters mixed -> only strict-match is used
#   hellaswag  model-b has a re-run -> only the latest timestamp is used
#   ko_ifeval  ifeval format -> expanded into plsa / ilsa / plla / illa categories
#   winogrande the two models have different question counts -> [SKIP]
# ─────────────────────────────────────────────────────────────

DATA_DIR = "example"
RESULT_SLUG = "example"

BENCHMARKS = ['kmmlu', 'gsm8k', 'hellaswag', 'ko_ifeval', 'winogrande']

BENCH_FOLDERS = {'kmmlu': 'cot_kmmlu'}

# Benchmarks that get a per-category (sub-task) sheet
CATEGORY_BENCHMARKS = ['kmmlu', 'ko_ifeval']

# Extra aggregate rows: several benchmarks combined / only categories containing a token
EXTRA_GROUPS = {
    'gsm8k+hellaswag': {'benchmarks': ['gsm8k', 'hellaswag']},
    'kmmlu_math_only': {'benchmarks': ['kmmlu'], 'category_contains': '_math'},
}

# Domain -> benchmarks or categories (question-weighted)
DOMAIN_TO_BENCHMARKS = {
    'Expert Knowledge': ['kmmlu'],
    'Legal Knowledge': ['kmmlu_law'],
    'Math': ['gsm8k', 'kmmlu_math'],
    'Commonsense Reasoning': ['hellaswag', 'winogrande'],
    'Instruction Following': ['ko_ifeval'],
}

DOMAINS = list(DOMAIN_TO_BENCHMARKS.keys())

# Instruction following = mean of the ifeval benchmark scores (not question-weighted)
DOMAIN_AVERAGE = {
    'Instruction Following': ['ko_ifeval'],
}
