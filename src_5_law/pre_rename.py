import os
import shutil
from datetime import datetime

def move_files_to_correct_folders(source_folder, temp_folder, dry_run=False):
    """
    gpt4o-1120 폴더의 파일들을 temp 폴더의 올바른 카테고리로 옮기는 함수
    """
    log_lines = []
    
    # 폴더 매핑 규칙
    folder_mapping = {
        # 법률문서해석
        "last_kolbench": "법률문서해석",
        
        # 법률지식_QA
        "cot_kmmlu_criminal_law": "법률지식_QA",
        "cot_kmmlu_law": "법률지식_QA", 
        "kmmlu-pro": "법률지식_QA",
        "kbl_knowledge_em": "법률지식_QA",
        
        # 법률추론
        "kbl_reasoning_em": "법률추론",
        
        # 수학
        "gsm8k": "수학",
        
        # 한국어생성
        "(new)cot_ko_comprehensivegen": "한국어생성",
        
        # 한국어이해
        "k-pragmatics": "한국어이해",
        "kobalt_700": "한국어이해",
        
        # 한국어전문지식
        "(new)cot_ko_sovereign": "한국어전문지식",
        
        # 한국어추론 (ko-winogrande는 현재 없음)
        
        # 기타 (koifeval)
        "ko_ifeval_new_0827": "koifeval",
    }
    
    for source_subfolder in os.listdir(source_folder):
        if source_subfolder == 'temp':
            continue
            
        source_path = os.path.join(source_folder, source_subfolder)
        if not os.path.isdir(source_path):
            continue
            
        # 매핑된 대상 폴더 찾기
        target_folder_name = folder_mapping.get(source_subfolder)
        if not target_folder_name:
            print(f'⚠️ {source_subfolder}: 매핑 규칙 없음')
            continue
            
        target_folder_path = os.path.join(temp_folder, target_folder_name)
        
        # 대상 폴더가 없으면 생성
        if not os.path.exists(target_folder_path):
            if not dry_run:
                os.makedirs(target_folder_path)
            print(f'📁 폴더 생성: {target_folder_path}')
        
        # 파일들 이동
        files = [f for f in os.listdir(source_path) 
                if os.path.splitext(f)[1] in ['.jsonl', '.xlsx', '.json']]
        
        for filename in files:
            source_file_path = os.path.join(source_path, filename)
            target_file_path = os.path.join(target_folder_path, filename)
            
            # 파일이 이미 존재하는지 확인
            if os.path.exists(target_file_path):
                print(f'⚠️ 파일 이미 존재: {target_folder_name}/{filename}')
                continue
                
            print(f'✅ 이동: {source_subfolder}/{filename} → {target_folder_name}/{filename}')
            log_lines.append(f'{source_subfolder}/{filename} → {target_folder_name}/{filename}')
            
            if not dry_run:
                shutil.move(source_file_path, target_file_path)
    
    # 빈 폴더들 정리
    for source_subfolder in os.listdir(source_folder):
        if source_subfolder == 'temp':
            continue
            
        source_path = os.path.join(source_folder, source_subfolder)
        if os.path.isdir(source_path):
            try:
                if not os.listdir(source_path):  # 빈 폴더인지 확인
                    if not dry_run:
                        os.rmdir(source_path)
                    print(f'🗑️ 빈 폴더 삭제: {source_subfolder}')
            except OSError:
                pass  # 폴더가 비어있지 않거나 삭제할 수 없는 경우
    
    # 로그 저장
    if not dry_run and log_lines:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        log_filename = f'move_log_gpt4o-1120_{timestamp}.txt'
        
        with open(log_filename, 'w', encoding='utf-8') as f:
            for line in log_lines:
                f.write(line + '\n')
        print(f'\n📜 로그 저장 완료: {log_filename}')

# 실행
if __name__ == "__main__":
    source_folder = '/Users/joon/Dev/KT/KT_McNemar/법률지표/llama-legal'
    temp_folder = '/Users/joon/Dev/KT/KT_McNemar/법률지표/llama-legal/temp'
    
    print("�� 먼저 dry_run으로 확인해보겠습니다...")
    move_files_to_correct_folders(source_folder, temp_folder, dry_run=True)
    
    print("\n" + "="*50)
    response = input("실제로 파일을 이동하시겠습니까? (y/N): ")
    if response.lower() == 'y':
        print("�� 파일 이동을 시작합니다...")
        move_files_to_correct_folders(source_folder, temp_folder, dry_run=False)
    else:
        print("❌ 파일 이동을 취소했습니다.")