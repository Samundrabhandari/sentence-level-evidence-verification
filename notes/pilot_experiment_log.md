# Pilot Experiment Log

## Project Title

Improving the Reliability of AI-Generated Responses Through Sentence-Level Evidence Verification

## Purpose of the Pilot Experiment

The purpose of the pilot experiment was to test whether the full research pipeline could work from beginning to end on a small dataset.

The pilot dataset was intentionally small so that the system could be built, debugged, and evaluated before expanding to a larger dataset.

The pilot experiment tested:

1. Whether AI-generated answers could be split into sentences.
2. Whether Wikipedia evidence could be retrieved.
3. Whether semantic similarity could predict Supported or Unsupported labels.
4. Whether manually reviewed gold labels could be used for evaluation.
5. Whether error analysis could explain where the baseline failed.

---

# Pilot Dataset

The pilot dataset was saved as:

`data/pilot_answers.csv`

The original pilot dataset contained:

- 5 factual questions
- Around 3 sentences per answer
- 15 total sentence-level examples

The main columns were:

```text
question
ai_answer
evidence_query
```

## Pilot Questions

The pilot questions included:

1. Who developed the theory of relativity?
2. What is the capital of France?
3. Who wrote Hamlet?
4. What planet is known as the Red Planet?
5. Who was the first president of the United States?

---

# Sentence Splitting

The sentence splitting script was:

`src/split_sentences.py`

Command used:

```bash
python src/split_sentences.py
```

Input file:

`data/pilot_answers.csv`

Output file:

`results/sentence_level_output.csv`

## Purpose

This step converted full AI-generated answers into individual sentence-level claims.

Example:

```text
AI answer:
Mars is known as the Red Planet. It appears reddish because of iron oxide. Mars is the largest planet in the solar system.

Sentence-level claims:
1. Mars is known as the Red Planet.
2. It appears reddish because of iron oxide.
3. Mars is the largest planet in the solar system.
```

This step is important because the research project studies sentence-level verification instead of only full-response verification.

---

# Wikipedia Evidence Retrieval

The evidence retrieval script was:

`src/retrieve_evidence_by_question.py`

Command used:

```bash
python src/retrieve_evidence_by_question.py
```

Input file:

`results/sentence_level_output.csv`

Output file:

`results/sentence_with_question_evidence.csv`

## Evidence Query Column

An `evidence_query` column was added to improve Wikipedia retrieval.

Instead of searching Wikipedia using the full question, the script used a cleaner topic query.

Example:

```text
Question: What is the capital of France?
Evidence query: Paris
```

This helped retrieve more relevant Wikipedia pages.

## Pilot Evidence Retrieved

The pilot retrieved evidence for topics such as:

```text
Albert Einstein
Paris
Hamlet
Mars
George Washington
```

---

# Semantic Similarity Baseline

The semantic similarity baseline script was:

`src/semantic_similarity_baseline.py`

Command used:

```bash
python src/semantic_similarity_baseline.py
```

Input file:

`results/sentence_with_question_evidence.csv`

Output file:

`results/similarity_baseline_results.csv`

## Method

The script compared each sentence with the retrieved Wikipedia evidence using sentence embeddings.

It added two columns:

```text
similarity_score
predicted_label
```

## Prediction Rule

The baseline used this rule:

```text
similarity_score >= 0.50 → Supported
similarity_score < 0.50 → Unsupported
```

## Limitation

Semantic similarity measures how related two pieces of text are. It does not always prove factual support.

A false sentence can still have high semantic similarity if it shares topic words with the evidence.

---

# Manual Gold Labeling

A simplified labeling file was created using:

`src/create_simple_labeling_file.py`

Command used:

```bash
python src/create_simple_labeling_file.py
```

Output file:

`data/simple_labeling_file.csv`

The final reviewed pilot labels were saved in:

`data/labeled_sentences_final.csv`

Later, the pilot labeled file was backed up as:

