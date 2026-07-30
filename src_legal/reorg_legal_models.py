#!/usr/bin/env python3
"""midm-legal / llama-legal 폴더를 gemma-4-26B-A4B-Legel 구조에 맞게 정규화."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEGAL_BASE = REPO_ROOT / "법률"
DEFAULT_TS = "2026-01-01T00-00-00.000000"

TS_IN_NAME = re.compile(r"_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}\.\d+(?:_v\d+)?")


def samples_name(task_stem: str, ts: str = DEFAULT_TS) -> str:
    return f"samples_{task_stem}_{ts}.jsonl"


def extract_ts(filename: str) -> str:
    m = TS_IN_NAME.search(Path(filename).stem)
    return m.group(0).lstrip("_") if m else DEFAULT_TS


def move_jsonl(src: Path, dest_dir: Path, dest_name: str, log: list[str]) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / dest_name
    if dest.exists():
        log.append(f"  [SKIP] already exists: {dest.relative_to(REPO_ROOT)}")
        return
    shutil.move(str(src), str(dest))
    log.append(f"  [MOVE] {src.relative_to(REPO_ROOT)} → {dest.relative_to(REPO_ROOT)}")


def move_sidecars(src_jsonl: Path, dest_dir: Path, dest_stem: str, log: list[str]) -> None:
    """같은 폴더의 results/samples xlsx·json 등을 함께 이동."""
    parent = src_jsonl.parent
    ts = extract_ts(src_jsonl.name)
    for pattern in (f"{src_jsonl.stem}.xlsx", f"results_{ts}.json"):
        for f in parent.glob(pattern):
            dest = dest_dir / f.name.replace(src_jsonl.stem, dest_stem)
            if dest.exists():
                continue
            shutil.move(str(f), str(dest))
            log.append(f"  [SIDE] {f.relative_to(REPO_ROOT)} → {dest.relative_to(REPO_ROOT)}")


def reorg_midm(model_root: Path, run_dir: str, log: list[str]) -> None:
    log.append(f"\n########## {model_root.name} ##########")

    def go(src: Path, category: str, bench: str, task_stem: str) -> None:
        dest_dir = model_root / category / bench / run_dir
        move_jsonl(src, dest_dir, samples_name(task_stem), log)

    root = model_root

    singles = {
        "gsm8k/gsm8k.jsonl": ("공통지표", "legal_cot_gsm8k_zeroshot", "legal_cot_gsm8k_zeroshot"),
        "ko_winogrande/ko_winogrande.jsonl": ("공통지표", "legal_cot_ko-winogrande_zeroshot", "legal_cot_ko-winogrande_zeroshot"),
        "ko_comprehensivegen/ko_comprehensivegen.jsonl": ("공통지표", "legal_cot_ko_comprehensivegen_golden", "legal_cot_ko_comprehensivegen_golden"),
        "kobalt_700/kobalt_700.jsonl": ("공통지표", "legal_kobalt_700", "legal_kobalt_700"),
        "ko_ifeval/ko_ifeval.jsonl": ("공통지표", "legal_koifeval_new", "legal_koifeval_new"),
        "kmmlu_pro/kmmlu_pro.jsonl": ("법률지표", "legal_kmmlu-pro", "legal_kmmlu-pro"),
    }
    for rel, (cat, bench, stem) in singles.items():
        src = root / rel
        if src.exists():
            go(src, cat, bench, stem)

    for src in sorted((root / "ko_sovereign").glob("*.jsonl")):
        sub = src.stem.replace("ko_sovereign_", "")
        if sub == "law":
            go(src, "법률지표", "legal_cot_ko_sovereign_law", "legal_cot_ko_sovereign_law")
        else:
            go(src, "공통지표", "legal_cot_ko_sovereign_etc", f"legal_cot_ko_sovereign_{sub}")

    prag_map = {
        "k_honorifics": "legal_cot_k_honorifics",
        "k_implicature": "legal_cot_k_implicature",
        "k_lexicon": "legal_cot_k_lexicon",
    }
    for src in sorted((root / "k_pragmatics").glob("*.jsonl")):
        sub = src.stem
        bench = prag_map[sub]
        dest_dir = root / "공통지표" / "legal_pragmatics" / bench / run_dir
        move_jsonl(src, dest_dir, samples_name(bench), log)

    for src in sorted((root / "kbl_knowledge_em").glob("*.jsonl")):
        task = src.stem.replace("kbl_knowledge_em_", "")
        go(src, "법률지표", "kbl_knowledge_em", f"kbl_{task}")

    for src in sorted((root / "kbl_reasoning").glob("*.jsonl")):
        task = src.stem.replace("kbl_reasoning_", "")
        go(src, "법률지표", "kbl_reasoning_em", f"kbl_{task}")

    for src in sorted((root / "kmmlu").glob("*.jsonl")):
        sub = src.stem.replace("kmmlu_", "")
        go(src, "법률지표", "legal_cot_kmmlu", f"legal_cot_kmmlu_{sub}")

    for src in sorted((root / "kolbench").glob("*.jsonl")):
        bench = src.stem  # kolbench_dq etc.
        go(src, "법률지표", bench, bench)


def _normalize_llama_samples_name(filename: str) -> str:
    """llama 원본 파일명을 gemma 기준 samples_* 이름으로 정규화."""
    p = Path(filename)
    stem, suffix = p.stem, p.suffix
    if not stem.startswith("samples_"):
        return filename

    ts = extract_ts(filename)
    inner = TS_IN_NAME.sub("", stem[len("samples_"):])

    renames = {
        "cot_gsm8k_zeroshot": "legal_cot_gsm8k_zeroshot",
        "cot_ko-winogrande_zeroshot": "legal_cot_ko-winogrande_zeroshot",
        "cot_ko_comprehensivegen": "legal_cot_ko_comprehensivegen_golden",
        "cot_kmmlu_law": "legal_cot_kmmlu_law",
        "cot_kmmlu_criminal_law": "legal_cot_kmmlu_criminal_law",
        "kmmlu-pro": "legal_kmmlu-pro",
        "kobalt_700": "legal_kobalt_700",
        "koifeval_new": "legal_koifeval_new",
    }
    if inner in renames:
        inner = renames[inner]
    elif inner.startswith("cot_ko_sovereign_"):
        inner = "legal_" + inner  # cot_ko_sovereign_X → legal_cot_ko_sovereign_X
    elif inner.startswith("cot_k_"):
        inner = "legal_" + inner  # cot_k_honorifics → legal_cot_k_honorifics

    return f"samples_{inner}_{ts}{suffix}"


def _move_file(src: Path, dest_dir: Path, dest_name: str | None, log: list[str], tag: str = "MOVE") -> None:
    if src.name.startswith("._") or not src.is_file():
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (dest_name or src.name)
    if dest.exists():
        log.append(f"  [SKIP] already exists: {dest.relative_to(REPO_ROOT)}")
        return
    shutil.move(str(src), str(dest))
    log.append(f"  [{tag}] {src.relative_to(REPO_ROOT)} → {dest.relative_to(REPO_ROOT)}")


def _move_samples_tree(src_dir: Path, dest_dir: Path, log: list[str], rename: bool = True) -> None:
    """src_dir 아래 samples_*/results_* 파일을 dest_dir 로 이동 (이름 정규화 옵션)."""
    if not src_dir.is_dir():
        return
    for f in sorted(src_dir.rglob("*")):
        if not f.is_file() or f.name.startswith("._"):
            continue
        if not (f.name.startswith("samples_") or f.name.startswith("results_")):
            continue
        dest_name = _normalize_llama_samples_name(f.name) if rename and f.name.startswith("samples_") else f.name
        _move_file(f, dest_dir, dest_name, log)


def reorg_llama(model_root: Path, run_dir: str, log: list[str]) -> None:
    """flat llama-legal → gemma 구조(법률지표|공통지표/{bench}/{run}/)."""
    log.append(f"\n########## {model_root.name} ##########")

    # (src_rel, category, bench_folder)
    mappings: list[tuple[str, str, str]] = [
        # 법률지표
        ("kbl_knowledge_em", "법률지표", "kbl_knowledge_em"),
        ("kbl_reasoning_em", "법률지표", "kbl_reasoning_em"),
        ("kmmlu_law", "법률지표", "legal_cot_kmmlu"),
        ("kmmlu_criminal_law", "법률지표", "legal_cot_kmmlu"),
        ("kmmlu_pro", "법률지표", "legal_kmmlu-pro"),
        ("ko-sovereign_law", "법률지표", "legal_cot_ko_sovereign_law"),
        ("last_kolbench/kolbench_qa", "법률지표", "kolbench_qa"),
        ("last_kolbench/kolbench_reason", "법률지표", "kolbench_reason"),
        ("last_kolbench/kolbench_dq", "법률지표", "kolbench_dq"),
        # 공통지표
        ("cot_gsm8k_zeroshot", "공통지표", "legal_cot_gsm8k_zeroshot"),
        ("cot_ko-winogrande_zeroshot", "공통지표", "legal_cot_ko-winogrande_zeroshot"),
        ("kobalt-700", "공통지표", "legal_kobalt_700"),
        ("koifeval_new", "공통지표", "legal_koifeval_new"),
        ("ko-comprehensivegen", "공통지표", "legal_cot_ko_comprehensivegen_golden"),
    ]

    for src_rel, cat, bench in mappings:
        src_dir = model_root / src_rel
        dest_dir = model_root / cat / bench / run_dir
        _move_samples_tree(src_dir, dest_dir, log)

    # ko_sovereign etc (nested culture_folklore 포함). law 는 별도 폴더에서 이미 이동.
    sov_src = model_root / "cot_ko_sovereign"
    if sov_src.is_dir():
        etc_dest = model_root / "공통지표" / "legal_cot_ko_sovereign_etc" / run_dir
        law_dest = model_root / "법률지표" / "legal_cot_ko_sovereign_law" / run_dir
        for f in sorted(sov_src.rglob("*")):
            if not f.is_file() or f.name.startswith("._"):
                continue
            if not (f.name.startswith("samples_") or f.name.startswith("results_")):
                continue
            dest_dir = law_dest if "sovereign_law" in f.name else etc_dest
            dest_name = (
                _normalize_llama_samples_name(f.name)
                if f.name.startswith("samples_")
                else f.name
            )
            _move_file(f, dest_dir, dest_name, log, tag="SOV")

    # pragmatics: honorifics / implicature / lexicon
    # referential 은 gemma 기준에 없어 _extra 로 보관 (mcnemar k_pragmatics 오염 방지)
    prag_src = model_root / "cot_kt_new-benchmarks"
    if prag_src.is_dir():
        for key in ("honorifics", "implicature", "lexicon", "referential"):
            bench = f"legal_cot_k_{key}"
            if key == "referential":
                dest_dir = model_root / "_extra" / bench / run_dir
            else:
                dest_dir = model_root / "공통지표" / "legal_pragmatics" / bench / run_dir
            for f in sorted(prag_src.glob(f"*_{key}_*")):
                dest_name = (
                    _normalize_llama_samples_name(f.name)
                    if f.name.startswith("samples_")
                    else f.name
                )
                _move_file(f, dest_dir, dest_name, log, tag="PRAG")
            for samples in dest_dir.glob(f"samples_legal_cot_k_{key}_*"):
                ts = extract_ts(samples.name)
                for res in prag_src.glob(f"results_{ts}.*"):
                    _move_file(res, dest_dir, res.name, log, tag="PRAG")

    # comprehensivegen orphan results (파일명에 task 없음 → ts 매칭)
    comp_dest = model_root / "공통지표" / "legal_cot_ko_comprehensivegen_golden" / run_dir
    if comp_dest.is_dir():
        for samples in comp_dest.glob("samples_*"):
            ts = extract_ts(samples.name)
            for leftover in (
                model_root / "cot_kt_new-benchmarks",
                model_root,
            ):
                if not leftover.is_dir():
                    continue
                for res in leftover.glob(f"results_{ts}.*"):
                    _move_file(res, comp_dest, res.name, log, tag="COMP")


def cleanup_empty_dirs(root: Path, log: list[str]) -> None:
    for d in sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if d.is_dir() and d != root and not any(d.iterdir()):
            d.rmdir()
            log.append(f"  [RMDIR] {d.relative_to(REPO_ROOT)}")


def main() -> None:
    import sys

    log: list[str] = ["===== 법률 midm-legal / llama-legal 구조 정규화 ====="]
    targets = [
        (LEGAL_BASE / "midm-legal", "midm-legal", reorg_midm),
        (LEGAL_BASE / "llama-legal", "llama-legal", reorg_llama),
    ]
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    for model_root, run_dir, fn in targets:
        if only and model_root.name not in only:
            continue
        if not model_root.is_dir():
            log.append(f"\n[MISSING] {model_root}")
            continue
        fn(model_root, run_dir, log)
        cleanup_empty_dirs(model_root, log)

    out = REPO_ROOT / f"reorg_legal_models_{Path(__file__).stem}.log"
    out.write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log))
    print(f"\n[LOG] {out}")


if __name__ == "__main__":
    main()
