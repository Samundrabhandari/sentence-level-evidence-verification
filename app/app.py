import os

import requests
import spacy
import streamlit as st
from openai import OpenAI
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline


# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="VeriClaim",
    page_icon="🔎",
    layout="wide",
)


# -----------------------------
# Cached model loading
# -----------------------------
@st.cache_resource
def load_spacy_model():
    """
    Load spaCy sentence splitter.
    Falls back to a blank English sentencizer if the small English model is unavailable.
    """
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        nlp = spacy.blank("en")
        nlp.add_pipe("sentencizer")
        return nlp


@st.cache_resource
def load_similarity_model():
    """
    Load sentence-transformer model for semantic similarity diagnostic score.
    """
    return SentenceTransformer("all-MiniLM-L6-v2")


@st.cache_resource
def load_nli_model():
    """
    Load Natural Language Inference model.
    This model predicts entailment, contradiction, or neutral.
    """
    return pipeline(
        "text-classification",
        model="facebook/bart-large-mnli",
        tokenizer="facebook/bart-large-mnli",
        top_k=None,
    )


nlp = load_spacy_model()
similarity_model = load_similarity_model()
nli_classifier = load_nli_model()


# -----------------------------
# OpenAI helper functions
# -----------------------------
def get_openai_api_key():
    """
    Read OpenAI API key from Streamlit secrets or environment variable.
    This keeps the key outside GitHub code.
    """
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
    except Exception:
        api_key = None

    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")

    return api_key


def generate_ai_answer(question):
    """
    Generate a short AI answer using the OpenAI API.
    """
    api_key = get_openai_api_key()

    if not api_key:
        st.error(
            "OpenAI API key is not configured. Add OPENAI_API_KEY in Streamlit secrets."
        )
        return ""

    client = OpenAI(api_key=api_key)

    prompt = f"""
Answer the following factual question in 2 to 3 short sentences.

Rules:
- Keep the answer factual and concise.
- Do not use bullet points.
- Do not mention that you are an AI.
- Do not include citations.
- Avoid long explanations.

Question:
{question}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=160,
        )

        return response.output_text.strip()

    except Exception as error:
        st.error(f"OpenAI answer generation failed: {error}")
        return ""


def generate_evidence_query(question, generated_answer):
    """
    Generate a short Wikipedia search query automatically.

    The query uses the user's question and the generated answer.
    This helps the app choose a useful Wikipedia page without requiring
    the user to manually enter an evidence query.
    """
    api_key = get_openai_api_key()

    if not api_key:
        st.error(
            "OpenAI API key is not configured. Add OPENAI_API_KEY in Streamlit secrets."
        )
        return ""

    client = OpenAI(api_key=api_key)

    prompt = f"""
Create the best short Wikipedia search query for verifying this generated answer.

Rules:
- Return only the search query.
- Do not write a sentence.
- Do not add quotation marks.
- Use the main entity, person, place, object, event, or topic.
- Keep it under 8 words.

Question:
{question}

Generated answer:
{generated_answer}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            max_output_tokens=40,
        )

        return response.output_text.strip()

    except Exception as error:
        st.error(f"Evidence query generation failed: {error}")
        return ""


# -----------------------------
# Verification helper functions
# -----------------------------
def split_into_sentences(text):
    """
    Split an answer into sentence-level claims.
    """
    doc = nlp(text)
    sentences = []

    for sent in doc.sents:
        sentence = sent.text.strip()
        if sentence:
            sentences.append(sentence)

    return sentences


def retrieve_wikipedia_evidence(query):
    """
    Retrieve a Wikipedia summary for the given evidence query.
    """
    if not query.strip():
        return "", "No evidence query provided."

    search_url = "https://en.wikipedia.org/w/api.php"

    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
    }

    try:
        search_response = requests.get(
            search_url,
            params=search_params,
            timeout=10,
            headers={"User-Agent": "VeriClaim research demo"},
        )
        search_response.raise_for_status()
        search_data = search_response.json()

        search_results = search_data.get("query", {}).get("search", [])

        if not search_results:
            return "", "No Wikipedia page found."

        page_title = search_results[0]["title"]

        summary_url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + page_title.replace(" ", "_")
        )

        summary_response = requests.get(
            summary_url,
            timeout=10,
            headers={"User-Agent": "VeriClaim research demo"},
        )
        summary_response.raise_for_status()
        summary_data = summary_response.json()

        evidence = summary_data.get("extract", "")

        if not evidence:
            return page_title, "No summary evidence found."

        return page_title, evidence

    except Exception as error:
        return "", f"Evidence retrieval failed: {error}"


