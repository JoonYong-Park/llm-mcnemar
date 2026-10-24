# McNemar's test for LLMs

Run McNemar's test on two LLMs' benchmark results, **paired question by question**, and get an Excel report
that answers "is the score difference between model A and model B statistically significant?" at the
benchmark, category and domain level.

Comparing accuracies alone cannot tell you whether a gap of a few questions is real or just noise.
McNemar's test looks at how the two models did on the *same* questions and tells the two apart.

## Setup

Requires Python 3.10+.

**venv**
```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**conda**
```bash
conda create -n mcnemar python=3.12
conda activate mcnemar
pip install -r requirements.txt
```

Run the commands below with the environment activated (`deactivate` / `conda deactivate` to leave it).

## Quick start

The repository ships with synthetic example data (`data/example`), so you can try it right away:

```bash
python src/mcnemar.py --config example -a model-a -b model-b
```

This writes `result/model-a__vs__model-b__example.xlsx`.

```
[OK]   kmmlu: 550 rows
[OK]   gsm8k: 300 rows
[OK]   hellaswag: 250 rows
[OK]   ko_ifeval: 728 rows
[SKIP] winogrande: row count mismatch (A=100, B=90)
...
```

`accuracy` sheet (excerpt):

| Type | Name | Questions | model-a accuracy (%) | model-b accuracy (%) | Diff (A-B, %p) | Significance |
|---|---|---|---|---|---|---|
| Benchmark | gsm8k | 300 | 81.00 | 79.00 | 2.00 | Not significant |
| Benchmark | hellaswag | 250 | 76.80 | 84.80 | -8.00 | Significant |
| Benchmark | kmmlu | 550 | 61.27 | 50.36 | 10.91 | Significant |

`benchmark_mcnemar` sheet (excerpt):

| Benchmark | Questions | Both correct | Only model-a correct | Only model-b correct | Both wrong | p-value | Significance |
|---|---|---|---|---|---|---|---|
| gsm8k | 300 | 214 | 29 | 23 | 34 | 0.4881 | Not significant |
| hellaswag | 250 | 180 | 12 | 32 | 26 | 0.0042 | Significant |
| kmmlu | 550 | 236 | 101 | 41 | 172 | <0.0001 | Significant |

On gsm8k, A is 2%p ahead but the difference is not significant; on hellaswag, B is significantly better;
on kmmlu, A is significantly better.

Each benchmark in the example data exercises one case (see [src/configs/example.py](src/configs/example.py)):

| Benchmark | Case |
|---|---|
| kmmlu | Folder name (`cot_kmmlu`) differs from the benchmark name; 3 categories; nested run folder |
| gsm8k | `strict-match` and `flexible-extract` filters mixed in one file |
| hellaswag | model-b has a re-run → only the latest file is used |
| ko_ifeval | ifeval format |
| winogrande | The two models have different question counts → skipped |

To compare your own models, put their results under `data/{DATA_DIR}/{model name}/`
(see [Preparing data](#preparing-data)) and pick the config and model names:

```bash
python src/mcnemar.py --config legal -a my-model -b baseline-model
```

## Options

| Option | Description | Default |
|---|---|---|
| `--config`, `-c` | Config name (`example`, `legal`, `korean`, `english`) | required |
| `--model-a`, `-a` | Model A folder name | required |
| `--model-b`, `-b` | Model B folder name | required |
| `--data-dir` | Folder that holds the model folders | `data/{DATA_DIR}` |
| `--output-dir` | Where to write the report | `result/` |
| `--alpha` | Significance level | `0.05` |
| `--min-discordant` | Withhold the verdict when fewer questions than this were answered correctly by only one model | `25` |

If a model folder does not exist, the available model folders are listed.

## Preparing data

The input format follows the `--log_samples` output (`samples_*.jsonl`) of
[lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness).

### Folder layout

```
data/
  example/                        # example data (tracked in git)
  legal/                          # a config's DATA_DIR
    model-a/
      .../kbl_knowledge_em/.../samples_<task>_<timestamp>.jsonl
      .../legal_cot_kmmlu/.../samples_<task>_<timestamp>.jsonl
    model-b/
      ...
  korean/
  english/
