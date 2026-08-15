# Research Log

## Project Title

Improving the Reliability of AI-Generated Responses Through Sentence-Level Evidence Verification

## Research Question

How does sentence-level evidence verification compare with full-response verification for evaluating the factual reliability of AI-generated answers?

## Main Project Goal

The goal of this research project is to build and evaluate a prototype system that checks whether each sentence in an AI-generated answer is supported by retrieved evidence.

Instead of judging the whole answer at once, the system splits the answer into individual sentences, retrieves Wikipedia evidence, and predicts whether each sentence is supported or unsupported by the evidence.

The broader purpose is to study whether sentence-level verification gives more precise information about factual reliability than full-response verification.

---

# Project Folder Structure

The project is organized in a clean folder named:

`summer_research_final`

Current main folders:

```text
summer_research_final/
├── data/
├── src/
├── results/
├── notes/
├── report/
├── README.md
└── .venv/
```

## Folder Purposes

- `data/` contains input datasets and manually labeled files.
- `src/` contains Python scripts.
- `results/` contains output files, evaluation results, and error analysis files.
- `notes/` contains research logs and experiment notes.
- `report/` will contain the final research report and presentation.
- `.venv/` is the virtual environment for this project.

---

# Python Environment

A virtual environment was created and activated using:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

The virtual environment keeps this project’s Python libraries separate from other projects.

## Libraries Used

```bash
pip install pandas spacy requests sentence-transformers scikit-learn
python -m spacy download en_core_web_sm
```

## Purpose of Each Library

- `pandas`: reads and writes CSV files.
- `spaCy`: splits AI-generated answers into sentences.
- `en_core_web_sm`: English language model used by spaCy.
- `requests`: retrieves evidence from Wikipedia.
- `sentence-transformers`: converts sentences and evidence into embeddings for semantic similarity.
- `scikit-learn`: calculates evaluation metrics such as accuracy, precision, recall, F1-score, and confusion matrix.

---

# Current Research Pipeline

The project pipeline is:

```text
AI-generated answer
↓
Sentence splitting
↓
Wikipedia evidence retrieval
↓
Semantic similarity baseline
↓
Gold labeling
↓
Evaluation
↓
Error analysis
```

## Main Scripts

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

# Pilot Experiment Summary

The first pilot experiment used:

- 5 factual questions
- 15 sentence-level examples

The pilot experiment confirmed that the full pipeline worked from beginning to end.

The pilot evaluation result was:

- Accuracy: 66.7%
- Total examples: 15
- Actual Supported examples: 9
- Actual Unsupported/Contradicted examples after binary conversion: 6

Pilot confusion matrix:

```text
                    Predicted Supported    Predicted Unsupported
Actual Supported             8                      1
Actual Unsupported           4                      2
```

The pilot error analysis found five error types:

- Pronoun/coreference problem
- Evidence incomplete / topical overlap
- Evidence incomplete
- Subjective claim / evidence incomplete
- Contradiction missed / topical overlap

Detailed pilot notes are saved in:

`notes/pilot_experiment_log.md`

---

# Expanded Dataset Summary

After completing the pilot experiment, the dataset was expanded.

The expanded dataset includes:

- 20 factual questions
- 58 sentence-level examples

The expanded dataset includes topics from:

- Science
- History
- Literature
- Geography
- Biology
- Technology
- General knowledge

Some AI-generated answers intentionally include incorrect or unsupported claims so the verification system can be tested on both correct and problematic sentences.

Detailed expanded experiment notes are saved in:

`notes/expanded_experiment_log.md`

---

# Expanded Dataset Evaluation Result

The semantic similarity baseline was evaluated on 58 sentence-level examples.

## Gold Label Counts

- Supported: 33
- Unsupported: 13
- Contradicted: 12
- Total: 58

Because the semantic similarity baseline only predicts `Supported` or `Unsupported`, the evaluation was converted into binary labels:

```text
Supported → Supported
Unsupported → Unsupported
Contradicted → Unsupported
```

## Accuracy

```text
Accuracy = 0.586207
Approximate accuracy = 58.6%
```

The model correctly predicted about 34 out of 58 sentence-level examples.

---

# Expanded Confusion Matrix

```text
                    Predicted Supported    Predicted Unsupported
Actual Supported             28                     5
Actual Unsupported           19                     6
```

## Interpretation

The model correctly predicted 28 supported claims as Supported.

The model incorrectly predicted 5 supported claims as Unsupported.

The model correctly predicted 6 unsupported or contradicted claims as Unsupported.

The model incorrectly predicted 19 unsupported or contradicted claims as Supported.

This shows that the semantic similarity baseline performs better on supported claims than unsupported or contradicted claims.

---

# Expanded Error Analysis Summary

The expanded evaluation had 24 incorrect predictions.

The errors were categorized as:

```text
Contradiction missed / topical overlap: 9
Evidence incomplete / retrieval limitation: 8
Pronoun/coreference problem: 5
Subjective claim / evidence limitation: 1
Sentence splitting / mixed claim: 1
Total errors: 24
```

---

# Main Research Findings So Far

1. Sentence-level verification helps identify exactly which parts of an AI-generated answer are problematic.

2. The semantic similarity baseline is useful as a simple first method, but it is not reliable enough by itself.

3. The model performs better on clearly supported claims than on unsupported or contradicted claims.

4. The model often confuses topical similarity with factual support.

5. Contradicted claims are especially difficult for semantic similarity because false claims may still share many keywords with the evidence.

6. Evidence retrieval quality strongly affects verification performance.

7. Pronouns and missing context can make sentence-level verification harder.

8. A stronger future method should include Natural Language Inference or another contradiction-aware model.

---

# Important Current Files

## Data Files

```text
data/pilot_answers.csv
data/pilot_answers_pilot_backup.csv
data/simple_labeling_file.csv
data/labeled_sentences_final.csv
data/labeled_sentences_pilot_backup.csv
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

## Notes Files

```text
notes/research_log.md
notes/pilot_experiment_log.md
notes/expanded_experiment_log.md
```

---

# Current Project Status

The project now has a complete expanded baseline experiment.

Completed so far:

- Clean project setup
- Pilot dataset
- Pilot evaluation
- Pilot error analysis
- Expanded dataset
- Sentence splitting on expanded dataset
- Wikipedia evidence retrieval
- Semantic similarity baseline
- Expanded gold labels
- Expanded evaluation
- Expanded confusion matrix
- Expanded error analysis
- Expanded error category summary

The project now has enough core results to begin writing the final research report.

---

# Next Steps

The next major step is to write the final research report.

The report should include:

1. Introduction
2. Research question
3. Background and motivation
4. Dataset
5. Methodology
6. Sentence-level verification pipeline
7. Semantic similarity baseline
8. Evaluation results
9. Error analysis
10. Limitations
11. Future work
12. Conclusion

If time allows, a stronger Natural Language Inference method can be added later. However, the semantic similarity baseline already provides useful results and clear limitations.


---

# Full-Response Baseline Update

## Date

August 10, 2026

I added a simple full-response semantic similarity baseline to compare sentence-level verification with full-response verification.

The script created was:

`src/full_response_baseline.py`

The output files were:

- `results/full_response_baseline_results.csv`
- `results/full_response_evaluation_report.csv`
- `results/full_response_confusion_matrix.csv`

## Full-Response Baseline Result

The full-response baseline was evaluated on 20 full AI-generated answers.

Accuracy:

`10.0%`

Confusion matrix:

```text
                    Predicted Supported    Predicted Unsupported
Actual Supported              2                     0
Actual Unsupported           18                     0