def calculate_similarity(claim, evidence):
    """
    Calculate semantic similarity between claim and evidence.
    This is used only as a diagnostic score, not the final verdict.
    """
    if not evidence.strip():
        return 0.0

    claim_embedding = similarity_model.encode(claim, convert_to_tensor=True)
    evidence_embedding = similarity_model.encode(evidence, convert_to_tensor=True)

    similarity_score = util.cos_sim(claim_embedding, evidence_embedding).item()

    return similarity_score


def classify_with_nli(claim, evidence):
    """
    Classify whether evidence entails, contradicts, or is neutral toward a claim.
    """
    if not evidence.strip():
        return "neutral", {"entailment": 0.0, "contradiction": 0.0, "neutral": 1.0}

    result = nli_classifier(
        {
            "text": evidence,
            "text_pair": claim,
        }
    )

    if len(result) > 0 and isinstance(result[0], list):
        result = result[0]

    scores = {}

    for item in result:
        label = item["label"].lower()
        score = float(item["score"])
        scores[label] = score

    best_label = max(scores, key=scores.get)

    return best_label, scores


def get_final_verdict(nli_label, nli_scores, confidence_threshold):
    """
    Convert NLI model output into VeriClaim labels.
    """
    confidence = nli_scores.get(nli_label, 0.0)

    if confidence < confidence_threshold:
        return "INSUFFICIENT EVIDENCE"

    if nli_label == "entailment":
        return "SUPPORTED"

    if nli_label == "contradiction":
        return "CONTRADICTED"

    return "INSUFFICIENT EVIDENCE"


def show_verdict_box(verdict):
    """
    Display verdict with a clear color.
    """
    if verdict == "SUPPORTED":
        st.success("SUPPORTED")
    elif verdict == "CONTRADICTED":
        st.error("CONTRADICTED")
    else:
        st.warning("INSUFFICIENT EVIDENCE")


def verify_answer(answer, evidence_query, nli_confidence_threshold):
    """
    Full verification pipeline:
    answer -> sentence claims -> Wikipedia evidence -> similarity + NLI -> verdicts
    """
    claims = split_into_sentences(answer)

    if not claims:
        st.warning("No sentence-level claims found.")
        return

    page_title, evidence = retrieve_wikipedia_evidence(evidence_query)

    st.subheader("Retrieved Evidence")

    if page_title:
        st.write(f"**Wikipedia page:** {page_title}")

    st.write(evidence)

    st.divider()

    st.subheader("Sentence-Level Verification Results")

    for index, claim in enumerate(claims, start=1):
        with st.container(border=True):
            st.markdown(f"### Claim {index}")
            st.write(claim)

            similarity_score = calculate_similarity(claim, evidence)

            nli_label, nli_scores = classify_with_nli(claim, evidence)

            verdict = get_final_verdict(
                nli_label=nli_label,
                nli_scores=nli_scores,
                confidence_threshold=nli_confidence_threshold,
            )

            show_verdict_box(verdict)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "NLI confidence",
                    f"{nli_scores.get(nli_label, 0.0):.4f}",
                )

            with col2:
                st.metric(
                    "Semantic similarity",
                    f"{similarity_score:.4f}",
                )

            with col3:
                st.metric(
                    "NLI label",
                    nli_label,
                )

            with st.expander("View NLI scores"):
                st.json(nli_scores)

            with st.expander("View evidence used"):
                st.write(evidence)


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("Settings")

semantic_similarity_threshold = st.sidebar.number_input(
    "Semantic similarity threshold:",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
)

nli_confidence_threshold = st.sidebar.number_input(
    "NLI confidence threshold:",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
)

st.sidebar.markdown("**Main verdicts:**")
st.sidebar.markdown("- SUPPORTED")
st.sidebar.markdown("- CONTRADICTED")
st.sidebar.markdown("- INSUFFICIENT EVIDENCE")

