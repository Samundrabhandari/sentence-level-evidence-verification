import pandas as pd
from sentence_transformers import SentenceTransformer, util


# Load a small sentence-transformer model.
# This model converts text into vectors so we can compare meaning.
model = SentenceTransformer("all-MiniLM-L6-v2")

# Input file from the evidence retrieval step
input_file = "results/sentence_with_question_evidence.csv"
df = pd.read_csv(input_file)

# Similarity threshold:
# If the score is 0.50 or higher, we predict Supported.
# Otherwise, we predict Unsupported.
THRESHOLD = 0.50

similarity_scores = []
predicted_labels = []

for index, row in df.iterrows():
    sentence = str(row["sentence"])
    evidence = str(row["wiki_evidence"])

    # If evidence is missing, the system cannot support the sentence
    if evidence.strip() == "" or evidence == "nan":
        similarity_scores.append(0.0)
        predicted_labels.append("Unsupported")
        continue

    # Convert sentence and evidence into embeddings
    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    evidence_embedding = model.encode(evidence, convert_to_tensor=True)

    # Calculate cosine similarity
    similarity = util.cos_sim(sentence_embedding, evidence_embedding).item()

    similarity_scores.append(similarity)

    if similarity >= THRESHOLD:
        predicted_labels.append("Supported")
    else:
        predicted_labels.append("Unsupported")


# Add new columns to the table
df["similarity_score"] = similarity_scores
df["predicted_label"] = predicted_labels

# Save the output
output_file = "results/similarity_baseline_results.csv"
df.to_csv(output_file, index=False)

print("Done! Similarity baseline saved to:", output_file)
print(df[["sentence", "wiki_title", "similarity_score", "predicted_label"]])