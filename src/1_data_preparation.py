import os

def prepare_data_folders(top_level_folder, prefix_to_keep, extension_to_keep):

    if not os.path.isdir(top_level_folder):
        print(f"[오류] 폴더를 찾을 수 없습니다: {top_level_folder}")
        return

    print(f"'{top_level_folder}' 폴더의 데이터 준비를 시작합니다...")
    print(f"==> 유지할 파일: '{prefix_to_keep}'로 시작하는 '{extension_to_keep}' 파일")
    print("-" * 50)

    for subfolder_name in os.listdir(top_level_folder):
        subfolder_path = os.path.join(top_level_folder, subfolder_name)

        if os.path.isdir(subfolder_path):
            print(f"📁 폴더 [{subfolder_name}] 처리 중...")
            
            for filename in os.listdir(subfolder_path):
                file_path = os.path.join(subfolder_path, filename)

                if filename.startswith(prefix_to_keep) and filename.endswith(extension_to_keep):
                    print(f"  [유지] {filename}")
                    continue
                try:
                    os.remove(file_path)
                    print(f"  [삭제] {filename}")
                except OSError as e:
                    print(f"  [에러] {filename} 삭제 중 오류 발생: {e}")
            
            print("-" * 50)

    print("✅ 모든 폴더의 데이터 준비가 완료되었습니다.")


if __name__ == "__main__":
    target_directory = './영어지표/GPT4o'
    prefix = 'samples'
    # extension = '.xlsx'
    extension = '.jsonl'
    
    prepare_data_folders(target_directory, prefix, extension)