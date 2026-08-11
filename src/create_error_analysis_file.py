import pandas as pd

# Read evaluated predictions
input_file = "results/evaluated_predictions.csv"
df = pd.read_csv(input_file)

# Keep only wrong predictions
errors_df = df[df["correct"] == False].copy()

# Add empty column for manual error category
errors_df["error_category"] = ""

# Keep useful columns for reviewing errors
columns_to_keep = [
    "answer_id",
    "question",
    "sentence_id",
    "sentence",
    "wiki_title",
    "wiki_evidence",
    "predicted_label",
    "gold_label",
    "predicted_label_binary",
    "gold_label_binary",
    "notes",
    "error_category"
]

# Only keep columns that exist
columns_to_keep = [col for col in columns_to_keep if col in errors_df.columns]
errors_df = errors_df[columns_to_keep]

# Save error analysis file
output_file = "results/error_analysis_candidates.csv"
errors_df.to_csv(output_file, index=False)

print("Done! Error analysis file created:", output_file)
print(errors_df)