# content_gap_finder.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

from functions_folder.APP_loggerSetup import app_loggerSetup
from functions_folder.LOCAL_loggerSetup import local_loggerSetup

logger = app_loggerSetup()

def find_content_gaps(your_text, competitor_texts, top_n=10):
    """
    Detect missing topics using TF-IDF and BERT embeddings.

    Args:
        your_text (str): Your page content.
        competitor_texts (list of str): List of competitor page contents.
        top_n (int): Number of top gaps to return.

    Returns:
        list of dict: Each dict contains 'term', 'tfidf_score', 'semantic_score'
    """
    # TF-IDF comparison
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    combined_texts = competitor_texts + [your_text]
    tfidf_matrix = vectorizer.fit_transform(combined_texts)
    feature_names = vectorizer.get_feature_names_out()

    # Get average competitor TF-IDF
    comp_tfidf = np.mean(tfidf_matrix[:-1].toarray(), axis=0)
    your_tfidf = tfidf_matrix[-1].toarray()[0]
    tfidf_diff = comp_tfidf - your_tfidf

    # BERT semantic comparison
    model = SentenceTransformer('all-MiniLM-L6-v2')
    your_embedding = model.encode([your_text], convert_to_tensor=True)
    semantic_scores = {}

    for idx, term in enumerate(feature_names):
        term_embedding = model.encode([term], convert_to_tensor=True)
        score = cosine_similarity(term_embedding.cpu().numpy(), your_embedding.cpu().numpy())[0][0]
        semantic_scores[term] = score

    # Combine scores
    gaps = []
    for idx, term in enumerate(feature_names):
        if tfidf_diff[idx] > 0:
            gaps.append({
                'term': term,
                'tfidf_score': round(tfidf_diff[idx], 4),
                'semantic_score': round(semantic_scores[term], 4)
            })

    # Sort by combined relevance
    sorted_gaps = sorted(gaps, key=lambda x: (x['tfidf_score'], 1 - x['semantic_score']), reverse=True)
    return sorted_gaps[:top_n]

# 🔧 Local test block
if __name__ == "__main__":
    logger=local_loggerSetup(use_filename=__file__)
    your_text = "We offer cloud-based data analytics and scalable infrastructure solutions."
    competitor_texts = [
        "Our platform provides AI-driven insights, predictive modeling, and real-time dashboards.",
        "We specialize in machine learning, big data pipelines, and cloud-native architecture."
    ]
    result = find_content_gaps(your_text, competitor_texts, top_n=5)
    for item in result:
        logger.info(f"{item['term']} | TF-IDF Gap: {item['tfidf_score']} | Semantic Similarity: {item['semantic_score']}")