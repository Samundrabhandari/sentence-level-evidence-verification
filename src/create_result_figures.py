from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# -----------------------------
# File paths
# -----------------------------
method_file = "results/method_comparison.csv"
error_file = "results/final_error_analysis_summary.csv"
sentence_confusion_file = "results/confusion_matrix.csv"
full_response_confusion_file = "results/full_response_confusion_matrix.csv"

figures_dir = Path("results/figures")
figures_dir.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Helper function for confusion matrices
# -----------------------------
def plot_confusion_matrix(confusion_df, title, output_path):
    """
    Create a labeled confusion matrix figure.
    """
    fig, ax = plt.subplots(figsize=(7, 5))

    values = confusion_df.values
    image = ax.imshow(values)

    ax.set_title(title)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("Actual Label")

    ax.set_xticks(range(len(confusion_df.columns)))
    ax.set_xticklabels(confusion_df.columns, rotation=20, ha="right")

    ax.set_yticks(range(len(confusion_df.index)))
    ax.set_yticklabels(confusion_df.index)

    for row_index in range(values.shape[0]):
        for col_index in range(values.shape[1]):
            ax.text(
                col_index,
                row_index,
                str(values[row_index, col_index]),
                ha="center",
                va="center",
                fontsize=14,
            )

    fig.colorbar(image, ax=ax)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()


# -----------------------------
# Figure 1: Method accuracy comparison
# -----------------------------
method_df = pd.read_csv(method_file)

method_labels = method_df["method"].replace({
    "Full-response semantic similarity baseline": "Full-response baseline",
    "Sentence-level semantic similarity baseline": "Sentence-level baseline",
})

accuracy_percent = method_df["accuracy"] * 100

plt.figure(figsize=(8, 5))
plt.bar(method_labels, accuracy_percent)
plt.ylabel("Accuracy (%)")
plt.title("Method Accuracy Comparison")
plt.ylim(0, 100)

for index, value in enumerate(accuracy_percent):
    plt.text(index, value + 2, f"{value:.1f}%", ha="center")

plt.tight_layout()
plt.savefig(figures_dir / "method_accuracy_comparison.png", dpi=300)
plt.close()


# -----------------------------
# Figure 2: Error category distribution
# -----------------------------
error_df = pd.read_csv(error_file)
error_df = error_df.sort_values("count", ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(error_df["error_category"], error_df["count"])
plt.xlabel("Number of Errors")
plt.title("Sentence-Level Error Category Distribution")

for index, value in enumerate(error_df["count"]):
    percentage = error_df.iloc[index]["percentage"]
    plt.text(value + 0.2, index, f"{value} ({percentage:.1f}%)", va="center")

plt.tight_layout()
plt.savefig(figures_dir / "error_category_distribution.png", dpi=300)
plt.close()


# -----------------------------
# Figure 3: Sentence-level confusion matrix
# -----------------------------
sentence_confusion_df = pd.read_csv(sentence_confusion_file, index_col=0)

plot_confusion_matrix(
    confusion_df=sentence_confusion_df,
    title="Sentence-Level Baseline Confusion Matrix",
    output_path=figures_dir / "sentence_level_confusion_matrix.png",
)


# -----------------------------
# Figure 4: Full-response confusion matrix
# -----------------------------
full_response_confusion_df = pd.read_csv(full_response_confusion_file, index_col=0)

plot_confusion_matrix(
    confusion_df=full_response_confusion_df,
    title="Full-Response Baseline Confusion Matrix",
    output_path=figures_dir / "full_response_confusion_matrix.png",
)


print("Figures created successfully:")
print("results/figures/method_accuracy_comparison.png")
print("results/figures/error_category_distribution.png")
print("results/figures/sentence_level_confusion_matrix.png")
print("results/figures/full_response_confusion_matrix.png")