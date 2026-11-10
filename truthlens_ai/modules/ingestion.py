import urllib.parse
import requests
from bs4 import BeautifulSoup
from truthlens_ai.modules.security import is_safe_url

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 TruthLensAI/1.0"

def extract_article_from_url(url: str) -> dict:
    """Safely extracts article title, metadata, author, publication date, and text from a news URL."""
    safe, msg = is_safe_url(url)
    if not safe:
        return {'success': False, 'error': f"Security Alert: {msg}", 'data': None}
    
    parsed = urllib.parse.urlparse(url)
    domain = parsed.hostname.lower() if parsed.hostname else ""
    if domain.startswith("www."):
        domain = domain[4:]
        
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return {'success': False, 'error': "The request timed out while attempting to reach the server.", 'data': None}
    except requests.exceptions.SSLError:
        return {'success': False, 'error': "SSL Certificate verification failed on destination server.", 'data': None}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f"Failed to retrieve URL: {str(e)}", 'data': None}
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Remove non-content elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'noscript', 'form']):
        element.decompose()
        
    # Extract Title
    title = ""
    og_title = soup.find('meta', property='og:title') or soup.find('meta', attrs={'name': 'twitter:title'})
    if og_title and og_title.get('content'):
        title = og_title['content'].strip()
    elif soup.find('h1'):
        title = soup.find('h1').get_text().strip()
    elif soup.title:
        title = soup.title.get_text().strip()
        
    # Extract Publication Date
    pub_date = ""
    time_tag = soup.find('time') or soup.find('meta', property='article:published_time') or soup.find('meta', attrs={'name': 'pubdate'})
    if time_tag:
        pub_date = time_tag.get('datetime') or time_tag.get('content') or time_tag.get_text().strip()
        
    # Extract Author / Publisher
    author = ""
    author_tag = soup.find('meta', attrs={'name': 'author'}) or soup.find('meta', property='article:author')
    if author_tag and author_tag.get('content'):
        author = author_tag['content'].strip()
        
    # Extract Main Body Paragraphs
    paragraphs = []
    # Try finding article tag first
    article_elem = soup.find('article') or soup.find('main') or soup
    for p in article_elem.find_all('p'):
        text = p.get_text().strip()
        if len(text.split()) > 4: # Filter navigation crumbs
            paragraphs.append(text)
            
    full_text = " ".join(paragraphs).strip()
    
    if len(full_text) < 40 and not title:
        return {
            'success': False,
            'error': "Could not extract sufficient text content from this page. The site may be protected by an aggressive paywall or JavaScript client-rendering. Please copy and paste the article text manually.",
            'data': None
        }
        
    return {
        'success': True,
        'error': None,
        'data': {
            'url': url,
            'domain': domain,
            'title': title or "Untitled News Article",
            'author': author or "Staff Reporter / Unknown",
            'publication_date': pub_date or "Not specified",
            'content': full_text,
            'word_count': len(full_text.split()),
            'extracted_paragraphs_count': len(paragraphs)
        }
    }
