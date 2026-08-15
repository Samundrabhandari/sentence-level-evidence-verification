import time
from urllib.parse import quote

import requests
import spacy
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline


# -----------------------------
# App settings
# -----------------------------
SIMILARITY_THRESHOLD = 0.50
NLI_CONFIDENCE_THRESHOLD = 0.50

SIMILARITY_MODEL_NAME = "all-MiniLM-L6-v2"
NLI_MODEL_NAME = "facebook/bart-large-mnli"

HEADERS = {
    "User-Agent": "VeriClaim/1.0 student research demo"
}


# -----------------------------
# Example inputs
# -----------------------------
EXAMPLES = {
    "Jupiter example: topical similarity can miss contradiction": {
        "question": "What is the largest planet in the Solar System?",
        "ai_answer": (
            "Jupiter is the largest planet in the Solar System. "
            "It is a gas giant. "
            "Jupiter is smaller than Earth."
        ),
        "evidence_query": "Jupiter",
    },
    "Alexander Graham Bell example": {
        "question": "Who invented the telephone?",
        "ai_answer": (
            "Alexander Graham Bell is widely credited with inventing the telephone. "
            "He received a patent in 1876. "
            "He was born in Italy."
        ),
        "evidence_query": "Alexander Graham Bell",
    },
    "DNA example: unsupported biological claim": {
        "question": "What is DNA?",
        "ai_answer": (
            "DNA stands for deoxyribonucleic acid. "
            "It carries genetic information in living organisms. "
            "DNA is made of amino acids."
        ),
        "evidence_query": "DNA",
    },
    "Mount Everest example: location error": {
        "question": "What is the tallest mountain above sea level?",
        "ai_answer": (
            "Mount Everest is the tallest mountain above sea level. "
            "It is located in the Himalayas. "
            "Mount Everest is located in South America."
        ),
        "evidence_query": "Mount Everest",
    },
    "Custom input": {
        "question": "",
        "ai_answer": "",
        "evidence_query": "",
    },
}


# -----------------------------
# Cached models
# -----------------------------
@st.cache_resource
def load_spacy_model():
    """
    Load spaCy English model once and reuse it.
    """
    return spacy.load("en_core_web_sm")


@st.cache_resource
def load_similarity_model():
    """
    Load sentence-transformer model once and reuse it.
    """
    return SentenceTransformer(SIMILARITY_MODEL_NAME)


@st.cache_resource
def load_nli_model():
    """
    Load Natural Language Inference model once and reuse it.

    NLI compares:
    - premise: retrieved evidence
    - hypothesis: claim

    It predicts:
    - entailment
    - contradiction
    - neutral
    """
    return pipeline(
        "text-classification",
        model=NLI_MODEL_NAME,
        tokenizer=NLI_MODEL_NAME,
        top_k=None,
    )


# -----------------------------
# Core functions
# -----------------------------
def split_into_sentences(text):
    """
    Split an AI-generated answer into sentence-level claims.
    """
    nlp = load_spacy_model()
    doc = nlp(text)

    sentences = []

    for sentence in doc.sents:
        clean_sentence = sentence.text.strip()
        if clean_sentence:
            sentences.append(clean_sentence)

    return sentences


def get_json_from_url(url, params=None):
    """
    Safely request JSON data from Wikipedia.
    """
    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            time.sleep(5)
            return None

        return None

    except requests.RequestException:
        return None


@st.cache_data(show_spinner=False)
def search_wikipedia(query):
    """
    Search Wikipedia and return the top page title.
    """
    search_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1,
    }

    data = get_json_from_url(search_url, params=params)

    if data is None:
        return None

    results = data.get("query", {}).get("search", [])

    if len(results) == 0:
        return None

    return results[0]["title"]


@st.cache_data(show_spinner=False)
def get_wikipedia_summary(title):
    """
    Retrieve a Wikipedia page summary.
    """
    if title is None:
        return "", ""

    safe_title = quote(title.replace(" ", "_"))
    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}"

    data = get_json_from_url(summary_url)

    if data is None:
        return "", ""

    evidence = data.get("extract", "")
    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

    return evidence, page_url


