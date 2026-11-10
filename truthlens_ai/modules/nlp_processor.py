import re
import string
import joblib
from pathlib import Path
from truthlens_ai.config import MODELS_DIR

# Common English stopwords
STOPWORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd",
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
    'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
    'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
    'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
    "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't"
}

KNOWN_ENTITIES = {
    'organizations': ['NASA', 'ISRO', 'WHO', 'UN', 'RBI', 'FDA', 'CDC', 'EU', 'NATO', 'Supreme Court', 'World Bank', 'IMF', 'Cabinet', 'Parliament'],
    'domains': ['Politics', 'Health', 'Science', 'Technology', 'Business', 'Defense', 'Environment']
}

def clean_text(text: str) -> str:
    """Performs standard NLP text cleaning and normalization."""
    if not text:
        return ""
    # Lowercase
    cleaned = text.lower()
    # Remove URLs
    cleaned = re.sub(r'https?://\S+|www\.\S+', '', cleaned)
    # Remove HTML markup
    cleaned = re.sub(r'<.*?>', '', cleaned)
    # Remove punctuation
    cleaned = cleaned.translate(str.maketrans('', '', string.punctuation))
    # Normalize extra whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def tokenize_and_filter(text: str) -> list[str]:
    """Tokenizes text and filters out stopwords."""
    cleaned = clean_text(text)
    tokens = cleaned.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 2]

def extract_named_entities(raw_text: str) -> dict:
    """Extracts named entities (Organizations, Acronyms, Capitalized proper nouns)."""
    if not raw_text:
        return {'organizations': [], 'key_terms': []}
        
    found_orgs = []
    for org in KNOWN_ENTITIES['organizations']:
        if re.search(r'\b' + re.escape(org) + r'\b', raw_text, re.IGNORECASE):
            found_orgs.append(org)
            
    # Extract multi-word proper capitalized sequences (e.g., 'James Webb', 'Shaktikanta Das')
    prop_matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', raw_text)
    # Deduplicate while preserving order
    seen = set()
    key_terms = []
    for term in prop_matches:
        if term not in seen and len(term) > 4:
            seen.add(term)
            key_terms.append(term)
            
    return {
        'organizations': list(set(found_orgs)),
        'key_terms': key_terms[:8]
    }

def analyze_linguistic_features(raw_text: str) -> dict:
    """Computes comprehensive linguistic and stylometric features."""
    if not raw_text:
        return {}
        
    words = raw_text.split()
    total_words = len(words)
    if total_words == 0:
        return {}
        
    sentences = re.split(r'[.!?]+', raw_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 0]
    total_sentences = max(len(sentences), 1)
    
    # Lexical Diversity (Type-Token Ratio)
    clean_words = [w.lower().strip(string.punctuation) for w in words if w]
    unique_words = len(set(clean_words))
    lexical_diversity = round((unique_words / max(total_words, 1)) * 100, 1)
    
    # Stylometric markers
    exclamation_count = raw_text.count('!')
    question_count = raw_text.count('?')
    uppercase_words = sum(1 for w in words if w.isupper() and len(w) > 1 and w.isalpha())
    all_caps_ratio = round((uppercase_words / total_words) * 100, 1)
    avg_sentence_len = round(total_words / total_sentences, 1)
    
    return {
        'word_count': total_words,
        'sentence_count': total_sentences,
        'avg_sentence_length': avg_sentence_len,
        'lexical_diversity_pct': lexical_diversity,
        'exclamation_count': exclamation_count,
        'question_count': question_count,
        'all_caps_word_ratio': all_caps_ratio
    }

def get_tfidf_features(text: str):
    """Loads TF-IDF vectorizer and transforms input text."""
    vec_path = MODELS_DIR / 'tfidf_vectorizer.pkl'
    if not vec_path.exists():
        raise FileNotFoundError("TF-IDF Vectorizer model artifact not found. Please train models first.")
    vectorizer = joblib.load(vec_path)
    return vectorizer, vectorizer.transform([text])
