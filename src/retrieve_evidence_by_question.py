import pandas as pd
import requests
import time
from urllib.parse import quote


HEADERS = {
    "User-Agent": "SentenceVerificationResearch/1.0 student research project"
}


def get_json_from_url(url, params=None):
    """
    Send a request to Wikipedia and safely return JSON data.
    """
    for attempt in range(3):
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=15
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 429:
            wait_time = 10 * (attempt + 1)
            print(f"Rate limited. Waiting {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            print("Request error:", response.status_code)
            return None

    return None


def search_wikipedia(query):
    """
    Search Wikipedia using the evidence_query column.
    """
    search_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": 1
    }

    data = get_json_from_url(search_url, params=params)

    if data is None:
        return None

    results = data.get("query", {}).get("search", [])

    if len(results) == 0:
        return None

    return results[0]["title"]


def get_wikipedia_summary(title):
    """
    Get summary evidence from a Wikipedia page.
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


input_file = "results/sentence_level_output.csv"
df = pd.read_csv(input_file)

evidence_rows = []
query_cache = {}

for index, row in df.iterrows():
    answer_id = row["answer_id"]
    question = row["question"]
    evidence_query = row["evidence_query"]
    sentence_id = row["sentence_id"]
    sentence = row["sentence"]

    if evidence_query not in query_cache:
        print(f"Searching Wikipedia for evidence query: {evidence_query}")

        wiki_title = search_wikipedia(evidence_query)
        evidence, page_url = get_wikipedia_summary(wiki_title)

        query_cache[evidence_query] = {
            "wiki_title": wiki_title,
            "wiki_evidence": evidence,
            "wiki_url": page_url
        }

        time.sleep(6)

    cached = query_cache[evidence_query]

    evidence_rows.append({
        "answer_id": answer_id,
        "question": question,
        "evidence_query": evidence_query,
        "sentence_id": sentence_id,
        "sentence": sentence,
        "wiki_title": cached["wiki_title"],
        "wiki_evidence": cached["wiki_evidence"],
        "wiki_url": cached["wiki_url"]
    })


evidence_df = pd.DataFrame(evidence_rows)

output_file = "results/sentence_with_question_evidence.csv"
evidence_df.to_csv(output_file, index=False)

print("Done! Evidence saved to:", output_file)
print(evidence_df[["answer_id", "sentence_id", "sentence", "wiki_title"]])