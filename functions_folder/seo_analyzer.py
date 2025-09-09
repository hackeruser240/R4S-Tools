import requests
from bs4 import BeautifulSoup
import spacy
from keybert import KeyBERT
from collections import Counter

nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

def seo_analyzer(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
    except Exception as e:
        return {'error': f"Failed to fetch URL: {e}"}

    soup = BeautifulSoup(html_content, 'html.parser')

    # Meta tags
    title = soup.title.string if soup.title else ''
    description = soup.find('meta', attrs={'name': 'description'})
    keywords = soup.find('meta', attrs={'name': 'keywords'})

    meta_info = {
        'title': title.strip() if title else '',
        'description': description['content'].strip() if description and description.get('content') else '',
        'keywords': keywords['content'].strip() if keywords and keywords.get('content') else ''
    }

    # Headings
    headings = {
        'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
        'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
        'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
    }

    # Text content for keyword density
    text = soup.get_text(separator=' ', strip=True)
    doc = nlp(text.lower())
    words = [token.text for token in doc if token.is_alpha and not token.is_stop]
    word_freq = Counter(words)
    top_keywords = word_freq.most_common(10)

    # KeyBERT semantic keywords
    keybert_keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=10)

    return {
        'meta': meta_info,
        'headings': headings,
        'keyword_density': top_keywords,
        'keybert_keywords': keybert_keywords
    }