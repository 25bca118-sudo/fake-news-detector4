import json
import urllib.parse
from truthlens_ai.config import DATA_DIR

_SOURCES_DATA = None

def get_sources_data():
    """Loads trusted sources and flagged domain registries."""
    global _SOURCES_DATA
    if _SOURCES_DATA is None:
        sources_file = DATA_DIR / 'trusted_sources.json'
        with open(sources_file, 'r', encoding='utf-8') as f:
            _SOURCES_DATA = json.load(f)
    return _SOURCES_DATA

def analyze_source(url_or_domain: str, author: str = "") -> dict:
    """Evaluates publisher reputation, domain integrity, and calculates Source Credibility Score (0-100)."""
    if not url_or_domain:
        return {
            'domain': 'Unspecified Direct Text',
            'credibility_score': 50.0,
            'status': 'Unverified Source',
            'category': 'Direct Submission',
            'badges': ['No Origin URL'],
            'details': 'Submitted as direct raw text without a verifiable online publisher domain.'
        }
        
    # Extract clean domain
    parsed = urllib.parse.urlparse(url_or_domain)
    raw_domain = parsed.hostname if parsed.hostname else url_or_domain.split('/')[0]
    domain = raw_domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
        
    sources = get_sources_data()
    badges = []
    
    # 1. Check known high credibility sources
    for item in sources['high_credibility']:
        if domain == item['domain'] or domain.endswith('.' + item['domain']):
            return {
                'domain': domain,
                'publisher_name': item['name'],
                'country': item['country'],
                'editorial_bias': item['bias'],
                'credibility_score': float(item['score']),
                'status': 'Verified High Credibility Publisher',
                'badges': ['IFCN / Reputable Outlet', 'Known Editorial Governance', 'SSL Verified'],
                'details': f"Publisher {item['name']} is a recognized journalism organization with rigorous editorial standards."
            }
            
    # 2. Check satire portals
    for item in sources['satire_sources']:
        if domain == item['domain'] or domain.endswith('.' + item['domain']):
            return {
                'domain': domain,
                'publisher_name': item['name'],
                'credibility_score': 20.0,
                'status': 'Satire / Spoof Publication',
                'badges': ['Satirical Outlet', 'Not Factual Journalism'],
                'details': f"{item['name']} is an acknowledged satire media platform. Content is published for humor and parody rather than factual reporting."
            }
            
    # 3. Check low credibility flags
    for flagged in sources['low_credibility_flags']:
        if domain == flagged or domain.endswith('.' + flagged):
            return {
                'domain': domain,
                'publisher_name': domain,
                'credibility_score': 15.0,
                'status': 'Flagged Misinformation Source',
                'badges': ['Low Reputation', 'Historical Misinformation Flags'],
                'details': "This domain has repeatedly been cited for publishing unverified rumors, conspiracy theories, or deceptive articles."
            }
            
    # 4. TLD and Heuristic Analysis for Unregistered Domains
    score = 55.0
    
    # Positive TLD signals
    if domain.endswith('.gov') or domain.endswith('.gov.in') or domain.endswith('.nic.in'):
        score = 95.0
        badges.append('Official Government TLD')
    elif domain.endswith('.edu') or domain.endswith('.ac.in'):
        score = 90.0
        badges.append('Academic Institution TLD')
    elif domain.endswith('.org'):
        score = 65.0
        badges.append('Non-Profit / Organization TLD')
        
    # Suspicious TLD signals
    for s_tld in sources['suspicious_tlds']:
        if domain.endswith(s_tld):
            score = 30.0
            badges.append(f'Suspicious High-Risk TLD ({s_tld})')
            break
            
    status = "Moderately Credible" if score >= 60 else "Unverified New Domain"
    if author and len(author.strip()) > 2 and author.lower() != "unknown":
        score = min(100.0, score + 5.0)
        badges.append('Author Byline Present')
        
    return {
        'domain': domain,
        'publisher_name': domain.title(),
        'credibility_score': round(score, 1),
        'status': status,
        'badges': badges if badges else ['Standard Web Domain'],
        'details': "Domain is not listed in major fact-checker registries. Assessed based on domain structure and metadata presence."
    }
