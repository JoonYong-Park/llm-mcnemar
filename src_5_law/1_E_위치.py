import os
import shutil
from datetime import datetime

def reorganize_files_by_reference(reference_folder, target_folder, dry_run=False):
    """
    reference_folder의 구조를 참고해서 target_folder의 파일들을 올바른 위치로 이동
    """
    log_lines = []
    
    # reference_folder의 구조를 먼저 파악
    reference_structure = {}
    for root, dirs, files in os.walk(reference_folder):
        if root == reference_folder:  # 최상위 폴더는 제외
            continue
            
        relative_path = os.path.relpath(root, reference_folder)
        reference_structure[relative_path] = [f for f in files if f.endswith(('.jsonl', '.xlsx', '.json'))]
    
    print("📋 Reference 폴더 구조:")
    for folder, files in reference_structure.items():
        print(f"  {folder}: {files}")
    
    # target_folder의 모든 파일을 수집
    target_files = {}
    for root, dirs, files in os.walk(target_folder):
        if root == target_folder:  # 최상위 폴더는 제외
            continue
            
        relative_path = os.path.relpath(root, target_folder)
        target_files[relative_path] = []
        
        for file in files:
            if file.endswith(('.jsonl', '.xlsx', '.json')):
                target_files[relative_path].append(file)
    
    print("\n📋 Target 폴더 현재 구조:")
    for folder, files in target_files.items():
        print(f"  {folder}: {files}")
    
    # 파일 이동 매핑 생성
    file_mapping = {}
    
    # 각 파일이 어느 폴더에 있어야 하는지 결정
    for current_folder, files in target_files.items():
        for file in files:
            # 파일명에서 벤치마크 타입 추출
            benchmark_type = get_benchmark_type(file)
            if benchmark_type:
                target_folder_name = get_target_folder_name(benchmark_type)
                if target_folder_name:
                    source_path = os.path.join(target_folder, current_folder, file)
                    target_path = os.path.join(target_folder, target_folder_name, file)
                    file_mapping[source_path] = target_path
    
    print("\n🔄 파일 이동 계획:")
    for source, target in file_mapping.items():
        print(f"  {os.path.relpath(source, target_folder)} → {os.path.relpath(target, target_folder)}")
    
    # 파일 이동 실행
    for source_path, target_path in file_mapping.items():
        # 대상 폴더가 없으면 생성
        target_dir = os.path.dirname(target_path)
        if not os.path.exists(target_dir):
            if not dry_run:
                os.makedirs(target_dir)
            print(f'�� 폴더 생성: {target_dir}')
        
        # 파일이 이미 존재하는지 확인
        if os.path.exists(target_path):
            print(f'⚠️ 파일 이미 존재: {os.path.relpath(target_path, target_folder)}')
            continue
        
        print(f'✅ 이동: {os.path.relpath(source_path, target_folder)} → {os.path.relpath(target_path, target_folder)}')
        log_lines.append(f'{os.path.relpath(source_path, target_folder)} → {os.path.relpath(target_path, target_folder)}')
        
        if not dry_run:
            shutil.move(source_path, target_path)
    
    # 빈 폴더 정리
    for root, dirs, files in os.walk(target_folder, topdown=False):
        if root == target_folder:  # 최상위 폴더는 제외
            continue
            
        try:
            if not os.listdir(root):  # 빈 폴더인지 확인
                if not dry_run:
                    os.rmdir(root)
                print(f'��️ 빈 폴더 삭제: {os.path.relpath(root, target_folder)}')
        except OSError:
            pass  # 폴더가 비어있지 않거나 삭제할 수 없는 경우
    
    # 로그 저장
    if not dry_run and log_lines:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        log_filename = f'reorganize_log_llama-legal_{timestamp}.txt'
        
        with open(log_filename, 'w', encoding='utf-8') as f:
            for line in log_lines:
                f.write(line + '\n')
        print(f'\n📜 로그 저장 완료: {log_filename}')

def get_benchmark_type(filename):
    """파일명에서 벤치마크 타입을 추출"""
    filename_lower = filename.lower()
    
    # 법률지식_QA 관련
    if any(keyword in filename_lower for keyword in ['kmmlu', 'sovereign_law', 'kolbench_qa', 'kbl_common_legal_mistake', 'kbl_legal_concept', 'kbl_offense_component', 'kbl_query_and_statute', 'kbl_statute_hallucination', 'kbl_statute_number']):
        return 'legal_qa'
    
    # 법률추론 관련
    elif any(keyword in filename_lower for keyword in ['kbl_case_relevance', 'kbl_causal_reasoning', 'kbl_statement_consistency', 'kolbench_reason']):
        return 'legal_reasoning'
    
    # 법률문서해석 관련
    elif 'kolbench_dq' in filename_lower:
        return 'legal_doc'
    
    # 수학 관련
    elif 'gsm8k' in filename_lower:
        return 'math'
    
    # 한국어생성 관련
    elif 'comprehensivegen' in filename_lower:
        return 'korean_generation'
    
    # 한국어이해 관련
    elif any(keyword in filename_lower for keyword in ['honorifics', 'implicature', 'lexicon', 'kobalt']):
        return 'korean_understanding'
    
    # 한국어전문지식 관련
    elif any(keyword in filename_lower for keyword in ['sovereign_culture', 'sovereign_education', 'sovereign_geography', 'sovereign_history', 'sovereign_language', 'sovereign_economics', 'sovereign_politics', 'sovereign_society']):
        return 'korean_knowledge'
    
    # 한국어추론 관련
    elif 'winogrande' in filename_lower:
        return 'korean_reasoning'
    
    # KoIFEval 관련
    elif 'koifeval' in filename_lower:
        return 'koifeval'
    
    return None

def get_target_folder_name(benchmark_type):
    """벤치마크 타입에 따른 대상 폴더명 반환"""
    mapping = {
        'legal_qa': '법률지식_QA',
        'legal_reasoning': '법률추론',
        'legal_doc': '법률문서해석',
        'math': '수학',
        'korean_generation': '한국어생성',
        'korean_understanding': '한국어이해',
        'korean_knowledge': '한국어전문지식',
        'korean_reasoning': '한국어추론',
        'koifeval': 'koifeval'
    }
    return mapping.get(benchmark_type)

# 실행
if __name__ == "__main__":
    reference_folder = '/Users/joon/Dev/KT/KT_McNemar/법률지표/gpt4o-1120'
    target_folder = '/Users/joon/Dev/KT/KT_McNemar/법률지표/qwen-72b'
    
    print(" 먼저 dry_run으로 확인해보겠습니다...")
    reorganize_files_by_reference(reference_folder, target_folder, dry_run=True)
    
    print("\n" + "="*50)
    response = input("실제로 파일을 이동하시겠습니까? (y/N): ")
    if response.lower() == 'y':
        print(" 파일 이동을 시작합니다...")
        reorganize_files_by_reference(reference_folder, target_folder, dry_run=False)
    else:
        print("❌ 파일 이동을 취소했습니다.")