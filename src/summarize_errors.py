import pandas as pd

# Read the labeled error analysis file
input_file = "results/error_analysis_candidates_labeled.csv"
df = pd.read_csv(input_file)

# Count how many times each error category appears
error_summary = df["error_category"].value_counts().reset_index()

# Rename columns clearly
error_summary.columns = ["error_category", "count"]

# Save summary
output_file = "results/error_analysis_summary.csv"
error_summary.to_csv(output_file, index=False)

print("Done! Error analysis summary saved to:", output_file)
print(error_summary)