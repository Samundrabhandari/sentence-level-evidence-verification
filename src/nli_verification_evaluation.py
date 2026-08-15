import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from transformers import pipeline


# -----------------------------
# Settings
# -----------------------------
MODEL_NAME = "facebook/bart-large-mnli"

input_file = "data/labeled_sentences_final.csv"

output_predictions_file = "results/nli_verification_results.csv"
output_report_file = "results/nli_evaluation_report.csv"
output_confusion_file = "results/nli_confusion_matrix.csv"


# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv(input_file)

required_columns = ["sentence", "wiki_evidence", "gold_label"]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")


# -----------------------------
# Load NLI model
# -----------------------------
classifier = pipeline(
    "text-classification",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME,
    top_k=None
)


def run_nli(evidence, claim):
    """
    Use NLI to classify whether the evidence supports,
    contradicts, or is neutral toward the claim.
    """
    if pd.isna(evidence) or str(evidence).strip() == "":
        return {
            "nli_label": "neutral",
            "predicted_label": "Unsupported",
            "nli_confidence": 0.0,
            "entailment_score": 0.0,
            "neutral_score": 1.0,
            "contradiction_score": 0.0
        }

    result = classifier(
        {
            "text": str(evidence),
            "text_pair": str(claim)
        },
        truncation=True
    )

    # Different transformers versions can return slightly different nesting.
    if len(result) > 0 and isinstance(result[0], list):
        result = result[0]

    scores = {}

    for item in result:
        label = item["label"].lower()
        score = float(item["score"])
        scores[label] = score

    entailment_score = scores.get("entailment", 0.0)
    neutral_score = scores.get("neutral", 0.0)
    contradiction_score = scores.get("contradiction", 0.0)

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    if best_label == "entailment":
        predicted_label = "Supported"
    elif best_label == "contradiction":
        predicted_label = "Contradicted"
    else:
        predicted_label = "Unsupported"

    return {
        "nli_label": best_label,
        "predicted_label": predicted_label,
        "nli_confidence": round(best_score, 4),
        "entailment_score": round(entailment_score, 4),
        "neutral_score": round(neutral_score, 4),
        "contradiction_score": round(contradiction_score, 4)
    }


# -----------------------------
# Run NLI prediction
# -----------------------------
nli_results = []

for index, row in df.iterrows():
    print(f"Running NLI on row {index + 1}/{len(df)}")

    evidence = row["wiki_evidence"]
    claim = row["sentence"]

    result = run_nli(evidence, claim)
    nli_results.append(result)


nli_df = pd.DataFrame(nli_results)

df["nli_label"] = nli_df["nli_label"]
df["nli_predicted_label"] = nli_df["predicted_label"]
df["nli_confidence"] = nli_df["nli_confidence"]
df["entailment_score"] = nli_df["entailment_score"]
df["neutral_score"] = nli_df["neutral_score"]
df["contradiction_score"] = nli_df["contradiction_score"]


# -----------------------------
# Clean labels
# -----------------------------
df["gold_label"] = df["gold_label"].astype(str).str.strip()
df["nli_predicted_label"] = df["nli_predicted_label"].astype(str).str.strip()

valid_labels = ["Supported", "Unsupported", "Contradicted"]

df = df[df["gold_label"].isin(valid_labels)]
df = df[df["nli_predicted_label"].isin(valid_labels)]


# -----------------------------
# Evaluate NLI predictions
# -----------------------------
y_true = df["gold_label"]
y_pred = df["nli_predicted_label"]

accuracy = accuracy_score(y_true, y_pred)

report = classification_report(
    y_true,
    y_pred,
    labels=valid_labels,
    zero_division=0,
    output_dict=True
)

report_df = pd.DataFrame(report).transpose()

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=valid_labels
)

confusion_df = pd.DataFrame(
    cm,
    index=[f"Actual {label}" for label in valid_labels],
    columns=[f"Predicted {label}" for label in valid_labels]
)

df["nli_correct"] = df["gold_label"] == df["nli_predicted_label"]


# -----------------------------
# Save outputs
# -----------------------------
df.to_csv(output_predictions_file, index=False)
report_df.to_csv(output_report_file)
confusion_df.to_csv(output_confusion_file)

print()
print("NLI evaluation complete!")
print()
print("Accuracy:", accuracy)
print()
print("Classification Report:")
print(report_df)
print()
print("Confusion Matrix:")
print(confusion_df)
print()
print("Saved files:")
print(output_predictions_file)
print(output_report_file)
print(output_confusion_file)