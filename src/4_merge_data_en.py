import pandas as pd
import os

model_A = "Llama-74B"
model_B = "GPT4o"
domain = [ 'winogrande', 'musr']
# domain = ['지시이행도', '추론', '전문지식']

BENCHMARKS = ['bbh','boolq','drop','gpqa','gsm8k','ifeval','mmlu_pro','musr','openbookqa','piqa','winogrande','math']
DOMAIN_TO_BENCHMARKS = {
    'joon': ['mmlu_pro', 'musr', 'winogrande'],
    '지시이행도-CKP': ['ifeval'],
    '추론-CKP': ['musr','gpqa','winogrande','bbh','openbookqa','drop', 'boolq','piqa'],
    '수학-CKP': ['gsm8k'],
    '전문지식-CKP': ['mmlu_pro'],
    '추론-내부': ['musr','gpqa','winogrande','bbh'],
    '전문지식-내부': ['mmlu_pro'],
    '지시이행도-내부': ['ifeval'],
    '수학-내부': ['gsm8k','math'],
}

def load_model_result(benchmark_name, model):
    df_list = []
    folder_paths = [f"./영어지표/{model}/{benchmark_name}/"]
    # 공통 처리
    for folder_path in folder_paths:
        jsonl_files = [f for f in os.listdir(folder_path) if f.endswith(('.json', '.jsonl', '.xlsx'))]
        for file in jsonl_files:
            file_path = os.path.join(folder_path, file)
            if file.endswith('.json'):
                df = pd.read_json(file_path)
            elif file.endswith('.jsonl'):
                df = pd.read_json(file_path, lines=True, encoding="utf-8-sig")
            elif file.endswith('.xlsx'):
                df = pd.read_excel(file_path)

            df['id'] = df.apply(lambda x: file.replace('.jsonl', '').replace('.xlsx', '') + str(x.name), axis=1)
            df_list.append(df)

    return pd.concat(df_list, ignore_index=True, sort=False)


for sub_domain in domain:
    raw_df_all = []
    model_A_df_all = []
    model_B_df_all = []

    # 데이터셋 폴더 경로 설정
    if sub_domain in BENCHMARKS:
        folder_paths = [f"./영어지표/dataset/{sub_domain}/"]
    elif sub_domain in DOMAIN_TO_BENCHMARKS:
        benchmarks = DOMAIN_TO_BENCHMARKS[sub_domain]
        folder_paths = [f"./영어지표/dataset/{benchmark}/" for benchmark in benchmarks]

    for folder_path in folder_paths:
        benchmark_name = os.path.basename(folder_path.rstrip('/'))
        files = [f for f in os.listdir(folder_path) if f.endswith('.jsonl')]
        df_list = []
        for file in files:
            file_path = os.path.join(folder_path, file)
            df = pd.read_json(file_path, lines=True)
            if benchmark_name == 'mmlu_pro':
                df['inner_index'] = df.groupby('category').cumcount()
                df['id'] = df.apply(lambda row: 'mmlu_pro_' + str(row['category']).replace('\n', '') + str(row['inner_index']), axis=1)
                df['category'] = df.apply(lambda row: 'mmlu_pro_' + str(row['category']).replace('\n', ''), axis=1)
            else:
                df['id'] = df.apply(lambda x: file.replace('.jsonl', '') + str(x.name), axis=1)
                df['category'] = os.path.splitext(file)[0]
            df_list.append(df)

        raw_df_all.append(pd.concat(df_list, ignore_index=True, sort=False))
        model_A_df = load_model_result(benchmark_name, model_A)
        model_B_df = load_model_result(benchmark_name, model_B)
    
        # 평가 기준 컬럼 이름 정리
        if benchmark_name == 'ifeval':
            model_A_df = model_A_df.rename(columns={'prompt_level_strict_acc': f'{model_A}_EM'})
            model_B_df = model_B_df.rename(columns={'prompt_level_strict_acc': f'{model_B}_EM'})
            model_A_df[f'{model_A}_EM'] = model_A_df[f'{model_A}_EM'].astype(int)
            model_B_df[f'{model_B}_EM'] = model_B_df[f'{model_B}_EM'].astype(int)
        elif benchmark_name == 'drop':
            model_A_df = model_A_df.rename(columns={'em': f'{model_A}_EM'})
            model_B_df = model_B_df.rename(columns={'em': f'{model_B}_EM'})
        elif benchmark_name == 'gsm8k':
            model_A_df = model_A_df.rename(columns={'exact_match': f'{model_A}_EM'})
            model_B_df = model_B_df.rename(columns={'exact_match': f'{model_B}_EM'})
            if 'filter' in model_A_df.columns:
                model_A_df = model_A_df[model_A_df['filter'].isin(['strict-match', 'none'])]
            if 'filter' in model_B_df.columns:
                model_B_df = model_B_df[model_B_df['filter'].isin(['strict-match', 'none'])]
        elif benchmark_name == 'bbh':
            model_A_df = model_A_df.rename(columns={'exact_match': f'{model_A}_EM'})
            model_B_df = model_B_df.rename(columns={'exact_match': f'{model_B}_EM'})
            if 'filter' in model_A_df.columns:
                model_A_df = model_A_df[model_A_df['filter'].isin(['flexible-extract', 'get-answer'])]
            if 'filter' in model_B_df.columns:
                model_B_df = model_B_df[model_B_df['filter'].isin(['flexible-extract', 'get-answer'])]
        else:
            model_A_df = model_A_df.rename(columns={'exact_match': f'{model_A}_EM'})
            model_B_df = model_B_df.rename(columns={'exact_match': f'{model_B}_EM'})
        model_A_df_all.append(model_A_df)
        model_B_df_all.append(model_B_df)
    
    raw_df = pd.concat(raw_df_all, ignore_index=True, sort=False)
    model_A_df = pd.concat(model_A_df_all, ignore_index=True, sort=False)
    model_B_df = pd.concat(model_B_df_all, ignore_index=True, sort=False)

    final_df = pd.merge(raw_df[['id', 'category']], model_A_df[['id', f'{model_A}_EM']], on='id', how='left')
    final_df = pd.merge(final_df, model_B_df[['id', f'{model_B}_EM']], on='id', how='left')

    if raw_df.shape[0] == model_A_df.shape[0] == model_B_df.shape[0]:
        if sub_domain in BENCHMARKS:
            output_path = f'./res_merge_data_en/{model_A}_{model_B}_en_벤치마크'
        elif sub_domain in DOMAIN_TO_BENCHMARKS:    
            output_path = f'./res_merge_data_en/{model_A}_{model_B}_en_지표'
        os.makedirs(output_path, exist_ok=True)
        final_df.to_excel(f"{output_path}/{sub_domain}_{model_A}_{model_B}.xlsx", index=False)
        print(f"{sub_domain}, {raw_df.shape[0], model_A_df.shape[0], model_B_df.shape[0]}")
    else:
        print(f"Check {sub_domain}, {raw_df.shape[0], model_A_df.shape[0], model_B_df.shape[0]}")
