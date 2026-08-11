import pandas as pd

# Read the full results file from the similarity baseline
input_file = "results/similarity_baseline_results.csv"
df = pd.read_csv(input_file)

# Keep only the columns that are useful for manual labeling
simple_df = df[
    [
        "answer_id",
        "question",
        "evidence_query",
        "sentence_id",
        "sentence",
        "wiki_title",
        "wiki_evidence",
        "predicted_label"
    ]
].copy()

# Add empty columns for your manual labels and notes
simple_df["gold_label"] = ""
simple_df["notes"] = ""

# Save the simplified labeling file
output_file = "data/simple_labeling_file.csv"
simple_df.to_csv(output_file, index=False)

print("Done! Simple labeling file created:", output_file)
print(simple_df.head())