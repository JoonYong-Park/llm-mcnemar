import pandas as pd
import os

model_A = "GPT4ok-6ckp"
model_B = "GPT4o-1120"
domain = ['k_referential_hard','kmmlu','ko_sovereign','kobest','Ko-ComprehensiveGen-hard','KoIFEval','Korean_national_civil_service','korean_naturalization','ko-winogrande','kpragmatics_hard','한국어이해-CKP','한국어추론-CKP','한국사회문화-CKP','한국전문지식-CKP']


BENCHMARKS = ['k_referential','k_referential_hard','kmmlu','ko_sovereign','kobest','Ko-ComprehensiveGen','Ko-ComprehensiveGen-hard','Ko-GSM8K','KoIFEval','Korean_national_civil_service','korean_naturalization','ko-winogrande','kpragmatics','kpragmatics_hard','kt_kmmlu']
DOMAIN_TO_BENCHMARKS = {
    '한국어이해-CKP': ['kpragmatics_hard','kobest_boolq','kobest_sentineg','ko_sovereign_language_literature'],
    '한국어생성-CKP': ['Ko-ComprehensiveGen-hard'],
    '한국어추론-CKP': ['ko-winogrande','kobest_copa','kobest_hellaswag','kobest_wic'],
    '한국사회문화-CKP': ['k_referential_hard','ko_sovereign_culture_folklore','ko_sovereign_society'],
    '한국전문지식-CKP': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography','Korean_national_civil_service','korean_naturalization'],

    '한국어이해-내부': ['kpragmatics','kpragmatics_hard','kobest_boolq','kobest_sentineg','ko_sovereign_language_literature'],
    '한국어생성-내부': ['Ko-ComprehensiveGen','Ko-ComprehensiveGen-hard'],
    '한국어추론-내부': ['ko-winogrande','kobest_copa','kobest_hellaswag','kobest_wic'],
    '한국사회문화-내부': ['k_referential','k_referential_hard','ko_sovereign_culture_folklore','ko_sovereign_society'],
    '한국전문지식-내부': ['kmmlu','ko_sovereign_history','ko_sovereign_law','ko_sovereign_economics_finance','ko_sovereign_politics','ko_sovereign_education','ko_sovereign_geography'],
}

def rename_and_filter_em_column(df: pd.DataFrame, model_name: str) -> pd.DataFrame:
    if 'prompt_level_strict_acc' in df.columns:
        df = df.rename(columns={'prompt_level_strict_acc': f'{model_name}_EM'})
        df[f'{model_name}_EM'] = df[f'{model_name}_EM'].astype(int)
    elif 'exact_match' in df.columns:
        df = df.rename(columns={'exact_match': f'{model_name}_EM'})
    elif 'acc' in df.columns:
        df = df.rename(columns={'acc': f'{model_name}_EM'})
    else:
        raise ValueError(f"[ERROR] {model_name} 결과에 정확도 컬럼이 없습니다.")

    if 'filter' in df.columns:
        filter_values = df['filter'].unique()
        if 'get-answer' in filter_values:
            df = df[df['filter'] == 'get-answer']
        elif 'none' in filter_values:
            df = df[df['filter'] == 'none']
        else:
            pass

    return df

def load_model_result(benchmark_name, model):
    df_list = []
    if not any(benchmark_name.startswith(prefix) for prefix in ['kobest_', 'ko_sovereign_']):
        folder_paths = [f"./한국적지표/{model}/{benchmark_name}/"]
        for folder_path in folder_paths:
            jsonl_files = [f for f in os.listdir(folder_path) if f.endswith(('.json', '.jsonl', '.xlsx'))]
            for file in jsonl_files:
                file_path = os.path.join(folder_path, file)
                # print(f"[DEBUG] Reading file: {file_path}")
                if file.endswith('.json'):
                    df = pd.read_json(file_path)
                elif file.endswith('.jsonl'):
                    df = pd.read_json(file_path, lines=True, encoding="utf-8-sig")
                elif file.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                df['id'] = df.apply(lambda x: file.replace('.jsonl', '').replace('.xlsx', '') + str(x.name), axis=1)
                df_list.append(df)
        return pd.concat(df_list, ignore_index=True, sort=False)

