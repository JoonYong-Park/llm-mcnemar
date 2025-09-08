BENCHMARKS = ['k_referential','k_referential_hard','kmmlu','ko_sovereign','kobest','Ko-ComprehensiveGen','Ko-ComprehensiveGen-hard','KoIFEval','korean_national_civil_service','korean_naturalization','ko-winogrande','kpragmatics','kpragmatics_hard','click','haerae','hrm8k','ko_commongenv2','kobalt700']
DOMAIN = ['한국어이해','한국어생성','한국어추론','한국사회문화','한국전문지식','한국어지시이행도','kobest_한국어이해','kobest_한국어추론','ko_sovereign_한국사회문화','한국어수학','ko_sovereign_한국전문지식','click_언어','click_문화']
DOMAIN_NEW = ['KMMLU_Applied_Science','KMMLU_HUMSS','KMMLU_Other','KMMLU_STEM']


BENCHMARKS_LIST = ['k_referential','k_referential_hard','kmmlu','ko_sovereign','kobest','Ko-ComprehensiveGen','Ko-ComprehensiveGen-hard','Ko-GSM8K','KoIFEval','korean_national_civil_service','korean_naturalization','ko-winogrande','kpragmatics','kpragmatics_hard']

DOMAIN_TO_BENCHMARKS = {
    '한국어이해': ['kpragmatics','kobest_boolq','kobest_sentineg','ko_sovereign_language_literature','kobalt700','click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],

    '한국어생성': ['Ko-ComprehensiveGen','ko_commongenv2'],

    '한국어추론': ['ko-winogrande','kobest_copa','kobest_hellaswag','kobest_wic'],

    '한국사회문화': ['k_referential','ko_sovereign_culture_folklore','ko_sovereign_society','haerae','click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],

    '한국전문지식': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography','korean_national_civil_service','korean_naturalization'],

    '한국어지시이행도': ['KoIFEval'],

    '한국어수학': ['hrm8k'],
    
    'kobest_한국어이해': ['kobest_boolq', 'kobest_sentineg'],
    'kobest_한국어추론': ['kobest_copa', 'kobest_hellaswag', 'kobest_wic'],
    'ko_sovereign_한국사회문화': ['ko_sovereign_culture_folklore', 'ko_sovereign_society'],
    'ko_sovereign_한국전문지식': ['ko_sovereign_history', 'ko_sovereign_law', 'ko_sovereign_economics_finance', 'ko_sovereign_politics', 'ko_sovereign_education', 'ko_sovereign_geography'],
    'click_언어': ['click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],
    'click_문화': ['click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],
    
    

    

    '한국어이해-CKP': ['kpragmatics_hard','kobest_boolq','kobest_sentineg','ko_sovereign_language_literature'],
    '한국어생성-CKP': ['Ko-ComprehensiveGen-hard'],
    '한국어지시이행도-CKP': ['KoIFEval'],
    '한국어추론-CKP': ['ko-winogrande','kobest_copa','kobest_hellaswag','kobest_wic'],
    '한국사회문화-CKP': ['k_referential_hard','ko_sovereign_culture_folklore','ko_sovereign_society'],
    '한국전문지식-CKP': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography','korean_national_civil_service','korean_naturalization'],
}
DOMAIN_TO_BENCHMARKS_NEW = {
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
}

DOMAIN_TO_BENCHMARKS_AVERAGE = {
    '한국어이해': ['kpragmatics','kobest_한국어이해','ko_sovereign_language_literature','kobalt700','click_언어'],
    '한국어생성': ['Ko-ComprehensiveGen','ko_commongenv2'],
    '한국어추론': ['ko-winogrande','kobest_한국어추론'],
    '한국사회문화': ['k_referential','ko_sovereign_한국사회문화'],
    '한국전문지식': ['kmmlu','ko_sovereign_한국전문지식','click_문화','haerae','korean_national_civil_service','korean_naturalization'],
    '한국어수학': ['hrm8k'],
    # '한국어지시이행도': ['KoIFEval_illa','KoIFEval_ilsa','KoIFEval_plla','KoIFEval_plsa'],
    '한국어지시이행도': ['KoIFEval_ilsa','KoIFEval_plla'],
}
GROUPED_RAW_CATEGORIES = {
        'kobest_한국어이해': ['kobest_boolq', 'kobest_sentineg'],
        'kobest_한국어추론': ['kobest_copa', 'kobest_hellaswag', 'kobest_wic'],
        'ko_sovereign_한국사회문화': ['ko_sovereign_culture_folklore', 'ko_sovereign_society'],
        'ko_sovereign_한국전문지식': [
            'ko_sovereign_history', 'ko_sovereign_law', 'ko_sovereign_economics_finance',
            'ko_sovereign_politics', 'ko_sovereign_education', 'ko_sovereign_geography'
        ],
        'click_언어': [
            'click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'
        ],
        'click_문화': [
            'click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'
        ],
        'KMMLU_Applied_Science': ['kmmlu_aviation_engineering_and_maintenance','kmmlu_electronics_engineering','kmmlu_energy_management','kmmlu_environmental_science','kmmlu_gas_technology_and_engineering','kmmlu_geomatics','kmmlu_industrial_engineer','kmmlu_machine_design_and_manufacturing','kmmlu_maritime_engineering','kmmlu_nondestructive_testing','kmmlu_railway_and_automotive_engineering','kmmlu_refrigerating_machinery','kmmlu_telecommunications_and_wireless_technology'],

        'KMMLU_HUMSS': ['kmmlu_accounting','kmmlu_criminal_law','kmmlu_economics','kmmlu_education','kmmlu_korean_history','kmmlu_management','kmmlu_political_science_and_sociology','kmmlu_psychology'],

        'KMMLU_Other': ['kmmlu_agricultural_sciences','kmmlu_construction','kmmlu_fashion','kmmlu_food_processing','kmmlu_health','kmmlu_interior_architecture_and_design','kmmlu_law','kmmlu_marketing','kmmlu_patent','kmmlu_public_safety','kmmlu_real_estate','kmmlu_social_welfare','kmmlu_taxation'],

        'KMMLU_STEM': ['kmmlu_biology','kmmlu_chemical_engineering','kmmlu_chemistry','kmmlu_civil_engineering','kmmlu_computer_science','kmmlu_ecology','kmmlu_electrical_engineering','kmmlu_information_technology','kmmlu_materials_engineering','kmmlu_math','kmmlu_mechanical_engineering'],
    }


HIERARCHY = {
    "KMMLU": {
        'KMMLU_Applied_Science': ['KMMLU_Applied_Science','kmmlu_aviation_engineering_and_maintenance','kmmlu_electronics_engineering','kmmlu_energy_management','kmmlu_environmental_science','kmmlu_gas_technology_and_engineering','kmmlu_geomatics','kmmlu_industrial_engineer','kmmlu_machine_design_and_manufacturing','kmmlu_maritime_engineering','kmmlu_nondestructive_testing','kmmlu_railway_and_automotive_engineering','kmmlu_refrigerating_machinery','kmmlu_telecommunications_and_wireless_technology'],

        'KMMLU_HUMSS': ['KMMLU_HUMSS','kmmlu_accounting','kmmlu_criminal_law','kmmlu_economics','kmmlu_education','kmmlu_korean_history','kmmlu_management','kmmlu_political_science_and_sociology','kmmlu_psychology'],

        'KMMLU_Other': ['KMMLU_Other','kmmlu_agricultural_sciences','kmmlu_construction','kmmlu_fashion','kmmlu_food_processing','kmmlu_health','kmmlu_interior_architecture_and_design','kmmlu_law','kmmlu_marketing','kmmlu_patent','kmmlu_public_safety','kmmlu_real_estate','kmmlu_social_welfare','kmmlu_taxation'],

        'KMMLU_STEM': ['KMMLU_STEM','kmmlu_biology','kmmlu_chemical_engineering','kmmlu_chemistry','kmmlu_civil_engineering','kmmlu_computer_science','kmmlu_ecology','kmmlu_electrical_engineering','kmmlu_information_technology','kmmlu_materials_engineering','kmmlu_math','kmmlu_mechanical_engineering'],

        'KMMLU': ['kmmlu'],
        
    },
    "KT_NEW_BENCHMARK": {
        "kpragmatics": ["k_honorifics", "k_implicature",'k_lexicon','kpragmatics'],
        "kpragmatics_hard": ["K-Honorifics-hard", "K-Implicature-hard",'K-Lexicon-hard','kpragmatics_hard'],
        "Ko-ComprehensiveGen": ['Ko-ComprehensiveGen'],
        "Ko-ComprehensiveGen-hard": ['Ko-ComprehensiveGen-hard'],
        "k_referential": ['k_referential'],
        "k_referential_hard": ['k_referential_hard']
    },
    "KoIFEval": {
        'KoIFEval':['KoIFEval_illa','KoIFEval_ilsa','KoIFEval_plla','KoIFEval_plsa']
        # 'KoIFEval':['KoIFEval_ilsa','KoIFEval_plla']
    },
    "ko_sovereign": {
        'ko_sovereign':['ko_sovereign','ko_sovereign_culture_folklore','ko_sovereign_economics_finance','ko_sovereign_education','ko_sovereign_geography','ko_sovereign_history','ko_sovereign_language_literature','ko_sovereign_law','ko_sovereign_politics','ko_sovereign_society']
    },
    "kobest": {
        'kobest':['kobest','kobest_boolq','kobest_copa','kobest_hellaswag','kobest_sentineg','kobest_wic']
    },
    "click": {
        'click_언어':['click_functional_csat','click_functional_kedu','click_functional_pse','click_grammar_csat','click_grammar_kedu','click_grammar_topik','click_textual_csat','click_textual_topik'],
        'click_문화':['click_economy_kedu','click_economy_kiip','click_geography_csat','click_geography_kedu','click_geography_kiip','click_history_kedu','click_history_khb','click_history_pse','click_law_kiip','click_law_psat','click_politics_kedu','click_politics_kiip','click_popular_kiip','click_popular_kedu','click_society_kedu','click_society_kiip','click_tradition_kedu','click_tradition_kiip'],
    },
    "haerae": {
        'haerae':['haerae','haerae_correct_definition_matching','haerae_csat_geo','haerae_csat_law','haerae_csat_socio','haerae_date_understanding','haerae_general_knowledge','haerae_history','haerae_loan_words','haerae_lyrics_denoising','haerae_proverbs_denoising','haerae_rare_words','haerae_reading_comprehension','haerae_standard_nomenclature']
    },
    "hrm8k": {
        'hrm8k':['hrm8k','hrm8k_gsm8k_math_verify','hrm8k_ksm_math_verify','hrm8k_math_math_verify','hrm8k_mmmlu_math_verify','hrm8k_omni_math_math_verify',]
    },
    "korean_national_civil_service": {
        'korean_national_civil_service':['korean_national_civil_service','korean_national_civil_service_education','korean_national_civil_service_historical_sources','korean_national_civil_service_Joseon','korean_national_civil_service_law','korean_national_civil_service_modern_contemporary','korean_national_civil_service_prehistoric_goryeo']
    },
}