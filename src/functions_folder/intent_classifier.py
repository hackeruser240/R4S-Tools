# File: functions_folder/intent_classifier.py

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sentence_transformers import SentenceTransformer
from collections import Counter
from tabulate import tabulate

bert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load or train classifier
try:
    clf = joblib.load('intent_model.pkl')
except FileNotFoundError:
    sample_texts = ["buy MOF membrane", "how does crystallization work?", "login issue"]
    sample_labels = ["purchase", "informational", "support"]
    X_train = bert_model.encode(sample_texts)
    clf = LogisticRegression()
    clf.fit(X_train, sample_labels)
    joblib.dump(clf, 'intent_model.pkl')

def classify_intents(text_list):
    embeddings = bert_model.encode(text_list)
    predictions = clf.predict(embeddings)
    return {text: intent for text, intent in zip(text_list, predictions)}

def summarize_intents(intent_dict):
    """
    Displays a table of input → intent and prints intent counts.
    Args:
        intent_dict (dict): Mapping of input text to predicted intent
    """
    # Tabular display
    table = [[text, intent] for text, intent in intent_dict.items()]
    print("\n📊 Intent Classification Table:")
    print(tabulate(table, headers=["Input Text", "Predicted Intent"], tablefmt="grid"))

    # Count summary
    counts = Counter(intent_dict.values())
    print("\n📈 Intent Counts:")
    for intent, count in counts.items():
        print(f"{intent}: {count}")

# 🔧 Local test block
if __name__ == '__main__':
    test_inputs = [
        "need help with login",
        "purchase MOF membrane",
        "what is crystallization",
        "how to install Flask on Windows",
        "I want to buy a gas separation unit",
        "reset my password",
        "benefits of mixed-linker synthesis",
        "contact customer support",
        "download latest research on MOF membranes",
        "schedule a demo for crystallization tech",
        "troubleshooting substrate contamination",
        "pricing for silica transformation kits",
        "find nearest distributor in Lahore",
        "difference between vapor-phase and solution-phase synthesis",
        "report a bug in the web interface"
    ]
    results = classify_intents(test_inputs)
    summarize_intents(results)