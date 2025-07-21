import os
import shutil

def clean_recursively(target_dir, prefix, ext):
    # 1단계: 불필요한 파일 및 특정 폴더 삭제
    for dirpath, dirnames, filenames in os.walk(target_dir, topdown=True):
        if '__MACOSX' in dirnames:
            try:
                path_to_remove = os.path.join(dirpath, '__MACOSX')
                shutil.rmtree(path_to_remove)
                print(f"  [DELETE] 불필요한 폴더: {path_to_remove}")
                dirnames.remove('__MACOSX')
            except OSError as e:
                print(f"  [ERROR] 폴더 삭제 중 오류 발생: {e}")

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            # 조건에 맞지 않으면 삭제
            if not (filename.startswith(prefix) and filename.endswith(ext)):
                try:
                    os.remove(file_path)
                    print(f"  [DELETE] 파일: {file_path}")
                except OSError as e:
                    print(f"  [ERROR] 파일 삭제 중 오류 발생: {e}")
            # 조건에 맞으면 유지 로그 출력
            else:
                print(f"  [☑️ ] 파일: {file_path}")

    # 2단계: 비어있는 폴더 정리
    for dirpath, _, _ in os.walk(target_dir, topdown=False):
        if not os.listdir(dirpath):
            try:
                os.rmdir(dirpath)
                print(f"  [정리] 빈 폴더 삭제: {dirpath}")
            except OSError as e:
                print(f"  [에러] 빈 폴더 삭제 중 오류 발생: {e}")

def process_top_level_folders(root_folder, prefix_to_keep, extension_to_keep, folders_to_preserve=[]):
    """
    최상위 폴더들을 순회하며, 각 폴더를 섹션으로 나누어 로그를 출력하고 정리 작업을 수행합니다.
    """
    print(f"'{root_folder}' 폴더의 데이터 정리를 시작합니다...")
    print(f"==> 유지할 파일: '{prefix_to_keep}'로 시작하는 '{extension_to_keep}' 파일")
    print(f"==> 유지할 폴더: {folders_to_preserve}")

    for folder_name in sorted(os.listdir(root_folder)):
        folder_path = os.path.join(root_folder, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        print("-" * 50)
        print(f"📁 폴더 [{folder_name}] 처리 중...")

        if folder_name in folders_to_preserve:
            print(f"  [유지] 설정에 따라 이 폴더 전체를 건너뜁니다.")
            continue

        clean_recursively(folder_path, prefix_to_keep, extension_to_keep)

    print("-" * 50)
    print("\n✅ 모든 폴더의 데이터 정리가 완료되었습니다.")

if __name__ == "__main__":
    target_directory = './영어지표'
    folders_to_keep = ['dataset'] 
    prefix = 'samples'
    extension = '.jsonl'
    # extension = '.xlsx'
    
    process_top_level_folders(target_directory, prefix, extension, folders_to_keep)