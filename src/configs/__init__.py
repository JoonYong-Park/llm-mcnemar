"""Per-domain McNemar's test configs.

`python src/mcnemar.py --config <name>`: <name> is a module in this folder (example, legal, korean, english).
Modules whose names start with `_` are not listed as configs.

[Required]
  DATA_DIR              Data folder under data/. Layout: data/{DATA_DIR}/{model}/**/{benchmark folder}/...
                        (override the whole path with --data-dir)
  RESULT_SLUG           Report file suffix -> result/{A}__vs__{B}__{RESULT_SLUG}.xlsx
  BENCHMARKS            Benchmarks to compare
  DOMAINS               Domains to report (keys of DOMAIN_TO_BENCHMARKS to use)
  DOMAIN_TO_BENCHMARKS  Domain -> benchmarks/categories (question-weighted)
  CATEGORY_BENCHMARKS   Benchmarks that get a per-category (sub-task) sheet

[Optional]
  DOMAIN_AVERAGE        Domain -> sub-items (benchmarks, categories or other domains). In the accuracy
                        sheet these domains use the simple mean of the sub-item scores instead of weighting
  BENCH_FOLDERS         Benchmark name -> actual folder name (default: folder name = benchmark name)
  SINGLE_FILE_BENCH     Benchmarks whose category is the benchmark name rather than the file name
  BENCHMARK_LABELS      Benchmark name -> label shown in the report
  EXTRA_GROUPS          Extra aggregate rows: label -> {"benchmarks": [...], "category_contains": "token" (optional)}
  ALPHA                 Significance level (default 0.05, overridden by --alpha)
  MIN_DISCORDANT        Withhold the verdict below this many discordant pairs (default 25, --min-discordant)
"""