def load_kobest_or_sovereign_result(benchmark_name, model):
    if benchmark_name.startswith('ko_sovereign_'):
        benchmark_folder = 'ko_sovereign'
    elif benchmark_name.startswith('kobest_'):
        benchmark_folder = 'kobest'
    folder_path = f"./한국적지표/{model}/{benchmark_folder}"
    for ext in ['.jsonl', '.json', '.xlsx']:
        candidate_file = benchmark_name + ext
        if candidate_file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, candidate_file)
            break
    else:
        raise FileNotFoundError(f"{benchmark_name}에 해당하는 파일이 없습니다.")

    if file_path.endswith('.json'):
        df = pd.read_json(file_path)
    elif file_path.endswith('.jsonl'):
        df = pd.read_json(file_path, lines=True, encoding="utf-8-sig")
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
        i_column = df.columns[8]
        df = df[df[i_column] != '0-shot']

    base_name = os.path.splitext(candidate_file)[0]
    df['id'] = df.apply(lambda x: base_name + str(x.name), axis=1)
    return df

for sub_domain in domain:
    raw_df_all = []
    model_A_df_all = []
    model_B_df_all = []

    if sub_domain in BENCHMARKS:
        folder_paths = [f"./한국적지표/dataset/{sub_domain}/"]
    elif sub_domain in DOMAIN_TO_BENCHMARKS:
        benchmarks = DOMAIN_TO_BENCHMARKS[sub_domain]
        folder_paths = [f"./한국적지표/dataset/{benchmark}/" for benchmark in benchmarks]

    for folder_path in folder_paths:
        benchmark_name = os.path.basename(folder_path.rstrip('/'))
        if not any(benchmark_name.startswith(prefix) for prefix in ['kobest_', 'ko_sovereign_']):
            files = [f for f in os.listdir(folder_path) if f.endswith('.jsonl')]
            df_list = []
            for file in files:
                file_path = os.path.join(folder_path, file)
                df = pd.read_json(file_path, lines=True)
                df['id'] = df.apply(lambda x: file.replace('.jsonl', '') + str(x.name), axis=1)
                df['category'] = os.path.splitext(file)[0]
                df_list.append(df)
            raw_df_all.append(pd.concat(df_list, ignore_index=True, sort=False))
            model_A_df = load_model_result(benchmark_name, model_A)
            model_B_df = load_model_result(benchmark_name, model_B)
        else:
            if benchmark_name.startswith('ko_sovereign_'):
                benchmark_folder = 'ko_sovereign'
            elif benchmark_name.startswith('kobest_'):
                benchmark_folder = 'kobest'
            file_path = f"./한국적지표/dataset/{benchmark_folder}/{benchmark_name}.jsonl"
            raw_df = pd.read_json(file_path, lines=True)
            raw_df['id'] = raw_df.apply(lambda x: benchmark_name + str(x.name), axis=1)
            raw_df['category'] = benchmark_name
            raw_df_all.append(raw_df)
            model_A_df = load_kobest_or_sovereign_result(benchmark_name, model_A)
            model_B_df = load_kobest_or_sovereign_result(benchmark_name, model_B)

        model_A_df = rename_and_filter_em_column(model_A_df, model_A)
        model_B_df = rename_and_filter_em_column(model_B_df, model_B)
        model_A_df_all.append(model_A_df)
        model_B_df_all.append(model_B_df)

    raw_df = pd.concat(raw_df_all, ignore_index=True, sort=False)
    model_A_df = pd.concat(model_A_df_all, ignore_index=True, sort=False)
    model_B_df = pd.concat(model_B_df_all, ignore_index=True, sort=False)

    final_df = pd.merge(raw_df[['id', 'category']], model_A_df[['id', f'{model_A}_EM']], on='id', how='left')
    final_df = pd.merge(final_df, model_B_df[['id', f'{model_B}_EM']], on='id', how='left')

    if raw_df.shape[0] == model_A_df.shape[0] == model_B_df.shape[0]:
        if sub_domain in BENCHMARKS:
            output_path = f'./result/mcnemar_en/{model_A}_{model_B}_korea_벤치마크'
        elif sub_domain in DOMAIN_TO_BENCHMARKS:
            output_path = f'./result/mcnemar_en/{model_A}_{model_B}_korea_지표'
        os.makedirs(output_path, exist_ok=True)
        final_df.to_excel(f"{output_path}/{sub_domain}_{model_A}_{model_B}.xlsx", index=False)
        print(f"{sub_domain}, {raw_df.shape[0], model_A_df.shape[0], model_B_df.shape[0]}")
    else:
        print(f"Check {sub_domain}, {raw_df.shape[0], model_A_df.shape[0], model_B_df.shape[0]}")


