import os
from datetime import datetime

target_tasks_finance = [
    "KoIFEval"
]

custom_keyword_map_finance = {
    "kbl_knowledge_em": {
        ("kbl","common_legal_mistake_qa_em"): "kbl_common_legal_mistake_qa_em",
        ("kbl","common_legal_mistake_qa_reasoning_em"): "kbl_common_legal_mistake_qa_reasoning_em",
        ("kbl","concept"): "kbl_legal_concept_qa_em",
        ("kbl","offense"): "kbl_offense_component_qa_em",
        ("kbl","query"): "kbl_query_and_statute_matching_qa_em",
        ("kbl","hallucination"): "kbl_statute_hallucination_qa_em",
        ("kbl","number"): "kbl_statute_number_and_content_matching_qa_em",
    },
    "kbl_reasoning": {
        ("kbl","qa_p"): "kbl_case_relevance_qa_p_em",
        ("kbl","qa_q"): "kbl_case_relevance_qa_q_em",
        ("kbl","causal"): "kbl_causal_reasoning_qa_em",
        ("kbl","statement"): "kbl_statement_consistency_qa_em",
    },
    "법률지식_QA": {
        ("kmmlu", "criminal_law"): "kmmlu_criminal_law",
        ("kmmlu", "law"): "kmmlu_law",
        ("kmmlu", "pro"): "kmmlu_pro",
        ("sovereign", "law"): "ko_sovereign_law",
        ("kbl","common_legal_mistake_qa_em"): "kbl_common_legal_mistake_qa_em",
        ("kbl","common_legal_mistake_qa_reasoning_em"): "kbl_common_legal_mistake_qa_reasoning_em",
        ("kbl","concept"): "kbl_legal_concept_qa_em",
        ("kbl","offense"): "kbl_offense_component_qa_em",
        ("kbl","query"): "kbl_query_and_statute_matching_qa_em",
        ("kbl","hallucination"): "kbl_statute_hallucination_qa_em",
        ("kbl","number"): "kbl_statute_number_and_content_matching_qa_em",
        ("kolbench","qa"): "kolbench_qa",
    },
    "법률추론": {
        ("kbl","qa_p"): "kbl_case_relevance_qa_p_em",
        ("kbl","qa_q"): "kbl_case_relevance_qa_q_em",
        ("kbl","causal"): "kbl_causal_reasoning_qa_em",
        ("kbl","statement"): "kbl_statement_consistency_qa_em",
        ("kolbench","reason"): "kolbench_reason",
    },
    "법률문서해석": {
        ("kolbench", "dq"): "kolbench_dq",
    },
    "한국어이해": {
        ("honorifics",): "k_honorifics",
        ("implicature",): "k_implicature",
        ("lexicon",): "k_lexicon",
        ("kobalt","700"): "kobalt_700",
    },
    "한국어생성": {
        ("comprehensivegen"): "ko_comprehensivegen",
    },
    "한국어추론": {
        ("ko-winogrande"): "ko-winogrande",
    },
    "한국어전문지식": {
        ("sovereign", "culture"): "ko_sovereign_culture_folklore",
        ("sovereign", "education"): "ko_sovereign_education",
        ("sovereign", "geography"): "ko_sovereign_geography",
        ("sovereign", "history"): "ko_sovereign_history",
        ("sovereign", "language"): "ko_sovereign_language_literature",
        ("sovereign", "economics"): "ko_sovereign_economics_finance",
        ("sovereign", "politics"): "ko_sovereign_politics",
        ("sovereign", "society"): "ko_sovereign_society",
    },
    "수학": {
        ("gsm8k"): "gsm8k",
    },
}


def matches_all_keywords(filename, keywords):
    return all(k.lower() in filename.lower() for k in keywords)

def rename_file_in_task_folders(root_folder, target_tasks, custom_keyword_map, dry_run=False):
    log_lines = []

    for model_name in os.listdir(root_folder):
        if model_name == 'dataset':
            print(f'⏩ 무시: {model_name} (dataset)')
            continue

        model_path = os.path.join(root_folder, model_name)
        if not os.path.isdir(model_path):
            continue

        all_tasks = set(target_tasks) | set(custom_keyword_map.keys())

        for task_name in all_tasks:
            task_path = os.path.join(model_path, task_name)
            if not os.path.isdir(task_path):
                continue

            files = [f for f in os.listdir(task_path)
                     if os.path.splitext(f)[1] in ['.jsonl', '.xlsx', '.json']]

            # ✅ 컨스텀 키워드 메이킹 처리
            if task_name in custom_keyword_map:
                for old_filename in files:
                    matched = False
                    best_match = None
                    best_base = None

                    for keyword_tuple, new_base in custom_keyword_map[task_name].items():
                        if matches_all_keywords(old_filename, keyword_tuple):
                            # 최고의 중차 클릭을 최선시킨다
                            if best_match is None or len("_".join(keyword_tuple)) > len("_".join(best_match)):
                                best_match = keyword_tuple
                                best_base = new_base

                    if best_base:
                        ext = os.path.splitext(old_filename)[1]
                        new_filename = f"{best_base}{ext}"
                        old_path = os.path.join(task_path, old_filename)
                        new_path = os.path.join(task_path, new_filename)

                        # ✅ 이미 새 이름이면 변경하지 않음
                        if old_filename == new_filename:
                            print(f'⏩ {model_name}/{task_name}/{old_filename}: 이미 올바른 이름')
                            continue

                        print(f'✅ {model_name}/{task_name}/{old_filename} → {new_filename}')
                        log_lines.append(f'{model_name}/{task_name}/{old_filename} → {new_filename}')
                        if not dry_run:
                            os.rename(old_path, new_path)
                    else:
                        print(f'⚠️ {model_name}/{task_name}: 키워드 매칭 실패 - {old_filename}')
                continue  # 컨스텀 task는 일반 처리 안 함

            # ✅ 일반 task 처리: 파일 1개일 때만
            if len(files) != 1:
                print(f'⚠️ {model_name}/{task_name}: 일반 처리 불가 (파일 수 {len(files)}개)')
                continue

            old_filename = files[0]
            ext = os.path.splitext(old_filename)[1]
            new_filename = f"{task_name}{ext}"
            old_path = os.path.join(task_path, old_filename)
            new_path = os.path.join(task_path, new_filename)

            # ✅ 이미 새 이름이면 변경하지 않음
            if old_filename == new_filename:
                print(f'⏩ {model_name}/{task_name}/{old_filename}: 이미 올바른 이름')
                continue

            print(f'✅ {model_name}/{task_name}/{old_filename} → {new_filename}')
            log_lines.append(f'{model_name}/{task_name}/{old_filename} → {new_filename}')
            if not dry_run:
                os.rename(old_path, new_path)

    # ✅ 로그 저장
    if not dry_run and log_lines:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        folder_tag = os.path.basename(root_folder).replace(' ', '_')
        log_filename = f'rename_log_{folder_tag}_{timestamp}.txt'

        with open(log_filename, 'w', encoding='utf-8') as f:
            for line in log_lines:
                f.write(line + '\n')
        print(f'\n📜 로그 저장 완료: {log_filename}')


# ✅ 실행
rename_file_in_task_folders(
    root_folder='./법률지표',
    target_tasks=target_tasks_finance,
    custom_keyword_map=custom_keyword_map_finance,
    dry_run=False
)
