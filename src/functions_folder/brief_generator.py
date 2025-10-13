# brief_generator.py

from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline
import random

from functions_folder.APP_loggerSetup import app_loggerSetup
from functions_folder.LOCAL_loggerSetup import local_loggerSetup

logger = app_loggerSetup()

def generate_brief(seed_text, faq_count=5):
    """
    Generates a structured outline and FAQs from a seed topic or paragraph.

    Args:
        seed_text (str): Topic or seed paragraph.
        faq_count (int): Number of FAQs to generate.

    Returns:
        dict: Contains H1, H2s, H3s, and FAQs.
    """
    # Extract keywords using TF-IDF
    vectorizer = TfidfVectorizer(stop_words='english', max_features=30)
    tfidf_matrix = vectorizer.fit_transform([seed_text])
    keywords = vectorizer.get_feature_names_out()
    keywords = [kw for kw in keywords if len(kw) > 3]  # Filter short tokens

    # Headings
    h1 = f"Overview of {keywords[0].capitalize()}" if keywords else "Overview"
    h2s = [f"What is {kw}?" for kw in keywords[1:4]]
    h3s = [f"Benefits of {kw}" for kw in keywords[4:7]]

    # FAQ generation using prompt conditioning
    generator = pipeline("text-generation", model="gpt2")
    faqs = []
    selected_keywords = random.sample(keywords, min(faq_count, len(keywords)))
    for kw in selected_keywords:
        prompt = f"Based on the topic '{seed_text}', what should I know about {kw}?"
        try:
            answer = generator(prompt, max_length=80, do_sample=False)[0]['generated_text']
            answer_clean = answer.replace(prompt, "").strip()
            faqs.append({
                "question": f"What should I know about {kw}?",
                "answer": answer_clean
            })
        except Exception:
            faqs.append({
                "question": f"What should I know about {kw}?",
                "answer": "Content generation failed. Try refining the topic."
            })

    return {
        "h1": h1,
        "h2": h2s,
        "h3": h3s,
        "faqs": faqs
    }

# 🔧 Local test block
if __name__ == "__main__":
    logger=local_loggerSetup(use_filename=__file__)
    seed = "CRISPR technology in cancer therapy and its applications in precision medicine"
    result = generate_brief(seed, faq_count=3)
    logger.info("H1:", result["h1"])
    logger.info("H2s:", result["h2"])
    logger.info("H3s:", result["h3"])
    logger.info("\nFAQs:")
    for faq in result["faqs"]:
        logger.info(f"Q: {faq['question']}\nA: {faq['answer']}\n")