def calculate_similarity(sentence, evidence):
    """
    Calculate cosine similarity between a sentence and retrieved evidence.
    """
    model = load_similarity_model()

    sentence_embedding = model.encode(sentence, convert_to_tensor=True)
    evidence_embedding = model.encode(evidence, convert_to_tensor=True)

    similarity = util.cos_sim(sentence_embedding, evidence_embedding).item()

    return similarity


def classify_with_nli(evidence, claim):
    """
    Use Natural Language Inference to classify the relationship between evidence and claim.

    Evidence = premise
    Claim = hypothesis
    """
    classifier = load_nli_model()

    result = classifier(
        {
            "text": evidence,
            "text_pair": claim,
        }
    )

    # Different transformers versions may return slightly different nesting.
    if len(result) > 0 and isinstance(result[0], list):
        result = result[0]

    scores = {}

    for item in result:
        label = item["label"].lower()
        score = float(item["score"])
        scores[label] = score

    entailment_score = scores.get("entailment", 0.0)
    contradiction_score = scores.get("contradiction", 0.0)
    neutral_score = scores.get("neutral", 0.0)

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    if best_label == "entailment" and best_score >= NLI_CONFIDENCE_THRESHOLD:
        verdict = "SUPPORTED"
    elif best_label == "contradiction" and best_score >= NLI_CONFIDENCE_THRESHOLD:
        verdict = "CONTRADICTED"
    else:
        verdict = "INSUFFICIENT EVIDENCE"

    return {
        "verdict": verdict,
        "best_label": best_label,
        "confidence": round(best_score, 4),
        "entailment_score": round(entailment_score, 4),
        "contradiction_score": round(contradiction_score, 4),
        "neutral_score": round(neutral_score, 4),
    }


def verify_answer(ai_answer, evidence_query):
    """
    Run the verification workflow for one AI-generated answer.
    """
    sentences = split_into_sentences(ai_answer)

    wiki_title = search_wikipedia(evidence_query)
    evidence, wiki_url = get_wikipedia_summary(wiki_title)

    results = []

    for sentence in sentences:
        if evidence.strip() == "":
            similarity_score = 0.0
            nli_result = {
                "verdict": "INSUFFICIENT EVIDENCE",
                "best_label": "no_evidence",
                "confidence": 0.0,
                "entailment_score": 0.0,
                "contradiction_score": 0.0,
                "neutral_score": 0.0,
            }
        else:
            similarity_score = calculate_similarity(sentence, evidence)
            nli_result = classify_with_nli(evidence, sentence)

        results.append(
            {
                "claim": sentence,
                "verdict": nli_result["verdict"],
                "nli_best_label": nli_result["best_label"],
                "nli_confidence": nli_result["confidence"],
                "entailment_score": nli_result["entailment_score"],
                "contradiction_score": nli_result["contradiction_score"],
                "neutral_score": nli_result["neutral_score"],
                "similarity_score": round(similarity_score, 4),
                "wiki_title": wiki_title,
                "evidence": evidence,
                "wiki_url": wiki_url,
            }
        )

    return results


def load_selected_example():
    """
    Load the selected example into the input fields.
    """
    selected_example = st.session_state.selected_example

    if selected_example == "Custom input":
        st.session_state.question = ""
        st.session_state.ai_answer = ""
        st.session_state.evidence_query = ""
        return

    example = EXAMPLES[selected_example]

    st.session_state.question = example["question"]
    st.session_state.ai_answer = example["ai_answer"]
    st.session_state.evidence_query = example["evidence_query"]


def display_verdict(verdict):
    """
    Display verdict using Streamlit status boxes.
    """
    if verdict == "SUPPORTED":
        st.success("SUPPORTED")
    elif verdict == "CONTRADICTED":
        st.error("CONTRADICTED")
    else:
        st.warning("INSUFFICIENT EVIDENCE")


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="VeriClaim",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 VeriClaim")
st.subheader("Evidence-Grounded Verification for LLM-Generated Claims")

st.markdown(
    """
    This demo checks whether individual sentences in an AI-generated answer are
    supported, contradicted, or not sufficiently supported by retrieved Wikipedia evidence.

    **Important:** This tool does not determine absolute truth. It evaluates claims only against the retrieved evidence.
    """
)

st.info(
    "How to interpret results: SUPPORTED means the retrieved evidence appears to support the claim. "
    "CONTRADICTED means the retrieved evidence appears inconsistent with the claim. "
    "INSUFFICIENT EVIDENCE means the retrieved evidence does not clearly support or contradict the claim."
)

