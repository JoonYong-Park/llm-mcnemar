## 한국어 벤치마크
# KOR_BENCHMARKS = ['ko_ifeval','k_pragmatics','ko_sovereign','kobalt700','click','ko_comprehensivegen_golden','ko_commongenv2','ko_winogrande','hrmcr','k_referential','kmmlu','hrm8k','aime2025_ko']
# KOR_DOMAIN = ['한국어이해','한국어생성','한국어추론','한국사회문화','한국전문지식','한국어지시이행도','한국어수학','ko_sovereign_한국사회문화','ko_sovereign_한국전문지식','click_언어','click_문화','KMMLU_Applied_Science','KMMLU_HUMSS','KMMLU_Other','KMMLU_STEM','click_economy','click_functional','click_geography','click_grammar','click_history','click_law','click_politics','click_popular','click_society','click_textual','click_tradition']

'''
1. 오면 파일 열어봐라
2. 이름 변경
3. 서브셋 있는지 확인 (있으면 CATEGORY_BENCHMARKS에 추가)
4. 정답 여부 컬럼 이름 확인(이름 다르면 rename_and_filter_em_column에 추가)

[변수]
- 카테고리가 그 안에서 나눠짐(파일 안에서 직접 나누기)
- 지표가 
'''
####################################

KOR_BENCHMARKS = ['ko_sovereign','click']
KOR_DOMAIN = ['한국어이해','한국사회문화','한국전문지식','click_언어','click_문화']

## 카테고리 영역 필요한 벤치마크
CATEGORY_BENCHMARKS = ['BFCL','FunctionChat','NESTFul','kmmlu', 'ko_sovereign', 'kobest', 'k_pragmatics', 'k_pragmatics_hard', 'ko_ifeval','click', 'haerae', 'hrm8k', 'korean_national_civil_service', 'hrmcr','bbh', 'gpqa', 'ifeval','ifbench', 'math_hard', 'mmlu_pro', 'musr', 'kbl_knowledge_em', 'kbl_reasoning', 'kolbench', 'korfin', 'konet','csat_2025','csat_2026','kmmlu_pro','hle','global_mmlu']

####################################

## 영어 벤치마크
EN_BENCHMARKS = ['ifeval','ifbench','gpqa_diamond','aime2025','math_hard','mmlu_pro','mbpp','livecodebench','humaneval']
EN_DOMAIN = ['영어추론','영어전문지식','영어지시이행도','영어수학','영어코딩']
# EN_BENCHMARKS = ['ifeval','ifbench','gpqa_diamond','aime2025','math_hard','mmlu_pro','mbpp','humaneval']
# EN_DOMAIN = ['영어추론','영어지시이행도','영어수학','영어전문지식']




# 문제 수 기반 가중평균(정답수 합 / 총 문항수)
DOMAIN_TO_BENCHMARKS = {
    ## 한국어 지표
    'joon': ['BFCL','FunctionChat','NESTFul'],

    '한국어이해': ['k_pragmatics','ko_sovereign_language_literature','kobalt700','click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],

    '한국어생성': ['ko_comprehensivegen_golden','ko_commongenv2'],

    '한국어추론': ['ko_winogrande','hrmcr'],

    '한국사회문화': ['k_referential','ko_sovereign_culture_folklore','ko_sovereign_society','click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],

    '한국전문지식': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography'],

    '한국어지시이행도': ['ko_ifeval'],

    '한국어수학': ['hrm8k','aime2025_ko'],
    

    'ko_sovereign_한국사회문화': ['ko_sovereign_culture_folklore', 'ko_sovereign_society'],
    'ko_sovereign_한국전문지식': ['ko_sovereign_history', 'ko_sovereign_law', 'ko_sovereign_economics_finance', 'ko_sovereign_politics', 'ko_sovereign_education', 'ko_sovereign_geography'],
    'click_언어': ['click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],
    'click_문화': ['click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],

    'click_economy':['click_economy_kedu','click_economy_kiip'],
    'click_functional':['click_functional_csat','click_functional_kedu','click_functional_pse'],
    'click_geography':['click_geography_csat','click_geography_kedu','click_geography_kiip'],
    'click_grammar':['click_grammar_csat','click_grammar_kedu','click_grammar_topik'],
    'click_history':['click_history_kedu','click_history_khb','click_history_pse'],
    'click_law':['click_law_kiip','click_law_psat'],
    'click_politics':['click_politics_kedu','click_politics_kiip'],
    'click_popular':['click_popular_kiip','click_popular_kedu'],
    'click_society':['click_society_kedu','click_society_kiip'],
    'click_textual':['click_textual_csat','click_textual_topik'],
    'click_tradition':['click_tradition_kedu','click_tradition_kiip'],
    

    'KMMLU_Applied_Science': ['kmmlu_aviation_engineering_and_maintenance','kmmlu_electronics_engineering','kmmlu_energy_management','kmmlu_environmental_science','kmmlu_gas_technology_and_engineering','kmmlu_geomatics','kmmlu_industrial_engineer','kmmlu_machine_design_and_manufacturing','kmmlu_maritime_engineering','kmmlu_nondestructive_testing','kmmlu_railway_and_automotive_engineering','kmmlu_refrigerating_machinery','kmmlu_telecommunications_and_wireless_technology'],

    'KMMLU_HUMSS': ['kmmlu_accounting','kmmlu_criminal_law','kmmlu_economics','kmmlu_education','kmmlu_korean_history','kmmlu_management','kmmlu_political_science_and_sociology','kmmlu_psychology'],

    'KMMLU_Other': ['kmmlu_agricultural_sciences','kmmlu_construction','kmmlu_fashion','kmmlu_food_processing','kmmlu_health','kmmlu_interior_architecture_and_design','kmmlu_law','kmmlu_marketing','kmmlu_patent','kmmlu_public_safety','kmmlu_real_estate','kmmlu_social_welfare','kmmlu_taxation'],

    'KMMLU_STEM': ['kmmlu_biology','kmmlu_chemical_engineering','kmmlu_chemistry','kmmlu_civil_engineering','kmmlu_computer_science','kmmlu_ecology','kmmlu_electrical_engineering','kmmlu_information_technology','kmmlu_materials_engineering','kmmlu_math','kmmlu_mechanical_engineering'],

    ## 영어 지표
    '영어추론': ['gpqa_diamond'],
    '영어전문지식': ['mmlu_pro'],
    '영어지시이행도': ['ifeval','ifbench'],
    '영어수학': ['aime2025','math_hard'],
    '영어코딩': ['humaneval','mbpp','livecodebench'],
}


# 단순 평균 값
DOMAIN_AVERAGE = {
    # 'joon': ['ifeval','ifbench','gpqa_diamond'],

    '한국어이해': ['k_pragmatics','ko_sovereign_language_literature','kobalt700','click_언어'],
    '한국어생성': ['ko_comprehensivegen_golden','ko_commongenv2'],
    '한국어추론': ['ko_winogrande','hrmcr'],
    '한국사회문화': ['k_referential','ko_sovereign_한국사회문화','click_문화'],
    '한국전문지식': ['kmmlu','ko_sovereign_한국전문지식'],
    '한국어수학': ['hrm8k','aime2025_ko'],

    '영어추론': ['gpqa_diamond'],
    '영어전문지식': ['mmlu_pro'],
    '영어수학': ['aime2025','math_hard'],
    '영어코딩': ['humaneval','mbpp','livecodebench'],
    '영어지시이행도': ['ifeval','ifbench'],
}