import pandas as pd
import spacy

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

# Read the pilot dataset
input_file = "data/pilot_answers.csv"
df = pd.read_csv(input_file)

sentence_rows = []

for answer_id, row in df.iterrows():
    question = row["question"]
    ai_answer = row["ai_answer"]
    evidence_query = row["evidence_query"]

    doc = nlp(ai_answer)

    for sentence_id, sentence in enumerate(doc.sents, start=1):
        sentence_rows.append({
            "answer_id": answer_id + 1,
            "question": question,
            "evidence_query": evidence_query,
            "sentence_id": sentence_id,
            "sentence": sentence.text.strip()
        })

sentence_df = pd.DataFrame(sentence_rows)

output_file = "results/sentence_level_output.csv"
sentence_df.to_csv(output_file, index=False)

print("Done! Sentence-level output saved to:", output_file)
print(sentence_df)