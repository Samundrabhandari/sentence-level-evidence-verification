# VeriClaim: Evidence-Grounded Verification for LLM-Generated Claims

## Abstract

Large language models can generate fluent answers that appear correct even when some individual claims are unsupported, outdated, or contradicted by available evidence. This project investigates whether sentence-level evidence verification can provide a more precise way to evaluate the factual reliability of AI-generated responses than judging an entire response at once.

I built **VeriClaim**, an evidence-grounded verification system that splits AI-generated answers into sentence-level claims, retrieves evidence from Wikipedia, and classifies each claim as **Supported**, **Contradicted**, or **Insufficient Evidence**. The project began as a research pipeline comparing sentence-level verification with full-response verification, then evolved into a deployed Applied AI application.

The project compares three approaches:

1. Full-response semantic similarity baseline
2. Sentence-level semantic similarity baseline
3. Sentence-level Natural Language Inference verifier

On a human-labeled dataset of 58 sentence-level claims, the sentence-level semantic similarity baseline achieved **58.6% accuracy**, while the sentence-level NLI verifier achieved **79.3% accuracy**. A full-response semantic similarity baseline performed poorly, achieving only **10.0% accuracy** on 20 full answers.

The final version of VeriClaim was deployed as an interactive Streamlit application. Users can either paste an AI-generated answer for verification or enter only a factual question and let the app generate, retrieve evidence for, and verify the answer automatically.

Live demo:

https://vericlaim-ai.streamlit.app

---

## 1. Introduction

AI-generated answers are increasingly used for search, education, research assistance, writing support, and general question answering. However, these answers can be difficult to trust because they may sound fluent even when some claims are wrong.

A common problem is that an answer can be partially correct. For example, an AI-generated response may contain two supported sentences and one contradicted sentence. If the entire answer is judged as one block, the incorrect sentence can be hidden by the overall relevance of the response.

Example:

> Jupiter is the largest planet in the Solar System. It is a gas giant. Jupiter is smaller than Earth.

The first two sentences are supported by evidence, but the final sentence is contradicted by evidence. A full-response verification method may still judge the answer as acceptable because the answer is topically related to Jupiter.

This project studies a more detailed approach: verifying AI-generated answers at the sentence level.

Instead of asking only whether the entire answer is correct, VeriClaim asks:

- Which sentence-level claims are supported?
- Which claims are contradicted?
- Which claims do not have enough evidence?
- Does sentence-level verification reveal errors that full-response verification misses?

---

## 2. Research Question

The central research question is:

**How does sentence-level evidence verification compare with full-response verification for evaluating the factual reliability of AI-generated answers?**

The project also investigates several related questions:

1. Does full-response verification miss partial errors inside otherwise relevant answers?
2. Does sentence-level verification provide more useful diagnostic information?
3. Is semantic similarity enough for factual verification?
4. Can Natural Language Inference improve contradiction detection?
5. Can the research pipeline be turned into a usable deployed AI application?

---

## 3. Project Goals

The project had two main goals.

### 3.1 Research Goal

The research goal was to compare verification methods for AI-generated answers.

The methods compared were:

- Full-response semantic similarity verification
- Sentence-level semantic similarity verification
- Sentence-level Natural Language Inference verification

The main objective was to determine whether sentence-level verification gives a better picture of factual reliability than judging an entire answer at once.

### 3.2 Applied AI Goal

The applied goal was to turn the research pipeline into a usable system.

The final application should allow a user to:

1. Enter or generate an AI answer
2. Retrieve evidence
3. Check each sentence-level claim
4. See clear verdicts
5. Understand which parts of the answer are supported, contradicted, or insufficiently supported

This led to the final deployed system: **VeriClaim**.

---

## 4. Project Evolution

The project evolved through several stages.

### 4.1 Stage 1: Initial Sentence-Level Verification Pipeline

The first version of the project focused on building a basic pipeline:

1. Start with factual questions
2. Use AI-generated answers
3. Split each answer into sentences
4. Retrieve evidence from Wikipedia
5. Compare each sentence with the retrieved evidence
6. Assign verification labels

