import os
from datetime import datetime

target_tasks_kor = [
    "k_referential",
    "k_referential_hard",
    "Ko-ComprehensiveGen",
    "Ko-ComprehensiveGen-hard",
    "KoIFEval",
    "ko-winogrande",
    "korean_naturalization",
    "Ko_InFoBench",
    "kobalt700",
    "ko_commongenv2",
    "hrmcr"
]

target_tasks_eng = [
    "gsm8k",
    "ifeval",
    "winogrande",
    "piqa",
    "boolq",
    "mbpp",
    "drop",
    "openbookqa",
    "InFoBench",
    "humaneval",
    "livecodebench",
    "aqua-rat",
    "aime2025",
]

custom_keyword_map_kor = {
    "kpragmatics": {
        ("honorifics",): "k_honorifics",
        ("implicature",): "k_implicature",
        ("lexicon",): "k_lexicon",
    },
    "kpragmatics_hard": {
        ("Honorifics",): "K-Honorifics-hard",
        ("Implicature",): "K-Implicature-hard",
        ("Lexicon",): "K-Lexicon-hard",
    },
    "ko_sovereign": {
        ("sovereign", "culture"): "ko_sovereign_culture_folklore",
        ("sovereign", "economic"): "ko_sovereign_economics_finance",
        ("sovereign", "education"): "ko_sovereign_education",
        ("sovereign", "geography"): "ko_sovereign_geography",
        ("sovereign", "history"): "ko_sovereign_history",
        ("sovereign", "language"): "ko_sovereign_language_literature",
        ("sovereign", "law"): "ko_sovereign_law",
        ("sovereign", "politics"): "ko_sovereign_politics",
        ("sovereign", "society"): "ko_sovereign_society",
    },
    "kobest": {
        ("kobest", "boolq"): "kobest_boolq",
        ("kobest", "copa"): "kobest_copa",
        ("kobest", "hellaswag"): "kobest_hellaswag",
        ("kobest", "sentineg"): "kobest_sentineg",
        ("kobest", "wic"): "kobest_wic",
    },
    "korean_national_civil_service": {
        ("korean_national_civil_service", "education"): "korean_national_civil_service_education",
        ("korean_national_civil_service", "historical"): "korean_national_civil_service_historical_sources",
        ("korean_national_civil_service", "Joseon"): "korean_national_civil_service_Joseon",
        ("korean_national_civil_service", "law"): "korean_national_civil_service_law",
        ("korean_national_civil_service", "modern"): "korean_national_civil_service_modern_contemporary",
        ("korean_national_civil_service", "prehistoric"): "korean_national_civil_service_prehistoric_goryeo",
    },
    "kmmlu": {
        ("kmmlu", "accounting"): "kmmlu_accounting",
        ("kmmlu", "agricultural"): "kmmlu_agricultural_sciences",
        ("kmmlu", "aviation_engineering"): "kmmlu_aviation_engineering_and_maintenance",
        ("kmmlu", "biology"): "kmmlu_biology",
        ("kmmlu", "chemical_engineering"): "kmmlu_chemical_engineering",
        ("kmmlu", "chemistry"): "kmmlu_chemistry",
        ("kmmlu", "civil_engineering"): "kmmlu_civil_engineering",
        ("kmmlu", "computer_science"): "kmmlu_computer_science",
        ("kmmlu", "construction"): "kmmlu_construction",
        ("kmmlu", "criminal_law"): "kmmlu_criminal_law",

        ("kmmlu", "ecology"): "kmmlu_ecology",
        ("kmmlu", "economics"): "kmmlu_economics",
        ("kmmlu", "education"): "kmmlu_education",
        ("kmmlu", "electrical_engineering"): "kmmlu_electrical_engineering",
        ("kmmlu", "electronics_engineering"): "kmmlu_electronics_engineering",
        ("kmmlu", "energy_management"): "kmmlu_energy_management",
        ("kmmlu", "environmental_science"): "kmmlu_environmental_science",
        ("kmmlu", "fashion"): "kmmlu_fashion",
        ("kmmlu", "food_processing"): "kmmlu_food_processing",
        ("kmmlu", "gas_technology"): "kmmlu_gas_technology_and_engineering",

        ("kmmlu", "geomatics"): "kmmlu_geomatics",
        ("kmmlu", "health"): "kmmlu_health",
        ("kmmlu", "industrial_engineer"): "kmmlu_industrial_engineer",
        ("kmmlu", "information_technology"): "kmmlu_information_technology",
        ("kmmlu", "interior_architecture"): "kmmlu_interior_architecture_and_design",
        ("kmmlu", "korean_history"): "kmmlu_korean_history",
        ("kmmlu", "law"): "kmmlu_law",
        ("kmmlu", "machine_design"): "kmmlu_machine_design_and_manufacturing",
        ("kmmlu", "management"): "kmmlu_management",
        ("kmmlu", "maritime"): "kmmlu_maritime_engineering",

        ("kmmlu", "marketing"): "kmmlu_marketing",
        ("kmmlu", "materials_engineering"): "kmmlu_materials_engineering",
        ("kmmlu", "math"): "kmmlu_math",
        ("kmmlu", "mechanical_engineering"): "kmmlu_mechanical_engineering",
        ("kmmlu", "nondestructive"): "kmmlu_nondestructive_testing",
        ("kmmlu", "patent"): "kmmlu_patent",
        ("kmmlu", "political_science"): "kmmlu_political_science_and_sociology",
        ("kmmlu", "psychology"): "kmmlu_psychology",
        ("kmmlu", "public_safety"): "kmmlu_public_safety",
        ("kmmlu", "railway"): "kmmlu_railway_and_automotive_engineering",

        ("kmmlu", "real_estate"): "kmmlu_real_estate",
        ("kmmlu", "refrigerating_machinery"): "kmmlu_refrigerating_machinery",
        ("kmmlu", "social_welfare"): "kmmlu_social_welfare",
        ("kmmlu", "taxation"): "kmmlu_taxation",
        ("kmmlu", "telecommunications"): "kmmlu_telecommunications_and_wireless_technology",
    },
    "hrm8k": {
        ("hrm8k", "gsm8k"): "hrm8k_gsm8k_math_verify",
        ("hrm8k", "ksm"): "hrm8k_ksm_math_verify",
        ("hrm8k", "hrm8k_math_math"): "hrm8k_math_math_verify",
        ("hrm8k", "mmmlu"): "hrm8k_mmmlu_math_verify",
        ("hrm8k", "omni"): "hrm8k_omni_math_math_verify",
    },
    "haerae": {
        ("haerae", "definition"): "haerae_correct_definition_matching",
        ("haerae", "geo"): "haerae_csat_geo",
        ("haerae", "law"): "haerae_csat_law",
        ("haerae", "socio"): "haerae_csat_socio",
        ("haerae", "date"): "haerae_date_understanding",
        ("haerae", "general"): "haerae_general_knowledge",
        ("haerae", "history"): "haerae_history",
        ("haerae", "loan"): "haerae_loan_words",
        ("haerae", "lyrics"): "haerae_lyrics_denoising",
        ("haerae", "proverbs"): "haerae_proverbs_denoising",
        ("haerae", "rare"): "haerae_rare_words",
        ("haerae", "reading"): "haerae_reading_comprehension",
        ("haerae", "standard"): "haerae_standard_nomenclature",
    },
    "click": {
        ("click", "economy_kiip"): "click_economy_kiip",
        ("click", "economy_kedu"): "click_economy_kedu",
        ("click", "functional_csat"): "click_functional_csat",
        ("click", "functional_kedu"): "click_functional_kedu",
        ("click", "functional_pse"): "click_functional_pse",
        ("click", "geography_csat"): "click_geography_csat",
        ("click", "geography_kedu"): "click_geography_kedu",
        ("click", "geography_kiip"): "click_geography_kiip",
        ("click", "grammar_csat"): "click_grammar_csat",
        ("click", "grammar_kedu"): "click_grammar_kedu",
        ("click", "grammar_topik"): "click_grammar_topik",
        ("click", "history_kedu"): "click_history_kedu",
        ("click", "history_khb"): "click_history_khb",
        ("click", "history_pse"): "click_history_pse",
        ("click", "law_kiip"): "click_law_kiip",
        ("click", "law_psat"): "click_law_psat",
        ("click", "politics_kedu"): "click_politics_kedu",
        ("click", "politics_kiip"): "click_politics_kiip",
        ("click", "popular_kedu"): "click_popular_kedu",
        ("click", "popular_kiip"): "click_popular_kiip",
        ("click", "society_kedu"): "click_society_kedu",
        ("click", "society_kiip"): "click_society_kiip",
        ("click", "textual_csat"): "click_textual_csat",
        ("click", "textual_topik"): "click_textual_topik",
        ("click", "tradition_kedu"): "click_tradition_kedu",
        ("click", "tradition_kiip"): "click_tradition_kiip",
    },
}

