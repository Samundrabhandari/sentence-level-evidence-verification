import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Read the final labeled file
input_file = "data/labeled_sentences_final.csv"
df = pd.read_csv(input_file)

# Clean labels
df["predicted_label"] = df["predicted_label"].astype(str).str.strip()
df["gold_label"] = df["gold_label"].astype(str).str.strip()

# Remove rows without gold labels
df = df[df["gold_label"] != ""]
df = df[df["gold_label"] != "nan"]

# Our semantic similarity baseline only predicts Supported/Unsupported.
# So for this first evaluation, we convert Contradicted into Unsupported.
def convert_to_binary(label):
    if label == "Supported":
        return "Supported"
    elif label in ["Unsupported", "Contradicted"]:
        return "Unsupported"
    else:
        return "Unknown"

df["gold_label_binary"] = df["gold_label"].apply(convert_to_binary)
df["predicted_label_binary"] = df["predicted_label"].apply(convert_to_binary)

# Remove any unknown labels
df = df[df["gold_label_binary"] != "Unknown"]
df = df[df["predicted_label_binary"] != "Unknown"]

# True labels and model predictions
y_true = df["gold_label_binary"]
y_pred = df["predicted_label_binary"]

# Calculate accuracy
accuracy = accuracy_score(y_true, y_pred)

# Generate report
report = classification_report(y_true, y_pred, zero_division=0, output_dict=True)
report_df = pd.DataFrame(report).transpose()

# Generate confusion matrix
labels = ["Supported", "Unsupported"]
cm = confusion_matrix(y_true, y_pred, labels=labels)

confusion_df = pd.DataFrame(
    cm,
    index=["Actual Supported", "Actual Unsupported"],
    columns=["Predicted Supported", "Predicted Unsupported"]
)

# Add correctness column for error analysis
df["correct"] = df["gold_label_binary"] == df["predicted_label_binary"]

# Save results
report_df.to_csv("results/evaluation_report.csv")
confusion_df.to_csv("results/confusion_matrix.csv")
df.to_csv("results/evaluated_predictions.csv", index=False)

print("Evaluation complete!")
print("\nAccuracy:", accuracy)
print("\nClassification Report:")
print(pd.DataFrame(report).transpose())
print("\nConfusion Matrix:")
print(confusion_df)

print("\nSaved files:")
print("results/evaluation_report.csv")
print("results/confusion_matrix.csv")
print("results/evaluated_predictions.csv")