st.sidebar.info(
    "This version uses Natural Language Inference for the main verdict "
    "and semantic similarity as a diagnostic score."
)


# -----------------------------
# Main UI
# -----------------------------
st.title("🔎 VeriClaim")

st.subheader("Evidence-Grounded Verification for LLM-Generated Claims")

st.write(
    "This demo checks whether individual sentences in an AI-generated answer are "
    "supported, contradicted, or not sufficiently supported by retrieved Wikipedia evidence."
)

st.warning(
    "Important: This tool does not determine absolute truth. "
    "It evaluates claims only against the retrieved evidence."
)

st.info(
    "How to interpret results: SUPPORTED means the retrieved evidence appears to support the claim. "
    "CONTRADICTED means the retrieved evidence appears inconsistent with the claim. "
    "INSUFFICIENT EVIDENCE means the retrieved evidence does not clearly support or contradict the claim."
)

st.divider()

st.header("Try VeriClaim")

input_mode = st.radio(
    "Choose input mode",
    [
        "Verify a pasted AI answer",
        "Generate an AI answer, then verify it",
    ],
)


# -----------------------------
# Mode 1: Verify pasted answer
# -----------------------------
if input_mode == "Verify a pasted AI answer":
    examples = {
        "Jupiter example: topical similarity can miss contradiction": {
            "question": "What is the largest planet in the Solar System?",
            "answer": (
                "Jupiter is the largest planet in the Solar System. "
                "It is a gas giant. "
                "Jupiter is smaller than Earth."
            ),
            "evidence_query": "Jupiter",
        },
        "Mount Everest example: contradiction detection": {
            "question": "Where is Mount Everest located?",
            "answer": (
                "Mount Everest is Earth's highest mountain above sea level. "
                "It lies in the Himalayas. "
                "Mount Everest is located in South America."
            ),
            "evidence_query": "Mount Everest",
        },
        "DNA example: unsupported biological claim": {
            "question": "What is DNA?",
            "answer": (
                "DNA carries genetic information in living organisms. "
                "DNA is made of amino acids."
            ),
            "evidence_query": "DNA",
        },
        "Custom input": {
            "question": "",
            "answer": "",
            "evidence_query": "",
        },
    }

    selected_example = st.selectbox(
        "Choose an example",
        list(examples.keys()),
    )

    default_question = examples[selected_example]["question"]
    default_answer = examples[selected_example]["answer"]
    default_evidence_query = examples[selected_example]["evidence_query"]

    question = st.text_input(
        "Question",
        value=default_question,
    )

    answer = st.text_area(
        "AI-generated answer to verify",
        value=default_answer,
        height=140,
    )

    evidence_query = st.text_input(
        "Evidence query for Wikipedia",
        value=default_evidence_query,
    )

    if st.button("Verify Answer"):
        if not answer.strip():
            st.warning("Please enter an AI-generated answer to verify.")
        elif not evidence_query.strip():
            st.warning("Please enter an evidence query.")
        else:
            verify_answer(
                answer=answer,
                evidence_query=evidence_query,
                nli_confidence_threshold=nli_confidence_threshold,
            )


# -----------------------------
# Mode 2: Generate answer, auto-query, verify
# -----------------------------
else:
    st.subheader("Ask a Question")

    question = st.text_input(
        "Enter a factual question",
        value="",
        placeholder="Example: What is Jupiter?",
    )

    st.caption(
        "This mode uses the OpenAI API to generate a short answer. "
        "Then VeriClaim automatically selects a Wikipedia evidence query and verifies the generated answer."
    )

    if st.button("Generate Answer and Verify"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Generating AI answer..."):
                generated_answer = generate_ai_answer(question)

            if generated_answer:
                with st.spinner("Selecting Wikipedia evidence query..."):
                    evidence_query = generate_evidence_query(
                        question=question,
                        generated_answer=generated_answer,
                    )

                if evidence_query:
                    st.subheader("Generated AI Answer")
                    st.write(generated_answer)

                    st.subheader("Automatically Selected Evidence Query")
                    st.code(evidence_query)

                    st.divider()

                    verify_answer(
                        answer=generated_answer,
                        evidence_query=evidence_query,
                        nli_confidence_threshold=nli_confidence_threshold,
                    )