This established the foundation for sentence-level evidence verification.

### 4.2 Stage 2: Semantic Similarity Baseline

The first verification method used semantic similarity.

Each sentence-level claim was compared with retrieved Wikipedia evidence using a sentence-transformer model. If the similarity score was above a threshold, the claim was predicted as supported. Otherwise, it was predicted as unsupported.

This method was useful as a simple baseline. It made the project measurable and gave an initial way to compare claims with evidence.

However, error analysis later showed that semantic similarity often confused topical similarity with factual support.

For example, a false claim about Jupiter may still be semantically similar to evidence about Jupiter because both texts discuss the same topic.

### 4.3 Stage 3: Full-Response Baseline

To compare sentence-level verification against full-response verification, I added a full-response semantic similarity baseline.

This method compared the entire AI-generated answer against Wikipedia evidence.

The purpose was to test whether judging a complete response at once is reliable.

The full-response baseline performed poorly because incorrect sentences were often hidden inside longer, topically relevant answers.

### 4.4 Stage 4: Error Analysis

After evaluating the semantic similarity baseline, I created an error analysis file and manually categorized failure cases.

The largest failure category was:

**Contradiction missed / topical overlap**

This showed that the semantic similarity baseline struggled when a claim was false but still shared topic words with the evidence.

This became an important motivation for adding a contradiction-aware method.

### 4.5 Stage 5: Natural Language Inference Verifier

To improve beyond semantic similarity, I added a Natural Language Inference verifier.

Natural Language Inference is better aligned with factual verification because it asks whether evidence:

- entails a claim,
- contradicts a claim, or
- is neutral toward a claim.

This makes it more useful than semantic similarity, which only measures whether two texts are related.

### 4.6 Stage 6: Deployed Application

The final stage was turning the research pipeline into a deployed app.

The deployed app supports two modes:

1. **Verify a pasted AI answer**
2. **Generate an AI answer, then verify it**

This made the project more useful as an Applied AI portfolio project because users can interact with the system directly through a public link.

---

## 5. System Overview

VeriClaim follows this general pipeline:

```text
User question or AI-generated answer
        ↓
Sentence splitting
        ↓
Wikipedia evidence retrieval
        ↓
Semantic similarity diagnostic score
        ↓
Natural Language Inference classification
        ↓
Sentence-level verdicts
```

The final verdict labels are:

- **Supported**
- **Contradicted**
- **Insufficient Evidence**

The system does not claim to determine absolute truth. It evaluates whether a claim is supported, contradicted, or insufficiently supported by the retrieved evidence.

This distinction is important because the system depends on the retrieved Wikipedia evidence. If the evidence is incomplete or outdated, the verdict may also be limited.

---

## 6. Dataset

The final labeled dataset contains 58 sentence-level claims from 20 factual questions.

| Property | Value |
|---|---:|
| Questions | 20 |
| Sentence-level examples | 58 |
| Supported claims | 33 |
| Unsupported claims | 13 |
| Contradicted claims | 12 |

The main dataset file is:

```text
data/labeled_sentences_final.csv
```

Each row contains a sentence-level claim, the associated question, retrieved evidence, prediction information, and a human-labeled gold label.

Important columns include:

| Column | Description |
|---|---|
| answer_id | Identifier for each AI-generated answer |
| question | Original factual question |
| evidence_query | Query used to retrieve Wikipedia evidence |
| sentence_id | Sentence number inside the answer |
| sentence | Sentence-level claim being verified |
| wiki_title | Retrieved Wikipedia page title |
| wiki_evidence | Retrieved Wikipedia evidence text |
| predicted_label | Baseline predicted label |
| gold_label | Human-labeled correct label |
| notes | Notes about labeling or edge cases |

The dataset was intentionally small and manually inspectable. The purpose was not to create a large-scale benchmark, but to build a clear pilot study that compares verification approaches and reveals their failure modes.

---

## 7. Methods

## 7.1 Full-Response Semantic Similarity Baseline

The full-response baseline compares the entire AI-generated answer with retrieved Wikipedia evidence.

