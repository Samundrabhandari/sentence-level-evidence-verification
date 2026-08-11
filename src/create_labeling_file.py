import pandas as pd

# Read the similarity baseline results
input_file = "results/similarity_baseline_results.csv"
df = pd.read_csv(input_file)

# Add empty columns for manual research labeling
df["gold_label"] = ""
df["notes"] = ""

# Save the file that we will manually label
output_file = "data/labeled_sentences.csv"
df.to_csv(output_file, index=False)

print("Done! Labeling file created:", output_file)
print(df[["answer_id", "sentence_id", "sentence", "predicted_label", "gold_label", "notes"]])