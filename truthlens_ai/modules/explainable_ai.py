import re
import html
from truthlens_ai.modules.ml_detector import get_loaded_models

def explain_prediction(text: str) -> dict:
    """
    Computes feature attribution and token-level influences for Explainable AI (XAI).
    Highlights words that push predictions toward 'Genuine' (green) or 'Fake' (red).
    """
    models = get_loaded_models()
    vectorizer = models['vectorizer']
    lr_model = models['logistic']
    
    feature_names = vectorizer.get_feature_names_out()
    coefs = lr_model.coef_[0] # Positive -> Genuine (1), Negative -> Fake (0)
    coef_dict = {feature_names[i]: float(coefs[i]) for i in range(len(feature_names))}
    
    # Tokenize input into words preserving punctuation for rendering
    tokens_with_delimiters = re.findall(r'\b\w+\b|\s+|[^\w\s]', text)
    
    highlighted_tokens = []
    word_attributions = []
    
    for token in tokens_with_delimiters:
        token_clean = token.lower().strip()
        weight = coef_dict.get(token_clean, 0.0)
        
        # Categorize influence
        if weight > 0.08:
            token_type = "genuine_influencer" # Green
            css_class = "xai-genuine"
        elif weight < -0.08:
            token_type = "fake_influencer"    # Red
            css_class = "xai-fake"
        else:
            token_type = "neutral"
            css_class = "xai-neutral"
            
        highlighted_tokens.append({
            'text': html.escape(token),
            'type': token_type,
            'weight': round(weight, 3),
            'css_class': css_class
        })
        
        if token_clean and abs(weight) > 0.05 and token.isalpha():
            word_attributions.append({
                'word': token_clean,
                'weight': round(weight, 3),
                'direction': 'Genuine' if weight > 0 else 'Fake / Misleading'
            })
            
    # Deduplicate top words by absolute weight
    unique_words = {}
    for item in word_attributions:
        w = item['word']
        if w not in unique_words or abs(item['weight']) > abs(unique_words[w]['weight']):
            unique_words[w] = item
            
    sorted_words = sorted(unique_words.values(), key=lambda x: abs(x['weight']), reverse=True)[:10]
    
    # Generate inline HTML highlighted representation
    rendered_html = "".join([
        f"<span class='{t['css_class']}' title='Influence: {t['weight']}'>{t['text']}</span>"
        if t['type'] != 'neutral' else t['text']
        for t in highlighted_tokens
    ])
    
    return {
        'rendered_html': rendered_html,
        'top_influential_terms': sorted_words,
        'total_tokens_analyzed': len(tokens_with_delimiters),
        'disclaimer': "Linguistic attribution highlights reflect statistical model sensitivity patterns and vocabulary associations. Highlighted terms serve as explanatory indicators and do not independently prove factual veracity."
    }
