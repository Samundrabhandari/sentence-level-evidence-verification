import pandas as pd
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# -----------------------------
# Settings
# -----------------------------
THRESHOLD = 0.50

answers_file = "data/pilot_answers.csv"
sentence_labels_file = "data/labeled_sentences_final.csv"
evidence_file = "results/sentence_with_question_evidence.csv"

output_predictions_file = "results/full_response_baseline_results.csv"
output_report_file = "results/full_response_evaluation_report.csv"
output_confusion_file = "results/full_response_confusion_matrix.csv"


# -----------------------------
# Load data
# -----------------------------
answers_df = pd.read_csv(answers_file)
sentence_labels_df = pd.read_csv(sentence_labels_file)
evidence_df = pd.read_csv(evidence_file)

# Add answer_id to the original answer file
answers_df["answer_id"] = range(1, len(answers_df) + 1)

# Get one Wikipedia evidence text per answer
evidence_by_answer = (
    evidence_df
    .groupby("answer_id")
    .agg({
        "wiki_title": "first",
        "wiki_evidence": "first",
        "wiki_url": "first"
    })
    .reset_index()
)

# Merge answers with evidence
full_response_df = answers_df.merge(
    evidence_by_answer,
    on="answer_id",
    how="left"
)


# -----------------------------
# Create full-response gold labels
# -----------------------------
def get_full_response_gold_label(group):
    """
    If any sentence in the answer is Unsupported or Contradicted,
    the full response is treated as Unsupported.

    If all sentences are Supported,
    the full response is treated as Supported.
    """
    labels = group["gold_label"].astype(str).str.strip().tolist()

    if "Unsupported" in labels or "Contradicted" in labels:
        return "Unsupported"

    return "Supported"


gold_by_answer = (
    sentence_labels_df
    .groupby("answer_id")
    .apply(get_full_response_gold_label)
    .reset_index(name="gold_label")
)

full_response_df = full_response_df.merge(
    gold_by_answer,
    on="answer_id",
    how="left"
)


# -----------------------------
# Run full-response semantic similarity baseline
# -----------------------------
model = SentenceTransformer("all-MiniLM-L6-v2")

similarity_scores = []
predicted_labels = []

for index, row in full_response_df.iterrows():
    ai_answer = str(row["ai_answer"])
    evidence = str(row["wiki_evidence"])

    if evidence.strip() == "" or evidence == "nan":
        similarity_scores.append(0.0)
        predicted_labels.append("Unsupported")
        continue

    answer_embedding = model.encode(ai_answer, convert_to_tensor=True)
    evidence_embedding = model.encode(evidence, convert_to_tensor=True)

    similarity = util.cos_sim(answer_embedding, evidence_embedding).item()

    similarity_scores.append(similarity)

    if similarity >= THRESHOLD:
        predicted_labels.append("Supported")
    else:
        predicted_labels.append("Unsupported")


full_response_df["similarity_score"] = similarity_scores
full_response_df["predicted_label"] = predicted_labels


# -----------------------------
# Evaluate full-response baseline
# -----------------------------
full_response_df["gold_label"] = full_response_df["gold_label"].astype(str).str.strip()
full_response_df["predicted_label"] = full_response_df["predicted_label"].astype(str).str.strip()

# Keep only valid labels
full_response_df = full_response_df[
    full_response_df["gold_label"].isin(["Supported", "Unsupported"])
]

y_true = full_response_df["gold_label"]
y_pred = full_response_df["predicted_label"]

accuracy = accuracy_score(y_true, y_pred)

report = classification_report(
    y_true,
    y_pred,
    labels=["Supported", "Unsupported"],
    zero_division=0,
    output_dict=True
)

report_df = pd.DataFrame(report).transpose()

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=["Supported", "Unsupported"]
)

confusion_df = pd.DataFrame(
    cm,
    index=["Actual Supported", "Actual Unsupported"],
    columns=["Predicted Supported", "Predicted Unsupported"]
)

full_response_df["correct"] = full_response_df["gold_label"] == full_response_df["predicted_label"]


# -----------------------------
# Save results
# -----------------------------
full_response_df.to_csv(output_predictions_file, index=False)
report_df.to_csv(output_report_file)
confusion_df.to_csv(output_confusion_file)

print("Full-response baseline complete!")
print("\nAccuracy:", accuracy)

print("\nClassification Report:")
print(report_df)

print("\nConfusion Matrix:")
print(confusion_df)

print("\nSaved files:")
print(output_predictions_file)
print(output_report_file)
print(output_confusion_file)