## 한국어 벤치마크 (midm-300-pro-super-cpt-260722 vs Solar-Open-2-250B-A15B-0)
# 4개 벤치: k_pragmatics / k_referential / ko_comprehensivegen_golden / ko_sovereign

KOR_BENCHMARKS = [
    'k_pragmatics',
    'k_referential',
    'ko_comprehensivegen_golden',
    'ko_sovereign',
]

KOR_DOMAIN = [
    '한국어이해',
    '한국어생성',
    '한국사회문화',
    '한국전문지식',
    'ko_sovereign_한국사회문화',
    'ko_sovereign_한국전문지식',
    'ko_sovereign_한국언어문학',
]

## 카테고리 영역 필요한 벤치마크
CATEGORY_BENCHMARKS = [
    'k_pragmatics',
    'ko_sovereign',
]

####################################

## 영어 벤치마크 (미사용)
EN_BENCHMARKS = []
EN_DOMAIN = []

# 문제 수 기반 가중평균(정답수 합 / 총 문항수)
DOMAIN_TO_BENCHMARKS = {
    '한국어이해': [
        'k_pragmatics',
        'ko_sovereign_language_literature',
    ],
    '한국어생성': [
        'ko_comprehensivegen_golden',
    ],
    '한국사회문화': [
        'k_referential',
        'ko_sovereign_culture_folklore',
        'ko_sovereign_society',
    ],
    '한국전문지식': [
        'ko_sovereign_history',
        'ko_sovereign_law',
        'ko_sovereign_economics_finance',
        'ko_sovereign_politics',
        'ko_sovereign_education',
        'ko_sovereign_geography',
    ],
    'ko_sovereign_한국사회문화': [
        'ko_sovereign_culture_folklore',
        'ko_sovereign_society',
    ],
    'ko_sovereign_한국전문지식': [
        'ko_sovereign_history',
        'ko_sovereign_law',
        'ko_sovereign_economics_finance',
        'ko_sovereign_politics',
        'ko_sovereign_education',
        'ko_sovereign_geography',
    ],
    'ko_sovereign_한국언어문학': [
        'ko_sovereign_language_literature',
    ],
}

# 단순 평균 방식 지표 (법률과 동일하게 미사용 → 전부 문항수 가중평균)
DOMAIN_AVERAGE = {}