custom_keyword_map_eng = {
    "musr": {
        ("musr", "murder"): "musr_murder_mysteries",
        ("musr", "object"): "musr_object_placements",
        ("musr", "allocation"): "musr_team_allocation",
    },
    "gpqa": {
        ("gpqa", "diamond"): "gpqa_diamond",
        ("gpqa", "extended"): "gpqa_extended",
        ("gpqa", "main"): "gpqa_main",
    },
    "math": {
        ("math", "algebra"): "math_algebra",
        ("math", "counting"): "math_counting_and_prob",
        ("math", "geometry"): "math_geometry",
        ("math", "intermediate"): "math_intermediate_algebra",
        ("math", "theory"): "math_num_theory",
        ("math", "prealgebra"): "math_prealgebra",
        ("math", "precalculus"): "math_precalculus",
    },
    "mmlu_pro": {
        ("mmlu_pro", "biology"): "mmlu_pro_biology",
        ("mmlu_pro", "business"): "mmlu_pro_business",
        ("mmlu_pro", "chemistry"): "mmlu_pro_chemistry",
        ("mmlu_pro", "computer"): "mmlu_pro_computer science",
        ("mmlu_pro", "economics"): "mmlu_pro_economics",
        ("mmlu_pro", "engineering"): "mmlu_pro_engineering",
        ("mmlu_pro", "health"): "mmlu_pro_health",
        ("mmlu_pro", "history"): "mmlu_pro_history",
        ("mmlu_pro", "law"): "mmlu_pro_law",
        ("mmlu_pro", "math"): "mmlu_pro_math",
        ("mmlu_pro", "other"): "mmlu_pro_other",
        ("mmlu_pro", "philosophy"): "mmlu_pro_philosophy",
        ("mmlu_pro", "physics"): "mmlu_pro_physics",
        ("mmlu_pro", "psychology"): "mmlu_pro_psychology",
    },
    "bbh": {
        ("bbh", "boolean"): "bbh_boolean_expressions",
        ("bbh", "causal"): "bbh_causal_judgement",
        ("bbh", "date"): "bbh_date_understanding",
        ("bbh", "disambiguation"): "bbh_disambiguation_qa",
        ("bbh", "formal"): "bbh_formal_fallacies",
        ("bbh", "geometric"): "bbh_geometric_shapes",
        ("bbh", "hyperbaton"): "bbh_hyperbaton",
        ("bbh", "deduction_five_objects"): "bbh_logical_deduction_five_objects",
        ("bbh", "deduction_seven_objects"): "bbh_logical_deduction_seven_objects",
        ("bbh", "deduction_three_objects"): "bbh_logical_deduction_three_objects",
        ("bbh", "movie"): "bbh_movie_recommendation",
        ("bbh", "navigate"): "bbh_navigate",
        ("bbh", "counting"): "bbh_object_counting",
        ("bbh", "penguins"): "bbh_penguins_in_a_table",
        ("bbh", "reasoning"): "bbh_reasoning_about_colored_objects",
        ("bbh", "ruin"): "bbh_ruin_names",
        ("bbh", "salient"): "bbh_salient_translation_error_detection",
        ("bbh", "snarks"): "bbh_snarks",
        ("bbh", "sports"): "bbh_sports_understanding",
        ("bbh", "temporal"): "bbh_temporal_sequences",
        ("bbh", "objects_five"): "bbh_tracking_shuffled_objects_five_objects",
        ("bbh", "objects_seven"): "bbh_tracking_shuffled_objects_seven_objects",
        ("bbh", "objects_three"): "bbh_tracking_shuffled_objects_three_objects",
        ("bbh", "web"): "bbh_web_of_lies",
    }
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
    root_folder='./한국적지표',
    target_tasks=target_tasks_kor,
    custom_keyword_map=custom_keyword_map_kor,
    dry_run=False
)

rename_file_in_task_folders(
    root_folder='./영어지표',
    target_tasks=target_tasks_eng,
    custom_keyword_map=custom_keyword_map_eng,
    dry_run=False
)
