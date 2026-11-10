import socket
import ipaddress
import urllib.parse
import re
import html

# Disallowed internal networks for SSRF protection
BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network('127.0.0.0/8'),        # Loopback
    ipaddress.ip_network('10.0.0.0/8'),         # Private A
    ipaddress.ip_network('172.16.0.0/12'),      # Private B
    ipaddress.ip_network('192.168.0.0/16'),     # Private C
    ipaddress.ip_network('169.254.0.0/16'),     # Link-local / AWS metadata
    ipaddress.ip_network('0.0.0.0/8'),          # Current network
    ipaddress.ip_network('224.0.0.0/4'),        # Multicast
    ipaddress.ip_network('240.0.0.0/4'),        # Reserved
    ipaddress.ip_network('::1/128'),            # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),           # IPv6 unique local
    ipaddress.ip_network('fe80::/10'),          # IPv6 link-local
]

def is_safe_url(url: str) -> tuple[bool, str]:
    """Validates URL against SSRF attacks and ensures safe HTTP/HTTPS destination."""
    if not url or not isinstance(url, str):
        return False, "URL is empty or invalid."
    
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme.lower() not in ('http', 'https'):
        return False, "Invalid protocol scheme. Only HTTP and HTTPS are permitted."
    
    hostname = parsed.hostname
    if not hostname:
        return False, "URL missing valid hostname."
    
    # Block local keywords directly
    if hostname.lower() in ('localhost', 'localhost.localdomain', '127.0.0.1', '::1', 'metadata.google.internal'):
        return False, "Access to localhost and internal loopback addresses is strictly forbidden."
    
    try:
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False, f"Resolved IP {ip_str} belongs to a restricted internal network address."
    except Exception as e:
        return False, f"Could not resolve host: {str(e)}"
    
    return True, "URL validated safely."

def sanitize_text(text: str, max_chars: int = 50000) -> str:
    """Sanitizes text by escaping HTML entities and limiting character payload."""
    if not text:
        return ""
    # Strip dangerous HTML script tags
    cleaned = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'<style.*?>.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = html.escape(cleaned.strip())
    return cleaned[:max_chars]

def validate_input_length(text: str, min_chars: int = 10, max_chars: int = 50000) -> tuple[bool, str]:
    """Validates submitted text length for analysis."""
    if not text or len(text.strip()) < min_chars:
        return False, f"Submitted content is too brief. Please enter at least {min_chars} characters for credible linguistic analysis."
    if len(text) > max_chars:
        return False, f"Submitted content exceeds maximum limit of {max_chars} characters."
    return True, "Input length valid."
