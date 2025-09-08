# BENCHMARKS = ['kmmlu', 'mmlu_pro','ko_sovereign','Ko-ComprehensiveGen','kobest','ko-winogrande','kpragmatics','KoIFEval']
# DOMAIN = ['한국어이해-CKP','한국어생성-CKP','한국어추론-CKP','한국사회문화-CKP','한국전문지식-CKP','한국어지시이행도-CKP','kobest_한국어이해','kobest_한국어추론','ko_sovereign_한국사회문화','ko_sovereign_한국전문지식']
# DOMAIN_NEW = ['KMMLU_Applied_Science','KMMLU_HUMSS','KMMLU_Other','KMMLU_STEM']

BENCHMARKS = ['법률문서해석', '법률지식_QA', '법률추론', '수학', '한국어생성', '한국어이해', '한국어전문지식', '한국어추론','kbl_knowledge_em', 'kbl_reasoning', 'KoIFEval']
DOMAIN = []

DOMAIN_NEW = []



DOMAIN_TO_BENCHMARKS = {

}
DOMAIN_TO_BENCHMARKS_NEW = {

}

DOMAIN_TO_BENCHMARKS_AVERAGE = {
    '법률문서해석': ['kolbench_dq'],
    '법률지식_QA': [
        'kbl_common_legal_mistake_qa_em',
        'kbl_common_legal_mistake_qa_reasoning_em',
        'kbl_legal_concept_qa_em',
        'kbl_offense_component_qa_em',
        'kbl_query_and_statute_matching_qa_em',
        'kbl_statute_hallucination_qa_em',
        'kbl_statute_number_and_content_matching_qa_em',
        'kmmlu_criminal_law',
        'kmmlu_law',
        'kmmlu_pro',
        'ko_sovereign_law',
        'kolbench_qa'
    ],
    '법률추론': [
        'kbl_case_relevance_qa_p_em',
        'kbl_case_relevance_qa_q_em',
        'kbl_causal_reasoning_qa_em',
        'kbl_statement_consistency_qa_em',
        'kolbench_reason'
    ],
    '수학': ['gsm8k'],
    '한국어생성': ['ko_comprehensivegen'],
    '한국어이해': [
        'k_honorifics',
        'k_implicature',
        'k_lexicon',
        'kobalt_700'
    ],
    '한국어전문지식': [
        'ko_sovereign_culture_folklore',
        'ko_sovereign_economics_finance',
        'ko_sovereign_education',
        'ko_sovereign_geography',
        'ko_sovereign_history',
        'ko_sovereign_language_literature',
        'ko_sovereign_politics',
        'ko_sovereign_society'
    ],
    '한국어추론': ['ko-winogrande'],
    'KoIFEval': [
        'KoIFEval_illa',
        'KoIFEval_ilsa',
        'KoIFEval_plla',
        'KoIFEval_plsa'
    ]
}
GROUPED_RAW_CATEGORIES = {


    }


HIERARCHY = {
    "법률지식_QA": {
        "kmmlu": ["kmmlu_law", "kmmlu_criminal_law"],
        "kmmlu_pro": ["kmmlu_pro"],
        "ko_sovereign": ["ko_sovereign_law"],
        "kolbench": ["kolbench_qa"],
        "kbl_knowledge_em": ['kbl_common_legal_mistake_qa_em','kbl_common_legal_mistake_qa_reasoning_em','kbl_legal_concept_qa_em','kbl_offense_component_qa_em','kbl_query_and_statute_matching_qa_em','kbl_statute_hallucination_qa_em','kbl_statute_number_and_content_matching_qa_em']
    },
    "법률추론": {
        "kbl-reasoning": ['kbl_case_relevance_qa_p_em','kbl_case_relevance_qa_q_em','kbl_causal_reasoning_qa_em','kbl_statement_consistency_qa_em'],
        "kolbench": ["kolbench_reason"],
    },
    "법률문서해석": {
        "kolbench": ["kolbench_dq"],
    },
    "KoIFEval": {
        'KoIFEval':['KoIFEval_illa','KoIFEval_ilsa','KoIFEval_plla','KoIFEval_plsa']
        # 'KoIFEval':['KoIFEval_ilsa','KoIFEval_plla']
    },
    "한국어이해": {
        "kpragmatics": ["k_honorifics", "k_implicature",'k_lexicon'],
        "kobalt_700": ["kobalt_700"]
    },
    "한국어생성": {
        "ko_comprehensivegen": ['ko_comprehensivegen'],
    },
    "한국어추론": {
        "ko-winogrande": ['ko-winogrande'],
    },
    
    "한국어전문지식": {
        'ko_sovereign':['ko_sovereign_culture_folklore','ko_sovereign_education','ko_sovereign_geography','ko_sovereign_history','ko_sovereign_language_literature','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_society']
    },
    "수학": {
        'gsm8k':['gsm8k'],
    }
}