The method predicts whether the full response is supported based on semantic similarity.

This baseline represents a simple approach where the entire answer is judged as one unit.

### Weakness

The weakness of this method is that a full answer can be mostly relevant while still containing an incorrect sentence.

For example, if two sentences are correct and one sentence is false, the whole answer may still be semantically similar to the evidence.

This makes full-response verification too coarse for detecting partial factual errors.

---

## 7.2 Sentence-Level Semantic Similarity Baseline

The sentence-level semantic similarity baseline splits each answer into individual claims and compares each sentence with the retrieved evidence.

This method is more fine-grained than full-response verification because each sentence receives its own prediction.

### Strength

Sentence-level similarity gives more diagnostic information than full-response similarity. It can show which part of an answer is problematic.

### Weakness

Semantic similarity is not the same as factual support.

A contradicted sentence can still have high semantic similarity if it shares the same topic, entity, or keywords with the evidence.

For example:

```text
Jupiter is smaller than Earth.
```

This sentence is topically related to Wikipedia evidence about Jupiter, but it is factually contradicted.

This is why semantic similarity alone is not enough for factual verification.

---

## 7.3 Sentence-Level Natural Language Inference Verifier

The strongest method uses Natural Language Inference.

For each claim and evidence pair, the NLI model predicts whether the evidence:

- entails the claim,
- contradicts the claim, or
- is neutral toward the claim.

These NLI outputs are mapped to VeriClaim labels:

| NLI Output | VeriClaim Label |
|---|---|
| Entailment | Supported |
| Contradiction | Contradicted |
| Neutral | Insufficient Evidence |

This method is better aligned with factual verification because it directly models the relationship between evidence and claim.

---

## 8. Implementation

The project was implemented in Python.

Main tools used:

| Component | Tool |
|---|---|
| Web application | Streamlit |
| Sentence splitting | spaCy |
| Evidence retrieval | Wikipedia API |
| Semantic similarity | Sentence-Transformers |
| NLI verification | Hugging Face Transformers |
| Evaluation | pandas, scikit-learn |
| Visualization | matplotlib |
| AI answer generation | OpenAI API |
| Deployment | Streamlit Community Cloud |
| Version control | Git and GitHub |

Important project files:

```text
app.py
app/app.py
src/semantic_similarity_baseline.py
src/full_response_baseline.py
src/nli_verification_evaluation.py
src/create_method_comparison.py
src/create_result_figures.py
data/labeled_sentences_final.csv
results/method_comparison.csv
results/nli_evaluation_report.csv
results/nli_confusion_matrix.csv
results/figures/
```

The root-level `app.py` acts as a launcher for deployment. The main Streamlit application code is inside:

```text
app/app.py
```

---

## 9. Results

## 9.1 Method Comparison

| Method | Unit | Examples | Accuracy | Correct | Errors |
|---|---:|---:|---:|---:|---:|
| Full-response semantic similarity baseline | Full response | 20 | 10.0% | 2 | 18 |
| Sentence-level semantic similarity baseline | Sentence | 58 | 58.6% | 34 | 24 |
| Sentence-level NLI verifier | Sentence | 58 | 79.3% | 46 | 12 |

The full-response baseline performed worst because it predicted every full answer as supported. This showed that full-response verification can miss errors inside otherwise relevant answers.

The sentence-level semantic similarity baseline performed better, but it still struggled with contradicted claims that were topically similar to the retrieved evidence.

The sentence-level NLI verifier performed best, reaching **79.3% accuracy** on the labeled sentence-level dataset.

---

## 9.2 Full-Response Baseline Result

The full-response baseline was evaluated on 20 full AI-generated answers.

| Metric | Value |
|---|---:|
| Examples | 20 |
| Correct predictions | 2 |
| Errors | 18 |
| Accuracy | 10.0% |

The full-response baseline predicted every full answer as supported.

This result supports the main motivation of the project: judging an entire answer at once is too coarse because partial errors can be hidden inside the full response.

---

## 9.3 Sentence-Level Semantic Similarity Result

