# File: content_scorer.py

import textstat
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

# Load model once at module level
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

def interpret_scores(readability, similarity):
    if readability > 60 and similarity > 0.8:
        return "Content is readable and highly relevant."
    elif readability < 40:
        return "Content is difficult to read."
    elif similarity < 0.5:
        return "Content may not align well with the target topic."
    else:
        return "Content is moderately readable and somewhat relevant."
    
def content_scorer(content: str, reference: str) -> dict:
    # Readability metrics
    readability_score = textstat.flesch_reading_ease(content)
    grade_level = textstat.text_standard(content, float_output=True)

    # Semantic similarity
    def embed(text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1)
        return embeddings.squeeze().numpy()

    content_vec = embed(content)
    reference_vec = embed(reference)
    similarity = np.dot(content_vec, reference_vec) / (
        np.linalg.norm(content_vec) * np.linalg.norm(reference_vec)
    )

    return {
        "readability_score": round(readability_score, 2),
        "grade_level": round(grade_level, 2),
        "semantic_similarity": round(float(similarity), 3),
        "summary": interpret_scores(readability_score, similarity)
    }
    

if __name__=="__main__":
    input="Explore our whole aresnal of tools,providing a comprehensive range of features to enhance a website's visibility and performance on search engines.By leveraging our diverse range of AIO tools, businesses and website owners can develop a robust strategy to improve their online presence, attract organic traffic, and stay competitive in the digital landscape."
    
    reference = "Explore our whole aresnal of tools,providing a comprehensive range of features to enhance a website's visibility and performance on search engines.By leveraging our diverse range of AIO tools, businesses and website owners can develop a robust strategy to improve their online presence, attract organic traffic, and stay competitive in the digital landscape."

    result = content_scorer(input, reference)
    print("Readability Score:", result["readability_score"])
    print("Grade Level:", result["grade_level"])
    print("Semantic Similarity:", result["semantic_similarity"])
    print("Summary:", result["summary"])