```

- Everything under a model folder is searched recursively; the benchmark folder just has to appear somewhere in the path.
- If the benchmark folder name differs from the benchmark name, map it with `BENCH_FOLDERS` in the config.
- If a task was run more than once, only the file with the latest timestamp in its name is used (jsonl preferred over xlsx).
- Drop the evaluation output folders in as they are; no renaming or other preprocessing is needed.

### File format

- `samples_*.jsonl` or `samples_*.xlsx`, one question per line (row).
- The correctness column is looked up in this order: `exact_match`, `acc`, `q_eval`, `win_score`, `is_pass`, `valid`.
  Scores must be binary (0/1 or true/false); benchmarks with other values are skipped.
- If there is a `filter` column, a single filter is kept, by priority:
  `custom-answer` > `strict-match` > `none` > `get-answer` > `flexible-extract` > `custom-extract`.
- The category name is the task name from the file name with a `legal_cot_` / `legal_` / `cot_` prefix removed.
- Questions are paired by `doc_id` when every row has a unique one, otherwise by row order within each category.
- ifeval-style benchmarks (`ifeval`, `ko_ifeval`, `koifeval`) are expanded from `prompt_level_*` / `inst_level_*`
  into 4 categories (plsa / ilsa / plla / illa).
- `mbpp`, `humaneval`, `livecodebench`, `drop`, `ifbench`, `FunctionChat` and `NESTFul` have dedicated loaders in
  [src/loaders.py](src/loaders.py).

## Method

For each question, the two models' outcomes are counted in a 2×2 table.

|  | Model B correct | Model B wrong |
|---|---|---|
| **Model A correct** | Both correct | Only A correct |
| **Model A wrong** | Only B correct | Both wrong |

- Only the discordant pairs (`Only A correct` and `Only B correct`) decide the result.
- Chi-square McNemar's test with continuity correction (`statsmodels`), α = 0.05.
- With fewer than 25 discordant pairs the approximation is unreliable, so the verdict is withheld (`N/A (discordant < 25)`).
- Benchmarks whose question counts differ or whose questions cannot be paired are skipped (`[SKIP]`); the skipped
  benchmarks and the reasons are listed at the end of the run and in the `info` sheet.

## Report

`result/{model A}__vs__{model B}__{RESULT_SLUG}.xlsx`

| Sheet | Contents |
|---|---|
| `accuracy` | Summary: both models' accuracy, difference (A-B) and significance per benchmark / domain / category |
| `benchmark_mcnemar` | Test results per benchmark (+ `EXTRA_GROUPS` aggregates) |
| `domain_mcnemar` | Test results per domain |
| `{benchmark}` | Test results per category (sub-task) for benchmarks in `CATEGORY_BENCHMARKS` |
| `raw` | Per-question correct/incorrect for both models |
| `info` | Run details: models, config, data path, α, timestamp, compared and skipped benchmarks with reasons |

- Significant results are highlighted in red (the whole row in test sheets, the Significance cell in `accuracy`).
- The sign of `Diff (A-B, %p)` gives the direction: positive means A is higher, negative means B is higher.
- Every sheet has a frozen header and filters.
- p-values below 0.0001 are shown as `<0.0001` (the cell keeps the exact value).
- Domains defined in `DOMAIN_AVERAGE` are a simple mean of their sub-items, so their question and correct counts show `-`.

## Configs

| Name | Data folder | Contents |
|---|---|---|
| `example` | `data/example` | Synthetic example data |
| `legal` | `data/legal` | Korean legal benchmarks (KBL, KoLBench, kmmlu law, ...) + common Korean benchmarks |
| `korean` | `data/korean` | Korean benchmarks (kmmlu, ko_sovereign, kobest, click, ...) |
| `english` | `data/english` | English benchmarks (mmlu_pro, gpqa, bbh, gsm8k, humaneval, ...) |

### Adding a config

Create `src/configs/<name>.py` and it is available as `--config <name>`. Minimal example:

```python
DATA_DIR = "my_domain"            # data/my_domain/{model}/...
RESULT_SLUG = "my_domain"         # report file name suffix

BENCHMARKS = ["kmmlu", "gsm8k"]
CATEGORY_BENCHMARKS = ["kmmlu"]   # benchmarks that get a per-category sheet

DOMAIN_TO_BENCHMARKS = {          # domain -> benchmarks or categories
    "Expert Knowledge": ["kmmlu"],
    "Math": ["gsm8k"],
}
DOMAINS = list(DOMAIN_TO_BENCHMARKS)
```

For the optional keys (`BENCH_FOLDERS`, `DOMAIN_AVERAGE`, `EXTRA_GROUPS`, ...) see
[src/configs/\_\_init\_\_.py](src/configs/__init__.py) and [src/configs/legal.py](src/configs/legal.py).

## Project layout

```
src/
  mcnemar.py          # CLI, McNemar's test, accuracy, Excel report
  loaders.py          # finding and loading result files
  configs/            # per-domain configs (example, legal, korean, english)
tests/                # pytest (end-to-end runs on synthetic data)
data/                 # evaluation results (git-ignored except data/example)
result/               # reports (git-ignored)
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```