The sentence-level semantic similarity baseline was evaluated on 58 sentence-level claims.

| Metric | Value |
|---|---:|
| Examples | 58 |
| Correct predictions | 34 |
| Errors | 24 |
| Accuracy | 58.6% |

This method improved over full-response verification because it evaluated individual sentence-level claims.

However, the error analysis showed that semantic similarity still failed on many contradicted claims.

---

## 9.4 Sentence-Level NLI Result

The NLI verifier was evaluated on the same 58 sentence-level claims.

| Metric | Value |
|---|---:|
| Examples | 58 |
| Correct predictions | 46 |
| Errors | 12 |
| Accuracy | 79.3% |
| Macro F1 | 72.7% |
| Weighted F1 | 79.5% |

Per-class F1 scores:

| Label | F1 Score |
|---|---:|
| Supported | 92.3% |
| Unsupported | 53.8% |
| Contradicted | 72.0% |

The NLI verifier performed strongest on supported claims and showed meaningful improvement in contradiction detection.

---

## 10. NLI Confusion Matrix

The NLI verifier produced the following confusion matrix:

| Actual Label | Predicted Supported | Predicted Unsupported | Predicted Contradicted |
|---|---:|---:|---:|
| Supported | 30 | 3 | 0 |
| Unsupported | 2 | 7 | 4 |
| Contradicted | 0 | 3 | 9 |

The NLI verifier correctly identified:

- 30 out of 33 supported claims
- 7 out of 13 unsupported claims
- 9 out of 12 contradicted claims

This result shows that NLI improved the system’s ability to detect contradictions compared with semantic similarity.

---

## 11. Error Analysis

The sentence-level semantic similarity baseline made 24 errors.

These errors were manually categorized:

| Error Category | Count | Percentage |
|---|---:|---:|
| Contradiction missed / topical overlap | 9 | 37.50% |
| Evidence incomplete / retrieval limitation | 8 | 33.33% |
| Pronoun/coreference problem | 5 | 20.83% |
| Subjective claim / evidence limitation | 1 | 4.17% |
| Sentence splitting / mixed claim | 1 | 4.17% |

---

## 11.1 Contradiction Missed / Topical Overlap

This was the largest error category.

The semantic similarity baseline often labeled contradicted claims as supported because the false claim used the same topic words as the evidence.

This demonstrates that semantic similarity is not enough for factual verification.

A claim can be semantically related to evidence while still being false.

---

## 11.2 Evidence Incomplete / Retrieval Limitation

Some errors occurred because the retrieved Wikipedia evidence was incomplete.

The system retrieves a Wikipedia summary. This summary may not contain every fact needed to verify a specific sentence.

As a result, a true claim may appear unsupported if the required evidence is missing from the retrieved summary.

---

## 11.3 Pronoun and Coreference Problems

Some sentence-level claims used pronouns or references that depended on previous context.

Example:

```text
He was born in Germany.
```

When this sentence is checked alone, it may not be clear who “He” refers to.

This shows that sentence-level verification needs better context handling or coreference resolution.

---

## 11.4 Subjective Claims and Mixed Claims

Some errors came from subjective or mixed claims.

A sentence may contain more than one factual claim, or it may contain wording that is difficult to verify directly.

This shows that sentence splitting is useful, but more advanced claim decomposition would improve the system.

---

## 12. Deployed Application

The final version of VeriClaim was deployed as a Streamlit web application.

Live app:

https://vericlaim-ai.streamlit.app

The app supports two modes.

---

## 12.1 Mode 1: Verify a Pasted AI Answer

In this mode, the user provides:

- Question
- AI-generated answer
- Wikipedia evidence query

The app then:

1. Splits the answer into sentence-level claims
2. Retrieves Wikipedia evidence
3. Calculates a semantic similarity score
4. Runs NLI verification
5. Displays a verdict for each sentence

This mode is useful for testing specific AI-generated answers.

---

## 12.2 Mode 2: Generate an AI Answer, Then Verify It

In this mode, the user enters only a factual question.

The app then:

