import pandas as pd


def read_accuracy(report_df):
    """
    Read accuracy from a sklearn classification_report CSV.
    """
    if "accuracy" in report_df.index:
        # sklearn stores accuracy differently depending on output format
        row = report_df.loc["accuracy"]
        for col in ["precision", "recall", "f1-score"]:
            if col in row and pd.notna(row[col]):
                return float(row[col])

    return None


def get_metric(report_df, row_name, column_name):
    """
    Safely read a metric from the classification report.
    """
    if row_name in report_df.index and column_name in report_df.columns:
        value = report_df.loc[row_name, column_name]
        if pd.notna(value):
            return float(value)

    return None


def summarize_method(
    method_name,
    unit,
    report_file,
    predictions_file
):
    """
    Create one summary row for a verification method.
    """
    report_df = pd.read_csv(report_file, index_col=0)
    predictions_df = pd.read_csv(predictions_file)

    total_examples = len(predictions_df)

    if "correct" in predictions_df.columns:
        correct_predictions = int(predictions_df["correct"].sum())
        errors = total_examples - correct_predictions
        accuracy = correct_predictions / total_examples
    else:
        correct_predictions = None
        errors = None
        accuracy = read_accuracy(report_df)

    summary = {
        "method": method_name,
        "unit": unit,
        "examples": total_examples,
        "correct_predictions": correct_predictions,
        "errors": errors,
        "accuracy": accuracy,
        "supported_precision": get_metric(report_df, "Supported", "precision"),
        "supported_recall": get_metric(report_df, "Supported", "recall"),
        "supported_f1": get_metric(report_df, "Supported", "f1-score"),
        "unsupported_precision": get_metric(report_df, "Unsupported", "precision"),
        "unsupported_recall": get_metric(report_df, "Unsupported", "recall"),
        "unsupported_f1": get_metric(report_df, "Unsupported", "f1-score"),
        "macro_precision": get_metric(report_df, "macro avg", "precision"),
        "macro_recall": get_metric(report_df, "macro avg", "recall"),
        "macro_f1": get_metric(report_df, "macro avg", "f1-score"),
        "weighted_f1": get_metric(report_df, "weighted avg", "f1-score"),
    }

    return summary


sentence_level_summary = summarize_method(
    method_name="Sentence-level semantic similarity baseline",
    unit="sentence",
    report_file="results/evaluation_report.csv",
    predictions_file="results/evaluated_predictions.csv"
)

full_response_summary = summarize_method(
    method_name="Full-response semantic similarity baseline",
    unit="full_response",
    report_file="results/full_response_evaluation_report.csv",
    predictions_file="results/full_response_baseline_results.csv"
)

comparison_df = pd.DataFrame([
    full_response_summary,
    sentence_level_summary
])

output_file = "results/method_comparison.csv"
comparison_df.to_csv(output_file, index=False)

print("Method comparison saved to:", output_file)
print()
print(comparison_df)