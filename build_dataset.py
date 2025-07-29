from datasets import load_dataset
import json

# bbh_subset = [
#     'boolean_expressions', 'causal_judgement', 'date_understanding', 'default', 'disambiguation_qa',
#     'dyck_languages', 'formal_fallacies', 'geometric_shapes', 'hyperbaton', 'logical_deduction_five_objects',
#     'logical_deduction_seven_objects', 'logical_deduction_three_objects', 'movie_recommendation',
#     'multistep_arithmetic_two', 'navigate', 'object_counting', 'penguins_in_a_table',
#     'reasoning_about_colored_objects', 'ruin_names', 'salient_translation_error_detection', 'snarks',
#     'sports_understanding', 'temporal_sequences', 'tracking_shuffled_objects_five_objects',
#     'tracking_shuffled_objects_seven_objects', 'tracking_shuffled_objects_three_objects', 'web_of_lies', 'word_sorting'
# ]


ds = load_dataset("wis-k/instruction-following-eval", split="train")
file_name = "ifeval.jsonl"

num_examples = len(ds)
print(f"Total number of examples: {num_examples}")

with open(file_name, "w", encoding="utf-8") as f:
    for example in ds:
        json.dump(example, f, ensure_ascii=False)
        f.write("\n")

print(f"[SUCCESS] {file_name}: {num_examples} examples saved.")