1. Generates a short AI answer using the OpenAI API
2. Automatically selects a Wikipedia evidence query
3. Retrieves Wikipedia evidence
4. Splits the generated answer into sentence-level claims
5. Runs NLI verification
6. Displays verdicts for each claim

This turns VeriClaim into a complete question-to-verification workflow.

The OpenAI API key is stored using Streamlit secrets and is not included in the GitHub repository.

---

## 13. Example Use Case

Example question:

```text
What is the largest planet in the Solar System?
```

Example AI-generated answer:

```text
Jupiter is the largest planet in the Solar System. It is a gas giant. Jupiter is smaller than Earth.
```

Expected sentence-level results:

| Claim | Expected Verdict |
|---|---|
| Jupiter is the largest planet in the Solar System. | Supported |
| It is a gas giant. | Supported |
| Jupiter is smaller than Earth. | Contradicted |

This example demonstrates why sentence-level verification is useful. The full answer contains both correct and incorrect claims.

---

## 14. Key Findings

## 14.1 Full-Response Verification Is Too Coarse

The full-response baseline achieved only 10.0% accuracy.

It missed partial errors because it judged the answer as one block of text.

This supports the conclusion that full-response verification is not precise enough for evaluating factual reliability.

---

## 14.2 Sentence-Level Verification Gives Better Diagnostic Detail

Sentence-level verification makes it possible to identify which specific sentences are supported, contradicted, or insufficiently supported.

This is more useful than giving one label to an entire response.

---

## 14.3 Semantic Similarity Is Not Enough

Semantic similarity can measure topic relatedness, but factual verification requires more than topic overlap.

The largest error category was contradiction missed due to topical overlap.

This showed that semantic similarity alone is not reliable enough for factual verification.

---

## 14.4 NLI Improves Verification

The NLI verifier achieved 79.3% accuracy, outperforming both semantic similarity baselines.

It also correctly detected 9 out of 12 contradicted claims.

This shows that contradiction-aware models are better suited for evidence-grounded verification.

---

## 14.5 Retrieval Quality Matters

The verifier depends on the evidence it receives.

If retrieved evidence is incomplete, ambiguous, or outdated, the final verdict may be wrong.

This means future improvements should focus not only on better classification models, but also better evidence retrieval.

---

## 15. Limitations

## 15.1 Small Dataset

The final labeled dataset contains 58 sentence-level claims.

This is enough for a pilot research project and prototype, but not enough to make broad claims about all factual verification tasks.

A larger dataset would be needed for stronger generalization.

---

## 15.2 Wikipedia as the Only Evidence Source

The system uses Wikipedia summaries as its evidence source.

Wikipedia is useful and accessible, but it may not contain all facts needed to verify every claim.

The system should therefore be described as evidence-grounded, not truth-grounded.

---

## 15.3 Simple Evidence Retrieval

The current retrieval method uses a single evidence query and retrieves a Wikipedia summary.

This is simple and understandable, but limited.

A stronger version could retrieve multiple passages from multiple sources.

---

## 15.4 Sentence Splitting Can Lose Context

Sentence-level verification can lose context from previous sentences.

Pronouns such as “he,” “she,” “it,” or “they” may become ambiguous when checked independently.

Future work should include coreference resolution or context-aware claim extraction.

---

## 15.5 NLI Model Is Not Perfect

The NLI verifier improved results, but it still made errors.

Unsupported claims were the hardest class because insufficient evidence is difficult to distinguish from contradiction.

---

## 15.6 Generated Answers Can Be Time-Sensitive

In the deployed app’s generation mode, the AI-generated answer may be outdated for time-sensitive questions.

For example, questions about current office holders, live events, or recent news may require up-to-date retrieval beyond a static model response.

This is an important limitation of the generation mode.

---

## 15.7 Public API Cost Risk

The deployed app uses an API-based model for answer generation.

Because the app is public, usage can create API costs.

The current version limits generated answers to short responses, but future versions should include stronger rate limiting, usage controls, or authentication.

---

## 16. Future Work

Future improvements could include:

