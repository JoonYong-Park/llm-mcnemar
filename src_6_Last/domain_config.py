## 한국어 벤치마크
KOR_BENCHMARKS = ['k_referential','k_referential_hard','kmmlu','ko_sovereign','kobest','ko_comprehensivegen','ko_comprehensivegen_hard','ko_ifeval','ko_winogrande','k_pragmatics','k_pragmatics_hard','click','haerae','ko_commongenv2','kobalt700','hrmcr']
KOR_DOMAIN = ['한국어이해','한국어생성','한국어추론','한국사회문화','한국전문지식','한국어지시이행도','kobest_한국어이해','kobest_한국어추론','ko_sovereign_한국사회문화','ko_sovereign_한국전문지식','click_언어','click_문화','KMMLU_Applied_Science','KMMLU_HUMSS','KMMLU_Other','KMMLU_STEM']

## 영어 벤치마크
EN_BENCHMARKS = ['musr','gpqa','winogrande','bbh','mmlu_pro','ifeval','gsm8k','math','aqua_rat','aime2025','mbpp','livecodebench','humaneval']
EN_DOMAIN = ['영어추론','영어전문지식','영어지시이행도','영어수학','영어코딩']

## 법률 벤치마크
LAW_BENCHMARKS = ['gsm8k','k_pragmatics','kbl_knowledge_em','kbl_reasoning','kmmlu','kmmlu_pro','ko_comprehensivegen','ko_ifeval','ko_sovereign','ko_winogrande','kobalt_700','kolbench']
LAW_DOMAIN = ['법률지식QA','법률추론','법률문서해석','한국어지시이행도','한국어이해_법률','한국어생성_법률','한국어추론_법률','한국전문지식_법률','수학_법률']

## 금융 벤치마크
FINANCE_BENCHMARKS = ['kmmlu','mmlu_pro','ko_sovereign','korfin','gsm8k','math','ko_comprehensivegen','ko_ifeval','docmath_eval','k_pragmatics','ko_winogrande']
FINANCE_DOMAIN = ['금융지식QA','금융추론','수학_금융','테이블문서기반QA','한국어생성_금융','한국어추론_금융','한국전문지식_금융','한국어지시이행도']


## 카테고리 영역 필요한 벤치마크
CATEGORY_BENCHMARKS = ['kmmlu', 'ko_sovereign', 'kobest', 'k_pragmatics', 'k_pragmatics_hard', 'ko_ifeval','click', 'haerae', 'hrm8k', 'korean_national_civil_service', 'hrmcr','bbh', 'gpqa', 'ifeval', 'math', 'mmlu_pro', 'musr', 'kbl_knowledge_em', 'kbl_reasoning', 'kolbench', 'korfin']


