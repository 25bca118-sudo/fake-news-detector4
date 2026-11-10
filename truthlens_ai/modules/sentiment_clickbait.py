import json
import re
from truthlens_ai.config import DATA_DIR

_LEXICON_CACHE = None

def get_emotion_lexicon():
    global _LEXICON_CACHE
    if _LEXICON_CACHE is None:
        lexicon_file = DATA_DIR / 'emotion_lexicon.json'
        with open(lexicon_file, 'r', encoding='utf-8') as f:
            _LEXICON_CACHE = json.load(f)
    return _LEXICON_CACHE

# Positive & Negative valence dictionaries for rule-based sentiment
POSITIVE_WORDS = {
    'breakthrough', 'success', 'benefit', 'triumph', 'progress', 'cure', 'verified', 'approved',
    'growth', 'record', 'improve', 'promising', 'stable', 'effective', 'recovery', 'milestone',
    'clean', 'innovative', 'award', 'excellence', 'peace', 'vital', 'sustainable'
}
NEGATIVE_WORDS = {
    'danger', 'death', 'crisis', 'collapse', 'corrupt', 'scandal', 'disaster', 'threat', 'ruin',
    'fake', 'hoax', 'fraud', 'illegal', 'crime', 'warning', 'panic', 'poison', 'fatal', 'destroy',
    'catastrophe', 'conspiracy', 'arrest', 'banned', 'furious', 'evil', 'terrible'
}

def analyze_sentiment_and_emotion(text: str) -> dict:
    """Analyzes sentiment polarity, subjectivity, and 5-dimensional emotional tone."""
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = max(len(words), 1)
    
    pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)
    
    # Polarity (-1.0 to +1.0)
    net_val = pos_count - neg_count
    polarity = max(-1.0, min(1.0, round(net_val / max(pos_count + neg_count, 1), 2))) if (pos_count + neg_count) > 0 else 0.0
    
    if polarity > 0.15:
        sentiment_label = "Positive"
    elif polarity < -0.15:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral / Objective"
        
    subjectivity = min(1.0, round((pos_count + neg_count + text.count('!')) / (total_words * 0.4 + 1), 2))
    
    # Emotion Breakdown
    lex = get_emotion_lexicon()
    emotions = {
        'anger': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'surprise': 0
    }
    for category in emotions.keys():
        terms = lex.get(category, [])
        matches = sum(1 for w in words if w in terms)
        emotions[category] = matches
        
    total_emotion_hits = sum(emotions.values())
    if total_emotion_hits > 0:
        emotion_pcts = {k: round((v / total_emotion_hits) * 100, 1) for k, v in emotions.items()}
    else:
        emotion_pcts = {'anger': 10.0, 'fear': 10.0, 'joy': 20.0, 'sadness': 10.0, 'surprise': 50.0}
        
    dominant_emotion = max(emotion_pcts.items(), key=lambda x: x[1])[0].capitalize()
    
    return {
        'sentiment_label': sentiment_label,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'dominant_emotion': dominant_emotion,
        'emotion_distribution': emotion_pcts
    }

def detect_clickbait(text: str) -> dict:
    """Calculates Clickbait and Sensationalism Index (0-100)."""
    lex = get_emotion_lexicon()
    triggers = lex.get('clickbait_triggers', [])
    lower_t = text.lower()
    
    trigger_hits = [t for t in triggers if t in lower_t]
    
    # Punctuation signals
    excl_score = min(30, text.count('!') * 10)
    quest_score = min(20, text.count('?') * 10)
    
    # Uppercase words count
    words = text.split()
    caps_count = sum(1 for w in words if w.isupper() and len(w) > 2 and w.isalpha())
    caps_score = min(30, caps_count * 8)
    
    trigger_score = min(40, len(trigger_hits) * 20)
    
    clickbait_index = min(100, excl_score + quest_score + caps_score + trigger_score)
    
    if clickbait_index >= 70:
        rating = "Extreme Clickbait / High Sensationalism"
    elif clickbait_index >= 40:
        rating = "Moderate Clickbait Elements"
    else:
        rating = "Standard Journalistic Phrasing"
        
    return {
        'clickbait_score': clickbait_index,
        'rating': rating,
        'trigger_phrases_detected': trigger_hits,
        'exclamation_count': text.count('!'),
        'all_caps_words': caps_count
    }
