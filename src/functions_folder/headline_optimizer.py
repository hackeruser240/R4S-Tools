# headline_optimizer.py

from textblob import TextBlob
from transformers import pipeline
import random

from functions_folder.APP_loggerSetup import app_loggerSetup
from functions_folder.LOCAL_loggerSetup import local_loggerSetup

logger = app_loggerSetup()

def score_headline(headline):
    """
    Scores a headline using sentiment and semantic fluency.

    Args:
        headline (str): The headline to evaluate.

    Returns:
        dict: Contains sentiment polarity, subjectivity, fluency score, and suggestions.
    """
    # Sentiment analysis
    blob = TextBlob(headline)
    polarity = round(blob.sentiment.polarity, 3)
    subjectivity = round(blob.sentiment.subjectivity, 3)

    # Fluency scoring using transformer
    fill_mask = pipeline("fill-mask", model="bert-base-uncased")
    tokens = headline.split()
    fluency_score = 0
    count = 0

    for i, token in enumerate(tokens):
        if token.isalpha():
            masked = tokens.copy()
            masked[i] = "[MASK]"
            masked_text = " ".join(masked)
            try:
                predictions = fill_mask(masked_text)
                top_words = [p['token_str'].strip() for p in predictions]
                if token.lower() in top_words:
                    fluency_score += 1
                count += 1
            except:
                continue

    fluency = round(fluency_score / count, 3) if count else 0.0

    # Suggestions (simple rewording)
    suggestions = []
    if polarity < 0.1:
        suggestions.append("Add emotional or action verbs to increase impact.")
    if subjectivity < 0.3:
        suggestions.append("Consider making the headline more opinionated or expressive.")
    if fluency < 0.5:
        suggestions.append("Rephrase for smoother readability or word choice.")

    improved = [
        headline.replace("new", "breakthrough"),
        headline.replace("AI", "intelligent system"),
        headline.replace("tool", "platform"),
        headline.replace("study", "report"),
    ]
    improved = list(set(improved))  # Remove duplicates

    return {
        "headline": headline,
        "polarity": polarity,
        "subjectivity": subjectivity,
        "fluency": fluency,
        "suggestions": suggestions,
        "improved_variants": random.sample(improved, min(3, len(improved)))
    }

# 🔧 Local test block
if __name__ == "__main__":
    logger=local_loggerSetup(use_filename=__file__)
    test_headline = "New AI tool revolutionizes genomic research"
    logger.info(f"{test_headline}")
    result = score_headline(test_headline)
    logger.info("\n==========Result==========\n")
    logger.info("Headline:", result["headline"])
    logger.info("Polarity:", result["polarity"])
    logger.info("Subjectivity:", result["subjectivity"])
    logger.info("Fluency Score:", result["fluency"])
    logger.info("Suggestions:", result["suggestions"])
    logger.info("Improved Variants:", result["improved_variants"])