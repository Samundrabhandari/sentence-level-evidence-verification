# Expanded Experiment Log

## Project Title

Improving the Reliability of AI-Generated Responses Through Sentence-Level Evidence Verification

## Date

August 9, 2026

---

# Purpose of the Expanded Experiment

After completing the small pilot experiment, I expanded the dataset to make the research results stronger and more meaningful.

The original pilot dataset had:

- 5 questions
- 15 sentence-level examples

The expanded dataset has:

- 20 factual questions
- 58 sentence-level examples

The purpose of expanding the dataset was to test whether the semantic similarity baseline still performs well when evaluated on a larger and more varied set of factual claims.

---

# Expanded Dataset Creation

I updated:

`data/pilot_answers.csv`

The expanded dataset includes factual questions from topics such as:

- Science
- History
- Literature
- Geography
- Biology
- Technology
- General knowledge

Each row contains:

```text
question
ai_answer
evidence_query
```

Some AI-generated answers intentionally include incorrect or unsupported claims. This allows the verification system to be tested on both correct and problematic sentences.

## Examples of Intentionally Problematic Claims

```text
Mars is the largest planet in the solar system.
Jupiter is smaller than Earth.
DNA is made of amino acids.
Japan uses the euro as its official currency.
Mount Everest is located in South America.
Water is mainly composed of carbon dioxide.
```

These examples are useful because they test whether the system can detect unsupported or contradicted claims.

---

# Pipeline Rerun on Expanded Dataset

After updating the dataset, I reran the full pipeline.

The full pipeline was:

```text
data/pilot_answers.csv
↓
src/split_sentences.py
↓
results/sentence_level_output.csv
↓
src/retrieve_evidence_by_question.py
↓
results/sentence_with_question_evidence.csv
↓
src/semantic_similarity_baseline.py
↓
results/similarity_baseline_results.csv
↓
src/create_simple_labeling_file.py
↓
data/simple_labeling_file.csv
↓
data/labeled_sentences_final.csv
↓
src/evaluate_results.py
↓
results/evaluation_report.csv
results/confusion_matrix.csv
results/evaluated_predictions.csv
↓
src/create_error_analysis_file.py
↓
results/error_analysis_candidates.csv
```

---

# Step 1: Sentence Splitting

Script used:

`src/split_sentences.py`

Command used:

```bash
python src/split_sentences.py
```

Input file:

`data/pilot_answers.csv`

Output file:

`results/sentence_level_output.csv`

## Result

The expanded dataset produced 58 sentence-level examples.

## Purpose

This step split full AI-generated answers into individual sentence-level claims so that each claim could be checked separately.

---

# Step 2: Wikipedia Evidence Retrieval

Script used:

`src/retrieve_evidence_by_question.py`

Command used:

```bash
python src/retrieve_evidence_by_question.py
```

Input file:

`results/sentence_level_output.csv`

Output file:

`results/sentence_with_question_evidence.csv`

## Rate Limiting Issue

During this step, Wikipedia rate limiting occurred.

The terminal showed messages such as:

```text
Rate limited. Waiting 10 seconds...
Rate limited. Waiting 20 seconds...
Rate limited. Waiting 30 seconds...
```

To reduce rate limiting, I increased the delay between Wikipedia requests from 2 seconds to 6 seconds.

After rerunning the script, the evidence retrieval worked better and retrieved Wikipedia evidence for the expanded dataset.

## Purpose

This step retrieved evidence from Wikipedia for each sentence-level claim using the `evidence_query` column.

---

# Step 3: Semantic Similarity Baseline

Script used:

`src/semantic_similarity_baseline.py`

Command used:

```bash
python src/semantic_similarity_baseline.py
```

Input file:

`results/sentence_with_question_evidence.csv`

Output file:

`results/similarity_baseline_results.csv`

## Added Columns

The semantic similarity baseline added:

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

## Purpose

This baseline measured how semantically similar each sentence was to the retrieved Wikipedia evidence.

---

# Step 4: Simple Labeling File

Script used:

`src/create_simple_labeling_file.py`

Command used:

```bash
python src/create_simple_labeling_file.py
```

Input file:

`results/similarity_baseline_results.csv`

Output file:

`data/simple_labeling_file.csv`

## Purpose

This file was created to make manual/gold labeling easier.

It included:

```text
sentence
wiki_title
wiki_evidence
predicted_label
gold_label
notes
```

---

# Expanded Gold Labels

The final expanded labeled file is:

`data/labeled_sentences_final.csv`

## Gold Label Counts

```text
Supported: 33
Unsupported: 13
Contradicted: 12
Total: 58
```

## Label Definitions

### Supported

The retrieved Wikipedia evidence clearly supports the sentence.

### Unsupported

The retrieved evidence does not clearly prove the sentence.

Important: Unsupported does not always mean the sentence is false. It means the retrieved evidence does not support it.

### Contradicted

The retrieved evidence clearly conflicts with the sentence or shows the sentence is false.

---

# Expanded Evaluation

Script used:

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

Because the semantic similarity baseline only predicts Supported or Unsupported, the evaluation used binary labels.

## Binary Conversion

```text
Supported → Supported
Unsupported → Unsupported
Contradicted → Unsupported
```

This means the binary evaluation tested whether the model could separate supported claims from claims that were not supported by the evidence.

---

# Expanded Evaluation Results

## Accuracy

```text
Accuracy = 0.586207
Approximate accuracy = 58.6%
```

The model correctly predicted about 34 out of 58 sentence-level examples.

---

# Classification Report

## Supported Class

```text
Precision = 0.595745
Recall = 0.848485
F1-score = 0.700000
Support = 33
```

## Unsupported Class

```text
Precision = 0.545455
Recall = 0.240000
F1-score = 0.333333
Support = 25
```

