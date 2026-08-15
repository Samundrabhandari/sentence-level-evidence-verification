import pandas as pd


input_file = "results/error_analysis_candidates_labeled_expanded.csv"
output_file = "results/final_error_analysis_summary.csv"

# Read labeled error analysis file
df = pd.read_csv(input_file)

# Clean error category text
df["error_category"] = df["error_category"].astype(str).str.strip()

# Remove empty categories if any exist
df = df[df["error_category"] != ""]
df = df[df["error_category"] != "nan"]

# Count error categories
summary_df = (
    df["error_category"]
    .value_counts()
    .reset_index()
)

summary_df.columns = ["error_category", "count"]

# Add percentage
total_errors = summary_df["count"].sum()
summary_df["percentage"] = (summary_df["count"] / total_errors * 100).round(2)

# Save final summary
summary_df.to_csv(output_file, index=False)

print("Final error analysis summary saved to:", output_file)
print()
print("Total errors:", total_errors)
print()
print(summary_df)