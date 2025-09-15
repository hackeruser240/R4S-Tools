# File: functions_folder/topic_modeler.py

import numpy as np
from typing import List, Dict, Optional
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sentence_transformers import SentenceTransformer
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from gensim.parsing.preprocessing import preprocess_string, strip_punctuation, strip_numeric, remove_stopwords
import matplotlib.pyplot as plt
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis

# 🧹 Text Cleaning
def clean_texts(texts: List[str]) -> List[List[str]]:
    CUSTOM_FILTERS = [lambda x: x.lower(), strip_punctuation, strip_numeric, remove_stopwords]
    return [preprocess_string(text, CUSTOM_FILTERS) for text in texts]

# 📚 LDA Topic Modeling
def lda_topic_modeling(texts: List[str], num_topics: int = 5):
    cleaned = clean_texts(texts)
    dictionary = corpora.Dictionary(cleaned)
    corpus = [dictionary.doc2bow(text) for text in cleaned]
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=num_topics, random_state=42)
    
    topics = []
    for i, topic in lda.show_topics(num_topics=num_topics, formatted=False):
        keywords = [word for word, _ in topic]
        assigned_texts = [texts[j] for j, bow in enumerate(corpus) if any(word_id in dict(bow) for word_id in [dictionary.token2id.get(k) for k in keywords if k in dictionary.token2id])]
        topics.append({"topic_id": i, "keywords": keywords, "texts": assigned_texts})
    
    return topics, lda, corpus, dictionary

# 🧠 BERT Topic Modeling
def bert_topic_modeling(texts: List[str], num_clusters: Optional[int] = None):
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
    
    return topics, embeddings, labels

# 📊 Visualization Function
def visualize_topics(method: str, lda_model=None, corpus=None, dictionary=None, embeddings=None, labels=None):
    if method == "lda":
        vis_data = gensimvis.prepare(lda_model, corpus, dictionary)
        pyLDAvis.save_html(vis_data, "lda_visualization.html")
        print("✅ LDA visualization saved as lda_visualization.html")
    elif method == "bert":
        tsne = TSNE(n_components=2, perplexity=3, random_state=42)
        reduced = tsne.fit_transform(embeddings)
        plt.figure(figsize=(8, 6))
        plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='tab10')
        plt.title("BERT Embedding Clusters")
        plt.savefig("bert_clusters.png")
        print("✅ BERT cluster plot saved as bert_clusters.png")

# 🧪 Local Test Harness
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

    method = "lda"  # Choose "lda" or "bert"
    viz = True       # Toggle visualization

    if method == "lda":
        topics, lda_model, corpus, dictionary = lda_topic_modeling(sample_texts, num_topics=3)
        for topic in topics:
            print(f"\nTopic {topic['topic_id']}:")
            print("Keywords:", topic['keywords'])
            print("Texts:", topic['texts'])
        if viz:
            visualize_topics("lda", lda_model=lda_model, corpus=corpus, dictionary=dictionary)

    elif method == "bert":
        topics, embeddings, labels = bert_topic_modeling(sample_texts, num_clusters=3)
        for topic in topics:
            print(f"\nCluster {topic['topic_id']}:")
            print("Keywords:", topic['keywords'])
            print("Texts:", topic['texts'])
        if viz:
            visualize_topics("bert", embeddings=embeddings, labels=labels)