## Overall Results

```text
Accuracy = 0.586207
Macro average precision = 0.570600
Macro average recall = 0.544242
Macro average F1-score = 0.516667
Weighted average F1-score = 0.541954
Total examples = 58
```

---

# Confusion Matrix

```text
                    Predicted Supported    Predicted Unsupported
Actual Supported             28                     5
Actual Unsupported           19                     6
```

## Confusion Matrix Interpretation

The model correctly predicted 28 supported claims as Supported.

The model incorrectly predicted 5 supported claims as Unsupported.

The model correctly predicted 6 unsupported or contradicted claims as Unsupported.

The model incorrectly predicted 19 unsupported or contradicted claims as Supported.

This shows that the semantic similarity baseline is much better at identifying supported claims than detecting unsupported or contradicted claims.

---

# Main Expanded Evaluation Finding

The expanded evaluation shows that semantic similarity alone is not reliable enough for factual verification.

The model often predicted `Supported` when a sentence was merely related to the Wikipedia evidence but not actually supported by it.

This means the model confused:

```text
topic similarity
```

with:

```text
factual support
```

This is an important research finding because factual verification requires more than checking whether two pieces of text are about the same topic.

---

# Expanded Error Analysis

Script used:

`src/create_error_analysis_file.py`

Command used:

```bash
python src/create_error_analysis_file.py
```

Output file:

`results/error_analysis_candidates.csv`

The expanded evaluation had 24 incorrect predictions.

A labeled expanded error analysis file was created:

`results/error_analysis_candidates_labeled_expanded.csv`

A summary file was created:

`results/error_analysis_summary_expanded.csv`

---

# Expanded Error Category Summary

The 24 errors were categorized as:

```text
Contradiction missed / topical overlap: 9
Evidence incomplete / retrieval limitation: 8
Pronoun/coreference problem: 5
Subjective claim / evidence limitation: 1
Sentence splitting / mixed claim: 1
Total errors: 24
```

---

# Error Analysis Interpretation

## 1. Contradiction Missed / Topical Overlap

This was the most common error type.

The semantic similarity model often gave high similarity scores to false claims because the sentence and evidence shared related topic words.

Example:

```text
Jupiter is smaller than Earth.
```

The retrieved evidence discusses Jupiter, so the topic is related. However, the claim is factually wrong.

This shows that semantic similarity can identify related text but cannot reliably detect contradiction.

---

## 2. Evidence Incomplete / Retrieval Limitation

Some sentences were true or partially true, but the retrieved Wikipedia summary did not clearly prove them.

In these cases, the system did not have enough evidence to make a reliable judgment.

This shows that evidence retrieval quality strongly affects verification performance.

---

## 3. Pronoun/Coreference Problem

Some sentences used pronouns such as “he” or “it.”

Example:

```text
He was born in Germany.
```

The evidence may support the claim, but the sentence does not repeat the person’s name. This can make semantic similarity weaker.

This shows that sentence-level verification may need coreference resolution so pronouns are linked back to the correct entity.

---

## 4. Subjective Claim / Evidence Limitation

Some claims used subjective wording such as:

```text
one of his most famous
```

These claims are harder to verify because they may require stronger or more specific evidence.

---

## 5. Sentence Splitting / Mixed Claim

One error came from a sentence containing more than one claim.

This shows that claim-level verification may sometimes be better than sentence-level verification when a sentence contains multiple factual claims.

---

# Updated Research Findings

Based on the expanded dataset, the main findings are:

1. Sentence-level verification helps identify exactly which parts of an AI-generated answer are problematic.

2. The semantic similarity baseline performs better on supported claims than unsupported or contradicted claims.

3. The model often confuses topical similarity with factual support.

4. Contradicted claims are especially difficult for semantic similarity because false claims may still share many keywords with the evidence.

5. Evidence retrieval quality is a major limitation. If the retrieved evidence is incomplete, the verification result may be unreliable.

6. Pronouns and sentence context matter. Some sentence-level claims are hard to verify when removed from the full answer.

7. A stronger future method should include Natural Language Inference or another contradiction-aware model.

---

# Important Expanded Experiment Files

## Data Files

```text
data/pilot_answers.csv
data/simple_labeling_file.csv
data/labeled_sentences_final.csv
```

## Result Files

```text
results/sentence_level_output.csv
results/sentence_with_question_evidence.csv
results/similarity_baseline_results.csv
results/evaluation_report.csv
results/confusion_matrix.csv
results/evaluated_predictions.csv
results/error_analysis_candidates.csv
results/error_analysis_candidates_labeled_expanded.csv
results/error_analysis_summary_expanded.csv
```

## Source Code Files

```text
src/split_sentences.py
src/retrieve_evidence_by_question.py
src/semantic_similarity_baseline.py
src/create_simple_labeling_file.py
src/evaluate_results.py
src/create_error_analysis_file.py
src/summarize_errors.py
```

---

# Expanded Experiment Conclusion

The expanded experiment produced stronger evidence that semantic similarity alone is not enough for factual verification.

The baseline achieved 58.6% accuracy on 58 sentence-level examples. It performed well on many supported claims but struggled with unsupported and contradicted claims.

The most important limitation was that semantic similarity often confused topic similarity with factual support.

This supports the main research argument that factual verification requires stronger methods than similarity alone, especially for detecting contradiction and unsupported claims.

---

# Next Step

The next step is to begin writing the final research report.

The report should explain:

1. Why sentence-level verification matters.
2. How the dataset was created.
3. How evidence was retrieved.
4. How the semantic similarity baseline worked.
5. What the evaluation results showed.
6. What the error analysis revealed.
7. Why stronger methods such as Natural Language Inference may be useful in future work.