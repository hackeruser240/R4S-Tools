# File: functions_folder/schema_generator.py

import spacy
import json
from typing import Dict

# Load spaCy model (English by default)
nlp = spacy.load("en_core_web_sm")

def generate_schema_ld(text: str, schema_type: str = "Article") -> Dict:
    doc = nlp(text)
    
    # Extract named entities
    entities = []
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_
        })

    # Basic schema structure
    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": text[:60] + "..." if len(text) > 60 else text,
        "description": text[:160] + "..." if len(text) > 160 else text,
        "entityMap": entities
    }

    # Optional enrichment
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            schema["author"] = ent.text
        elif ent.label_ == "ORG":
            schema["publisher"] = ent.text
        elif ent.label_ == "GPE":
            schema["location"] = ent.text
        elif ent.label_ == "DATE":
            schema["datePublished"] = ent.text

    return schema

# 🔬 Local test harness
if __name__ == "__main__":
    sample_text = """
    On September 15, 2025, Dr. Lena Morales submitted her final report titled "Genomic Drift in Isolated Populations" to the Bioinformatics Review Board. The document included 42 annotated datasets, each tagged with a unique identifier and timestamp. Her team, based in Oslo, Norway, used a hybrid pipeline combining UMI-based consensus sequencing and Bayesian error correction. The project cost was estimated at $128,400, with a projected completion date of March 2026. For inquiries, contact lena.morales@genomehub.org.
    """
    schema = generate_schema_ld(sample_text, schema_type="Article")
    print(json.dumps(schema, indent=2))