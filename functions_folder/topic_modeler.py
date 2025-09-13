# File: functions_folder/topic_modeler.py

import numpy as np
from typing import List, Dict, Optional
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.parsing.preprocessing import preprocess_string, strip_punctuation, strip_numeric, remove_stopwords

def clean_texts(texts: List[str]) -> List[List[str]]:
    CUSTOM_FILTERS = [lambda x: x.lower(), strip_punctuation, strip_numeric, remove_stopwords]
    return [preprocess_string(text, CUSTOM_FILTERS) for text in texts]

def lda_topic_modeling(texts: List[str], num_topics: int = 5) -> List[Dict]:
    cleaned = clean_texts(texts)
    dictionary = corpora.Dictionary(cleaned)
    corpus = [dictionary.doc2bow(text) for text in cleaned]
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=42)
    
    topics = []
    for i, topic in lda.show_topics(num_topics=num_topics, formatted=False):
        keywords = [word for word, _ in topic]
        assigned_texts = [texts[j] for j, bow in enumerate(corpus) if any(word_id in dict(bow) for word_id in [dictionary.token2id.get(k) for k in keywords if k in dictionary.token2id])]
        topics.append({"topic_id": i, "keywords": keywords, "texts": assigned_texts})
    return topics

def bert_topic_modeling(texts: List[str], num_clusters: Optional[int] = None) -> List[Dict]:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(texts)
    
    if not num_clusters:
        num_clusters = max(2, int(len(texts) / 5))
    
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    
    topics = []
    for cluster_id in range(num_clusters):
        cluster_texts = [texts[i] for i in range(len(texts)) if labels[i] == cluster_id]
        centroid = kmeans.cluster_centers_[cluster_id]
        keywords = [texts[i] for i in np.argsort(np.dot(embeddings, centroid))[-5:][::-1]]
        topics.append({
            "topic_id": cluster_id,
            "texts": cluster_texts,
            "keywords": keywords
        })
    return topics

# 🔬 Local test harness
if __name__ == "__main__":
    sample_texts = [
        "Crystallization techniques for organic semiconductors",
        "SEO optimization strategies for Flask applications",
        "Host–guest chemistry using cucurbiturils",
        "Deploying Python tools in cPanel environments",
        "Thin film deposition and substrate engineering",
        "Keyword mapping for patent literature synthesis",
        "Docker troubleshooting in automation pipelines"
    ]

    print("🔍 LDA Topic Modeling:")
    lda_results = lda_topic_modeling(sample_texts, num_topics=3)
    for topic in lda_results:
        print(f"\nTopic {topic['topic_id']}:")
        print("Keywords:", topic['keywords'])
        print("Texts:", topic['texts'])

    print("\n🧠 BERT Topic Modeling:")
    bert_results = bert_topic_modeling(sample_texts, num_clusters=3)
    for topic in bert_results:
        print(f"\nCluster {topic['topic_id']}:")
        print("Keywords:", topic['keywords'])
        print("Texts:", topic['texts'])