DOMAIN_TO_BENCHMARKS = {
    '법률지식QA': ['kmmlu_law','kmmlu_criminal_law','kmmlu_pro','ko_sovereign_law','kolbench_qa','kbl_knowledge_em'],
    '법률추론': ['kbl_reasoning','kolbench_reason'],
    '법률문서해석': ['kolbench_dq'],
    '한국어이해_법률': ['k_pragmatics','kobalt_700'],
    '한국어생성_법률': ['ko_comprehensivegen'],
    '한국어추론_법률': ['ko_winogrande'],
    '한국전문지식_법률': ['ko_sovereign_economics_finance','ko_sovereign_education','ko_sovereign_culture_folklore','ko_sovereign_society','ko_sovereign_language_literature','ko_sovereign_history','ko_sovereign_politics','ko_sovereign_geography'],
    '수학_법률': ['gsm8k'],

    '금융지식QA': ['kmmlu_accounting','kmmlu_economics','mmlu_pro_economics','ko_sovereign_economics_finance','korfin_qa'],
    '금융추론': ['korfin_asc','korfin_reason'],
    '테이블문서기반QA': ['docmatheval','korfin_dq'],
    '한국어생성_금융': ['ko_comprehensivegen'],
    '한국어추론_금융': ['ko_winogrande'],
    '한국전문지식_금융': ['ko_sovereign_education','ko_sovereign_culture_folklore','ko_sovereign_law','ko_sovereign_society','ko_sovereign_language_literature','ko_sovereign_history','ko_sovereign_politics','ko_sovereign_geography'],
    '수학_금융': ['gsm8k','math'],


    '영어추론': ['musr','gpqa','winogrande','bbh'],
    '영어전문지식': ['mmlu_pro'],
    '영어지시이행도': ['ifeval'],
    '영어수학': ['gsm8k','math','aqua_rat','aime2025'],
    '영어코딩': ['humaneval','mbpp','livecodebench'],


    '한국어이해': ['k_pragmatics','kobest_boolq','kobest_sentineg','ko_sovereign_language_literature','kobalt700','click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],

    '한국어생성': ['ko_comprehensivegen','ko_commongenv2'],

    '한국어추론': ['ko_winogrande','kobest_copa','kobest_hellaswag','kobest_wic','hrmcr'],

    '한국사회문화': ['k_referential','ko_sovereign_culture_folklore','ko_sovereign_society','haerae','click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],

    '한국전문지식': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography'],

    '한국어지시이행도': ['ko_ifeval'],

    '한국어수학': ['hrm8k'],
    
    'kobest_한국어이해': ['kobest_boolq', 'kobest_sentineg'],
    'kobest_한국어추론': ['kobest_copa', 'kobest_hellaswag', 'kobest_wic'],
    'ko_sovereign_한국사회문화': ['ko_sovereign_culture_folklore', 'ko_sovereign_society'],
    'ko_sovereign_한국전문지식': ['ko_sovereign_history', 'ko_sovereign_law', 'ko_sovereign_economics_finance', 'ko_sovereign_politics', 'ko_sovereign_education', 'ko_sovereign_geography'],
    'click_언어': ['click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],
    'click_문화': ['click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],
    
    

    'KMMLU_Applied_Science': ['kmmlu_aviation_engineering_and_maintenance','kmmlu_electronics_engineering','kmmlu_energy_management','kmmlu_environmental_science','kmmlu_gas_technology_and_engineering','kmmlu_geomatics','kmmlu_industrial_engineer','kmmlu_machine_design_and_manufacturing','kmmlu_maritime_engineering','kmmlu_nondestructive_testing','kmmlu_railway_and_automotive_engineering','kmmlu_refrigerating_machinery','kmmlu_telecommunications_and_wireless_technology'],

    'KMMLU_HUMSS': ['kmmlu_accounting','kmmlu_criminal_law','kmmlu_economics','kmmlu_education','kmmlu_korean_history','kmmlu_management','kmmlu_political_science_and_sociology','kmmlu_psychology'],

    'KMMLU_Other': ['kmmlu_agricultural_sciences','kmmlu_construction','kmmlu_fashion','kmmlu_food_processing','kmmlu_health','kmmlu_interior_architecture_and_design','kmmlu_law','kmmlu_marketing','kmmlu_patent','kmmlu_public_safety','kmmlu_real_estate','kmmlu_social_welfare','kmmlu_taxation'],

    'KMMLU_STEM': ['kmmlu_biology','kmmlu_chemical_engineering','kmmlu_chemistry','kmmlu_civil_engineering','kmmlu_computer_science','kmmlu_ecology','kmmlu_electrical_engineering','kmmlu_information_technology','kmmlu_materials_engineering','kmmlu_math','kmmlu_mechanical_engineering'],

    '한국어문법_및_맥락_이해': ['ko_sovereign_language_literature',
                      'K-Honorifics-hard','K-Lexicon-hard','Ko-ComprehensiveGen-hard',
                      'kobest_copa','kobest_hellaswag','kobest_wic',
                      'KoIFEval',
                      'ko-winogrande'],

    '한국문화_및_상징_이해': ['ko_sovereign_culture_folklore','ko_sovereign_society',
                     'K-Implicature-hard','k_referential_hard',
                     'korean_naturalization',
                     'kmmlu_fashion','kmmlu_interior_architecture_and_design'],

    '한국_사회제도_및_구조_이해': 
    ['ko_sovereign_society','ko_sovereign_economics_finance','ko_sovereign_law','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography',
     'kobest_boolq',
     'kmmlu_accounting','kmmlu_criminal_law','kmmlu_economics','kmmlu_law','kmmlu_taxation','kmmlu_education','kmmlu_management','kmmlu_marketing','kmmlu_patent','kmmlu_political_science_and_sociology','kmmlu_public_safety','kmmlu_geomatics',
     'korean_national_civil_service_law','korean_national_civil_service_education'],

     '한국정서_및_암묵규범_이해': ['ko_sovereign_society',
                     'kobest_sentineg',
                     'kmmlu_social_welfare','kmmlu_psychology'],

     '한국사': 
     ['ko_sovereign_history',
      'korean_national_civil_service_historical_sources','korean_national_civil_service_Joseon','korean_national_civil_service_modern_contemporary','korean_national_civil_service_prehistoric_goryeo',
      'kmmlu_korean_history'],
      
     '사회적이슈': 
     ['ko_sovereign_politics',
      'korean_national_civil_service_education',
      'kmmlu_social_welfare','kmmlu_real_estate'],


    '한국어이해-CKP': ['kpragmatics_hard','kobest_boolq','kobest_sentineg','ko_sovereign_language_literature'],
    '한국어생성-CKP': ['Ko-ComprehensiveGen-hard'],
    '한국어지시이행도-CKP': ['KoIFEval'],
    '한국어추론-CKP': ['ko-winogrande','kobest_copa','kobest_hellaswag','kobest_wic'],
    '한국사회문화-CKP': ['k_referential_hard','ko_sovereign_culture_folklore','ko_sovereign_society'],
    '한국전문지식-CKP': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography','korean_national_civil_service','korean_naturalization'],
}

DOMAIN_AVERAGE = {
    '한국어이해': ['k_pragmatics','kobest_한국어이해','ko_sovereign_language_literature','kobalt700','click_언어'],
    '한국어생성': ['ko_comprehensivegen','ko_commongenv2'],
    '한국어추론': ['ko_winogrande','kobest_한국어추론','hrmcr'],
    '한국사회문화': ['k_referential','ko_sovereign_한국사회문화','haerae','click_문화'],
    '한국전문지식': ['kmmlu','ko_sovereign_한국전문지식'],
    '한국어수학': ['hrm8k'],

    '영어추론': ['musr','gpqa','winogrande','bbh'],
    '영어전문지식': ['mmlu_pro'],
    '영어수학': ['gsm8k','math','aqua_rat','aime2025'],
    '영어코딩': ['humaneval','mbpp','livecodebench'],

    '법률지식QA': ['kmmlu','kmmlu_pro','ko_sovereign_law','kolbench_qa','kbl_knowledge_em'],
    '법률추론': ['kbl_reasoning','kolbench_reason'],
    '법률문서해석': ['kolbench_dq'],
    '한국어이해_법률': ['k_pragmatics','kobalt_700'],
    '한국어생성_법률': ['ko_comprehensivegen'],
    '한국어추론_법률': ['ko_winogrande'],
    '한국전문지식_법률': ['ko_sovereign_economics_finance','ko_sovereign_education','ko_sovereign_culture_folklore','ko_sovereign_society','ko_sovereign_language_literature','ko_sovereign_history','ko_sovereign_politics','ko_sovereign_geography'],
    '수학_법률': ['gsm8k'],

    '금융지식QA': ['kmmlu','mmlu_pro_economics','ko_sovereign_economics_finance','korfin_qa'],
    '금융추론': ['korfin_asc','korfin_reason'],
    '테이블문서기반QA': ['docmatheval','korfin_dq'],
    '한국어생성_금융': ['ko_comprehensivegen'],
    '한국어추론_금융': ['ko_winogrande'],
    '한국전문지식_금융': ['ko_sovereign_education','ko_sovereign_culture_folklore','ko_sovereign_law','ko_sovereign_society','ko_sovereign_language_literature','ko_sovereign_history','ko_sovereign_politics','ko_sovereign_geography'],
    '수학_금융': ['gsm8k','math'],
}