1. **Multi-source evidence retrieval**  
   Retrieve evidence from several trusted sources instead of only Wikipedia.

2. **Passage-level retrieval**  
   Retrieve specific passages instead of relying on full Wikipedia summaries.

3. **Coreference resolution**  
   Improve handling of pronouns and context-dependent claims.

4. **Atomic claim decomposition**  
   Split complex sentences into smaller factual claims.

5. **Better unsupported-claim detection**  
   Improve the distinction between unsupported and contradicted claims.

6. **Larger evaluation dataset**  
   Expand beyond 58 sentence-level claims.

7. **Explanations for verdicts**  
   Add natural-language explanations showing why a claim was supported or contradicted.

8. **Better evidence query generation**  
   Improve automatic selection of Wikipedia search queries.

9. **Rate limiting and cost controls**  
   Add stronger safeguards for public API usage.

10. **Model comparison**  
   Compare multiple NLI models and smaller deployable models.

---

## 17. Conclusion

This project demonstrates that sentence-level evidence verification is more useful than full-response verification for evaluating AI-generated answers.

The full-response semantic similarity baseline performed poorly because it judged entire answers at once and missed partial errors. The sentence-level semantic similarity baseline improved diagnostic detail, but it still confused topical similarity with factual support.

Error analysis showed that the largest failure mode was contradiction missed due to topical overlap.

The Natural Language Inference verifier improved the system by directly modeling whether retrieved evidence supports, contradicts, or is neutral toward each claim. It achieved 79.3% accuracy on the labeled sentence-level dataset, outperforming both the full-response baseline and the sentence-level semantic similarity baseline.

The final deployed VeriClaim application turns the research pipeline into a usable AI tool. Users can paste an AI-generated answer or enter a question and let the app generate and verify an answer automatically.

Overall, VeriClaim shows that evidence-grounded, sentence-level verification can make AI-generated answers more transparent, inspectable, and trustworthy.

---

## Appendix A: Main Results Files

```text
results/method_comparison.csv
results/evaluation_report.csv
results/full_response_evaluation_report.csv
results/nli_evaluation_report.csv
results/confusion_matrix.csv
results/full_response_confusion_matrix.csv
results/nli_confusion_matrix.csv
results/final_error_analysis_summary.csv
```

---

## Appendix B: Main Figures

```text
results/figures/method_accuracy_comparison.png
results/figures/error_category_distribution.png
results/figures/sentence_level_confusion_matrix.png
results/figures/full_response_confusion_matrix.png
results/figures/nli_confusion_matrix.png
```

---

## Appendix C: Reproducibility

To run the Streamlit app locally:

```bash
python -m streamlit run app.py
```

To run the sentence-level semantic similarity baseline:

```bash
python src/semantic_similarity_baseline.py
```

To run the full-response baseline:

```bash
python src/full_response_baseline.py
```

To evaluate the NLI verifier:

```bash
python src/nli_verification_evaluation.py
```

To update the method comparison table:

```bash
python src/create_method_comparison.py
```

To regenerate result figures:

```bash
python src/create_result_figures.py
```

The deployed app is available at:

```text
https://vericlaim-ai.streamlit.app
```

---

## Appendix D: Resume Summary

A short resume version of this project could be:

**VeriClaim — Evidence-Grounded Verification for LLM-Generated Claims**  
Built and deployed a Streamlit-based AI verification system that splits LLM-generated answers into sentence-level claims, retrieves Wikipedia evidence, and classifies claims as Supported, Contradicted, or Insufficient Evidence using Natural Language Inference. Compared full-response similarity, sentence-level similarity, and NLI verification; improved accuracy from 58.6% with semantic similarity to 79.3% with NLI on 58 human-labeled claims. Added OpenAI API-based answer generation and deployed the final app publicly on Streamlit Cloud.

---

## Appendix E: Technologies Used

```text
Python
Streamlit
OpenAI API
Hugging Face Transformers
facebook/bart-large-mnli
Sentence-Transformers
spaCy
Wikipedia API
pandas
scikit-learn
matplotlib
Git
GitHub
Streamlit Community Cloud
```