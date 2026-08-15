from transformers import pipeline


MODEL_NAME = "facebook/bart-large-mnli"

classifier = pipeline(
    "text-classification",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME,
    top_k=None
)


def classify_claim(evidence, claim):
    """
    Use an NLI model to classify whether evidence supports,
    contradicts, or is neutral toward a claim.
    """
    result = classifier({
        "text": evidence,
        "text_pair": claim
    })

    # Some transformers versions return [ [ {...}, {...} ] ]
    # Others return [ {...}, {...} ]
    if len(result) > 0 and isinstance(result[0], list):
        result = result[0]

    scores = {}

    for item in result:
        label = item["label"].lower()
        score = item["score"]
        scores[label] = score

    best_label = max(scores, key=scores.get)

    return best_label, scores


evidence = (
    "Mount Everest is Earth's highest mountain above sea level. "
    "It lies in the Himalayas on the border between Nepal and China."
)

claims = [
    "Mount Everest is located in the Himalayas.",
    "Mount Everest is located in South America.",
    "Mount Everest is made of chocolate."
]

for claim in claims:
    label, scores = classify_claim(evidence, claim)

    print()
    print("Claim:", claim)
    print("Predicted NLI label:", label)
    print("Scores:", scores)