`data/labeled_sentences_pilot_backup.csv`

## Label Definitions

### Supported

The retrieved evidence clearly supports the sentence.

### Unsupported

The retrieved evidence does not clearly prove the sentence.

Important: Unsupported does not always mean the sentence is false. It means the retrieved evidence does not support it.

### Contradicted

The retrieved evidence clearly conflicts with the sentence.

---

# Pilot Evaluation

The evaluation script was:

`src/evaluate_results.py`

Command used:

```bash
python src/evaluate_results.py
```

Output files:

```text
results/evaluation_report.csv
results/confusion_matrix.csv
results/evaluated_predictions.csv
```

Because the semantic similarity baseline only predicted Supported or Unsupported, the evaluation used binary labels:

```text
Supported → Supported
Unsupported → Unsupported
Contradicted → Unsupported
```

---

# Pilot Evaluation Results

The pilot evaluation used 15 sentence-level examples.

## Accuracy

```text
Accuracy = 0.666667
Approximate accuracy = 66.7%
```

## Classification Report

```text
Supported:
Precision = 0.6667
Recall = 0.8889
F1-score = 0.7619
Support = 9

Unsupported:
Precision = 0.6667
Recall = 0.3333
F1-score = 0.4444
Support = 6

Overall accuracy = 0.6667
```

## Confusion Matrix

```text
                    Predicted Supported    Predicted Unsupported
Actual Supported             8                      1
Actual Unsupported           4                      2
```

---

# Pilot Evaluation Interpretation

The pilot result showed that the semantic similarity baseline performed better on supported claims than unsupported or contradicted claims.

The model correctly identified many supported sentences, but it often incorrectly labeled unsupported or contradicted sentences as Supported.

This suggested that semantic similarity alone may confuse topic relatedness with factual support.

---

# Pilot Error Analysis

The error analysis script was:

`src/create_error_analysis_file.py`

Command used:

```bash
python src/create_error_analysis_file.py
```

Output file:

`results/error_analysis_candidates.csv`

A labeled pilot error analysis file was also created:

`results/error_analysis_candidates_labeled.csv`

A summary file was created:

`results/error_analysis_summary.csv`

## Pilot Error Categories

The pilot experiment had 5 errors.

The error categories were:

```text
Pronoun/coreference problem: 1
Evidence incomplete / topical overlap: 1
Evidence incomplete: 1
Subjective claim / evidence incomplete: 1
Contradiction missed / topical overlap: 1
```

---

# Pilot Error Analysis Interpretation

## 1. Pronoun/Coreference Problem

Some sentences used pronouns such as “he.”

Example:

```text
He was born in Germany.
```

The evidence may support the claim, but the sentence does not repeat the person’s name. This can weaken semantic similarity.

## 2. Evidence Incomplete / Topical Overlap

Some evidence discussed the same topic but did not clearly support the exact sentence.

## 3. Subjective Claim / Evidence Incomplete

Some claims used subjective wording such as:

```text
one of his most famous
```

These claims require stronger or more specific evidence.

## 4. Contradiction Missed / Topical Overlap

A false sentence may still share many topic words with the evidence.

Example:

```text
Mars is the largest planet in the solar system.
```

The evidence discusses Mars, so semantic similarity may be high, but the sentence is factually wrong.

---

# Pilot Research Takeaway

The pilot experiment showed that the full pipeline works.

It also showed the main weakness of the semantic similarity baseline:

```text
Semantic similarity can identify related text, but it cannot reliably determine factual support or contradiction.
```

This finding justified expanding the dataset and running a larger evaluation.

---

# Pilot Files

## Data Files

```text
data/pilot_answers_pilot_backup.csv
data/labeled_sentences_pilot_backup.csv
```

## Result Files

```text
results/error_analysis_summary.csv
results/error_analysis_candidates_labeled.csv
```

Some result files were later overwritten when the expanded dataset was run. This is acceptable because the pilot results are preserved in this log.