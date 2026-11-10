import re

# Unicode script ranges for Indian regional languages
SCRIPT_RANGES = {
    'hi': (0x0900, 0x097F, 'Hindi (Devanagari)'),
    'kn': (0x0C80, 0x0CFF, 'Kannada'),
    'ta': (0x0B80, 0x0BFF, 'Tamil'),
    'te': (0x0C00, 0x0C7F, 'Telugu'),
    'bn': (0x0980, 0x09FF, 'Bengali'),
    'ml': (0x0D00, 0x0D7F, 'Malayalam')
}

# Regional phrase translations for common fake/genuine keywords
REGIONAL_KEYWORDS = {
    'hi': {
        'चमत्कारी': 'miracle', 'दवा': 'medicine', 'कैंसर': 'cancer', 'रहस्य': 'secret',
        'सनसनीखेज': 'sensational', 'वैज्ञानिक': 'scientific', 'पुष्टि': 'confirmed',
        'इसरो': 'ISRO', 'मंत्रालय': 'Ministry', 'सरकार': 'Government', 'रोक': 'banned'
    },
    'kn': {
        'ಪವಾಡ': 'miracle', 'ರಹಸ್ಯ': 'secret', 'ಕ್ಯಾನ್ಸರ್': 'cancer', 'ಔಷಧಿ': 'medicine',
        'ಸರ್ಕಾರ': 'Government', 'ದೃಢಪಡಿಸಿದೆ': 'confirmed', 'ವಿಜ್ಞಾನಿಗಳು': 'scientists',
        'ಸುದ್ದಿ': 'news', 'ವೈರಲ್': 'viral'
    }
}

def detect_language(text: str) -> dict:
    """Detects script and language of submitted content."""
    if not text:
        return {'code': 'en', 'name': 'English', 'is_regional': False}
        
    script_counts = {}
    for char in text:
        cp = ord(char)
        for code, (start, end, name) in SCRIPT_RANGES.items():
            if start <= cp <= end:
                script_counts[code] = script_counts.get(code, 0) + 1
                
    if script_counts:
        top_code = max(script_counts.items(), key=lambda x: x[1])[0]
        name = SCRIPT_RANGES[top_code][2]
        return {'code': top_code, 'name': name, 'is_regional': True}
        
    return {'code': 'en', 'name': 'English', 'is_regional': False}

def process_multilingual_text(text: str) -> dict:
    """Normalizes regional text and extracts contextual English semantic equivalents for classification."""
    lang_info = detect_language(text)
    
    if not lang_info['is_regional']:
        return {
            'language': lang_info,
            'processed_text': text,
            'translated_terms': []
        }
        
    code = lang_info['code']
    lex = REGIONAL_KEYWORDS.get(code, {})
    translated_terms = []
    normalized_text = text
    
    for regional_word, en_word in lex.items():
        if regional_word in text:
            translated_terms.append({'regional': regional_word, 'english': en_word})
            normalized_text = normalized_text.replace(regional_word, f"{regional_word} ({en_word})")
            
    return {
        'language': lang_info,
        'processed_text': normalized_text,
        'translated_terms': translated_terms
    }