with st.sidebar:
    st.header("Settings")

    st.write("Semantic similarity threshold:")
    st.code(str(SIMILARITY_THRESHOLD))

    st.write("NLI confidence threshold:")
    st.code(str(NLI_CONFIDENCE_THRESHOLD))

    st.markdown(
        """
        Main verdicts:

        - **SUPPORTED**
        - **CONTRADICTED**
        - **INSUFFICIENT EVIDENCE**

        This version uses Natural Language Inference for the main verdict and semantic similarity as a diagnostic score.
        """
    )

st.divider()

# Initialize session state
if "selected_example" not in st.session_state:
    st.session_state.selected_example = "Jupiter example: topical similarity can miss contradiction"

if "question" not in st.session_state:
    st.session_state.question = EXAMPLES[st.session_state.selected_example]["question"]

if "ai_answer" not in st.session_state:
    st.session_state.ai_answer = EXAMPLES[st.session_state.selected_example]["ai_answer"]

if "evidence_query" not in st.session_state:
    st.session_state.evidence_query = EXAMPLES[st.session_state.selected_example]["evidence_query"]


st.subheader("Try an Example or Enter Your Own")

st.selectbox(
    "Choose an example",
    options=list(EXAMPLES.keys()),
    key="selected_example",
    on_change=load_selected_example,
)

question = st.text_input(
    "Question",
    key="question",
)

ai_answer = st.text_area(
    "AI-generated answer to verify",
    key="ai_answer",
    height=130,
)

evidence_query = st.text_input(
    "Evidence query for Wikipedia",
    key="evidence_query",
)

verify_button = st.button("Verify Answer", type="primary")

if verify_button:
    if ai_answer.strip() == "":
        st.error("Please enter an AI-generated answer.")
    elif evidence_query.strip() == "":
        st.error("Please enter an evidence query.")
    else:
        with st.spinner("Retrieving evidence and running NLI verification..."):
            verification_results = verify_answer(ai_answer, evidence_query)

        if len(verification_results) == 0:
            st.warning("No sentences were found in the answer.")
        else:
            supported_count = sum(
                1 for item in verification_results
                if item["verdict"] == "SUPPORTED"
            )

            contradicted_count = sum(
                1 for item in verification_results
                if item["verdict"] == "CONTRADICTED"
            )

            insufficient_count = sum(
                1 for item in verification_results
                if item["verdict"] == "INSUFFICIENT EVIDENCE"
            )

            total_claims = len(verification_results)

            st.success("Verification complete.")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Sentence-level claims", total_claims)
            col2.metric("Supported", supported_count)
            col3.metric("Contradicted", contradicted_count)
            col4.metric("Insufficient evidence", insufficient_count)

            st.warning(
                "Important: These verdicts are evidence-grounded, not absolute truth judgments. "
                "If the retrieved Wikipedia evidence is incomplete or wrong, the verdict may also be unreliable."
            )

            st.divider()

            first_result = verification_results[0]

            st.subheader("Retrieved Evidence")

            st.write("Wikipedia page:", first_result["wiki_title"])

            if first_result["wiki_url"]:
                st.write(first_result["wiki_url"])

            if first_result["evidence"]:
                st.info(first_result["evidence"])
            else:
                st.warning("No Wikipedia evidence was retrieved.")

            st.divider()

            st.subheader("Sentence-Level Verification Results")

            for index, item in enumerate(verification_results, start=1):
                with st.container(border=True):
                    st.markdown(f"### Claim {index}")
                    st.write(item["claim"])

                    display_verdict(item["verdict"])

                    metric_col1, metric_col2, metric_col3 = st.columns(3)

                    metric_col1.metric(
                        "NLI confidence",
                        item["nli_confidence"],
                    )

                    metric_col2.metric(
                        "Semantic similarity",
                        item["similarity_score"],
                    )

                    metric_col3.metric(
                        "NLI label",
                        item["nli_best_label"],
                    )

                    with st.expander("View NLI scores"):
                        st.write("Entailment score:", item["entailment_score"])
                        st.write("Contradiction score:", item["contradiction_score"])
                        st.write("Neutral score:", item["neutral_score"])

                    with st.expander("View evidence used"):
                        st.write(item["evidence"])