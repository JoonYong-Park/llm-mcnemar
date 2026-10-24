# ─────────────────────────────────────────────────────────────
# Korean benchmarks
#
# Layout: data/korean/{model}/{benchmark}/samples_*_<TS>.jsonl
# ─────────────────────────────────────────────────────────────

DATA_DIR = "korean"
RESULT_SLUG = "korean_benchmarks"

BENCHMARKS = [
    'k_referential', 'k_referential_hard', 'kmmlu', 'ko_sovereign', 'kobest',
    'ko_comprehensivegen', 'ko_comprehensivegen_hard', 'ko_ifeval', 'ko_winogrande',
    'k_pragmatics', 'k_pragmatics_hard', 'click', 'haerae', 'ko_commongenv2',
    'kobalt700', 'hrmcr',
]

# Benchmarks that get a per-category (sub-task) sheet
CATEGORY_BENCHMARKS = [
    'kmmlu', 'ko_sovereign', 'kobest', 'k_pragmatics', 'k_pragmatics_hard',
    'ko_ifeval', 'click', 'haerae', 'hrmcr',
]

DOMAINS = [
    'Korean Understanding', 'Korean Generation', 'Korean Reasoning',
    'Korean Society & Culture', 'Korean Expert Knowledge', 'Korean Instruction Following',
    'kobest_Understanding', 'kobest_Reasoning',
    'ko_sovereign_Society & Culture', 'ko_sovereign_Expert Knowledge',
    'click_Language', 'click_Culture',
    'KMMLU_Applied_Science', 'KMMLU_HUMSS', 'KMMLU_Other', 'KMMLU_STEM',
]

_CLICK_LANGUAGE = [
    'click_functional_csat', 'click_functional_kedu', 'click_functional_pse',
    'click_grammar_csat', 'click_grammar_kedu', 'click_grammar_topik',
    'click_textual_csat', 'click_textual_topik',
]
_CLICK_CULTURE = [
    'click_economy_kedu', 'click_economy_kiip', 'click_geography_csat', 'click_geography_kedu',
    'click_geography_kiip', 'click_history_kedu', 'click_history_khb', 'click_history_pse',
    'click_law_kiip', 'click_law_psat', 'click_politics_kedu', 'click_politics_kiip',
    'click_popular_kiip', 'click_popular_kedu', 'click_society_kedu', 'click_society_kiip',
    'click_tradition_kedu', 'click_tradition_kiip',
]
_KO_SOVEREIGN_SOCIETY = ['ko_sovereign_culture_folklore', 'ko_sovereign_society']
_KO_SOVEREIGN_EXPERT = [
    'ko_sovereign_history', 'ko_sovereign_law', 'ko_sovereign_economics_finance',
    'ko_sovereign_politics', 'ko_sovereign_education', 'ko_sovereign_geography',
]

# Domain -> benchmarks/categories (question-weighted; used for domain_mcnemar)
DOMAIN_TO_BENCHMARKS = {
    'Korean Understanding': ['k_pragmatics', 'kobest_boolq', 'kobest_sentineg', 'ko_sovereign_language_literature',
                 'kobalt700', *_CLICK_LANGUAGE],
    'Korean Generation': ['ko_comprehensivegen', 'ko_commongenv2'],
    'Korean Reasoning': ['ko_winogrande', 'kobest_copa', 'kobest_hellaswag', 'kobest_wic', 'hrmcr'],
    'Korean Society & Culture': ['k_referential', *_KO_SOVEREIGN_SOCIETY, 'haerae', *_CLICK_CULTURE],
    'Korean Expert Knowledge': ['kmmlu', *_KO_SOVEREIGN_EXPERT],
    'Korean Instruction Following': ['ko_ifeval'],

    'kobest_Understanding': ['kobest_boolq', 'kobest_sentineg'],
    'kobest_Reasoning': ['kobest_copa', 'kobest_hellaswag', 'kobest_wic'],
    'ko_sovereign_Society & Culture': _KO_SOVEREIGN_SOCIETY,
    'ko_sovereign_Expert Knowledge': _KO_SOVEREIGN_EXPERT,
    'click_Language': _CLICK_LANGUAGE,
    'click_Culture': _CLICK_CULTURE,

    'KMMLU_Applied_Science': [
        'kmmlu_aviation_engineering_and_maintenance', 'kmmlu_electronics_engineering',
        'kmmlu_energy_management', 'kmmlu_environmental_science',
        'kmmlu_gas_technology_and_engineering', 'kmmlu_geomatics', 'kmmlu_industrial_engineer',
        'kmmlu_machine_design_and_manufacturing', 'kmmlu_maritime_engineering',
        'kmmlu_nondestructive_testing', 'kmmlu_railway_and_automotive_engineering',
        'kmmlu_refrigerating_machinery', 'kmmlu_telecommunications_and_wireless_technology',
    ],
    'KMMLU_HUMSS': [
        'kmmlu_accounting', 'kmmlu_criminal_law', 'kmmlu_economics', 'kmmlu_education',
        'kmmlu_korean_history', 'kmmlu_management', 'kmmlu_political_science_and_sociology',
        'kmmlu_psychology',
    ],
    'KMMLU_Other': [
        'kmmlu_agricultural_sciences', 'kmmlu_construction', 'kmmlu_fashion',
        'kmmlu_food_processing', 'kmmlu_health', 'kmmlu_interior_architecture_and_design',
        'kmmlu_law', 'kmmlu_marketing', 'kmmlu_patent', 'kmmlu_public_safety',
        'kmmlu_real_estate', 'kmmlu_social_welfare', 'kmmlu_taxation',
    ],
    'KMMLU_STEM': [
        'kmmlu_biology', 'kmmlu_chemical_engineering', 'kmmlu_chemistry',
        'kmmlu_civil_engineering', 'kmmlu_computer_science', 'kmmlu_ecology',
        'kmmlu_electrical_engineering', 'kmmlu_information_technology',
        'kmmlu_materials_engineering', 'kmmlu_math', 'kmmlu_mechanical_engineering',
    ],
}

# Domains whose accuracy is the simple mean of sub-item scores instead of question-weighted
# (sub-items can be benchmarks, categories or domains above)
DOMAIN_AVERAGE = {
    'Korean Understanding': ['k_pragmatics', 'kobest_Understanding', 'ko_sovereign_language_literature', 'kobalt700', 'click_Language'],
    'Korean Generation': ['ko_comprehensivegen', 'ko_commongenv2'],
    'Korean Reasoning': ['ko_winogrande', 'kobest_Reasoning', 'hrmcr'],
    'Korean Society & Culture': ['k_referential', 'ko_sovereign_Society & Culture', 'haerae', 'click_Culture'],
    'Korean Expert Knowledge': ['kmmlu', 'ko_sovereign_Expert Knowledge'],
    'Korean Instruction Following': ['ko_ifeval'],
}
