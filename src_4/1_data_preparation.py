import os
import shutil


def move_files_from_subfolders(target_dir):
    """
    하위 폴더 안의 파일들을 상위 폴더로 이동시키고 빈 하위 폴더를 삭제합니다.
    """
    
    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        
        if os.path.isdir(item_path):
            print(f"[PROCESS] 하위 폴더 발견: {item}")
            
            for root, dirs, files in os.walk(item_path):
                for file in files:
                    src_path = os.path.join(root, file)
                    dst_path = os.path.join(target_dir, file)
                    
                    counter = 1
                    original_dst = dst_path
                    while os.path.exists(dst_path):
                        name, ext = os.path.splitext(original_dst)
                        dst_path = f"{name}_{counter}{ext}"
                        counter += 1
                    
                    try:
                        shutil.move(src_path, dst_path)
                        print(f"[MOVE] {src_path} -> {dst_path}")
                    except OSError as e:
                        print(f"[ERROR] 파일 이동 중 오류: {e}")
            
            try:
                shutil.rmtree(item_path)
                print(f"[DELETE] 하위 폴더 제거: {item_path}")
            except OSError as e:
                print(f"[ERROR] 하위 폴더 삭제 중 오류: {e}")


def clean_recursively(target_dir, prefix, ext):
    """
    불필요한 파일과 폴더 삭제합니다.
    유지할 파일:
    - prefix로 시작하고 ext로 끝나는 파일
    - samples로 시작하고 .jsonl로 끝나는 파일
    - Scenario로 시작하고 all.json으로 끝나는 파일
    - results로 시작하지 않는 .jsonl 파일
    """
    for dirpath, dirnames, filenames in os.walk(target_dir, topdown=True):
        if "__MACOSX" in dirnames:
            try:
                path_to_remove = os.path.join(dirpath, "__MACOSX")
                shutil.rmtree(path_to_remove)
                print(f"[DELETE] 불필요한 폴더: {path_to_remove}")
                dirnames.remove("__MACOSX")
            except OSError as e:
                print(f"[ERROR] 폴더 삭제 중 오류 발생: {e}")

        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            
            # 유지할 파일 조건들
            should_keep = (
                (filename.startswith(prefix) and filename.endswith(ext)) or  # 기본 조건
                (filename.startswith("samples") and filename.endswith(".jsonl")) or  # samples로 시작하고 .jsonl로 끝나는 파일
                (filename.startswith("Scenario") and filename.endswith("all.json")) or  # Scenario로 시작하고 all.json으로 끝나는 파일
                (filename.endswith(".jsonl") and not filename.startswith("results"))  # results로 시작하지 않는 .json 파일
            )
            
            if not should_keep:
                try:
                    os.remove(file_path)
                    print(f"[DELETE] 파일: {file_path}")
                except OSError as e:
                    print(f"[ERROR] 파일 삭제 중 오류 발생: {e}")
            else:
                print(f"[KEEP] 파일: {file_path}")

    for dirpath, _, _ in os.walk(target_dir, topdown=False):
        if not os.listdir(dirpath):
            try:
                os.rmdir(dirpath)
                print(f"[DELETE] 빈 폴더 삭제: {dirpath}")
            except OSError as e:
                print(f"[ERROR] 빈 폴더 삭제 중 오류 발생: {e}")


def process_top_level_folders(root_folder, prefix_to_keep, extension_to_keep, folders_to_preserve=[]):
    """
    최상위 폴더들을 순회하며, 각 폴더를 섹션으로 나누어 로그를 출력하고 정리 작업을 수행합니다.
    """
    print("-" * 116)
    print(f"==> 데이터 폴더:'{root_folder}' 폴더의 데이터 정리를 시작합니다...")
    print(f"==> 유지할 파일:")
    print(f"    - '{prefix_to_keep}'로 시작하는 '{extension_to_keep}' 파일")
    print(f"    - 'samples'로 시작하고 '.jsonl'로 끝나는 파일")
    print(f"    - 'Scenario'로 시작하고 'all.json'으로 끝나는 파일")
    print(f"    - 'results'로 시작하지 않는 '.json' 파일")
    print(f"==> 유지할 폴더: {folders_to_preserve}")

    for folder_name in sorted(os.listdir(root_folder)):
        folder_path = os.path.join(root_folder, folder_name)
        if not os.path.isdir(folder_path):
            continue

        print("\n"+"-" * 50 + f"[{folder_name:^14}]" + "-" * 50)
        
        if folder_name in folders_to_preserve:
            print(f"[SKIP] 설정에 따라 이 폴더 전체를 건너뜁니다.")
            continue

        move_files_from_subfolders(folder_path)
        clean_recursively(folder_path, prefix_to_keep, extension_to_keep)

    print("-" * 116)
    print("\n모든 폴더의 데이터 정리가 완료되었습니다.")


if __name__ == "__main__":
    a = "A.X-3.1"
    b = "Solar-pro2-31B"

    target_directory = f"영어지표/{a}"
    folders_to_keep = ["dataset"]
    prefix = "samples"
    extension = ".jsonl"
    process_top_level_folders(target_directory, prefix, extension, folders_to_keep)

    target_directory = f"영어지표/{b}"
    folders_to_keep = ["dataset"]
    prefix = "samples"
    extension = ".jsonl"
    process_top_level_folders(target_directory, prefix, extension, folders_to_keep)

    target_directory = f"한국어지표/{a}"
    folders_to_keep = ["dataset"]
    prefix = "samples"
    extension = ".jsonl"
    process_top_level_folders(target_directory, prefix, extension, folders_to_keep)

    target_directory = f"한국어지표/{b}"
    folders_to_keep = ["dataset"]
    prefix = "samples"
    extension = ".jsonl"
    process_top_level_folders(target_directory, prefix, extension, folders_to_keep)