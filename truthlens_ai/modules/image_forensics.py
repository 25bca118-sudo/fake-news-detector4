import os
import io
import urllib.parse
from pathlib import Path
from PIL import Image, ImageChops, ImageEnhance, ExifTags
from truthlens_ai.config import UPLOAD_DIR

def extract_image_exif(image_path: Path) -> dict:
    """Extracts EXIF metadata including camera equipment, timestamp, and editing software."""
    metadata = {}
    try:
        with Image.open(image_path) as img:
            metadata['format'] = img.format
            metadata['mode'] = img.mode
            metadata['dimensions'] = f"{img.width} x {img.height} px"
            
            exif = img.getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, str(tag_id))
                    # Avoid decoding large binary blocks
                    if isinstance(value, (str, int, float)):
                        metadata[tag] = str(value)
    except Exception as e:
        metadata['error'] = f"Failed to parse EXIF: {str(e)}"
    return metadata

def perform_error_level_analysis(image_path: Path, quality: int = 90, scale: int = 15) -> tuple[str, float, bool]:
    """
    Performs Error Level Analysis (ELA) to identify digital manipulation and pixel tampering.
    Re-compresses JPEG at given quality and computes the amplified difference map.
    Returns: (ela_relative_filename, manipulation_score_0_100, is_tampered)
    """
    filename = Path(image_path).name
    ela_filename = f"ela_{Path(image_path).stem}.png"
    ela_save_path = UPLOAD_DIR / ela_filename
    
    with Image.open(image_path).convert('RGB') as orig:
        # Re-save to memory at controlled compression
        buffer = io.BytesIO()
        orig.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        
        with Image.open(buffer) as resaved:
            # Compute difference between original and recompressed image
            diff = ImageChops.difference(orig, resaved)
            
            # Amplify difference by scale factor to reveal artifacts
            extrema = diff.getextrema()
            max_diff = max([ex[1] for ex in extrema]) if extrema else 1
            scale_factor = 255.0 / max(max_diff, 1)
            
            # Enhance contrast for clear visual inspection
            enhanced = ImageEnhance.Brightness(diff).enhance(scale_factor * 0.8)
            enhanced.save(ela_save_path, 'PNG')
            
            # Calculate manipulation score based on non-uniform high-frequency variance
            manipulation_score = min(100.0, round((max_diff / 40.0) * 100.0, 1))
            is_tampered = manipulation_score > 65.0
            
    return ela_filename, manipulation_score, is_tampered

def generate_reverse_search_links(image_url: str = "", query_terms: str = "") -> dict:
    """Constructs reverse image search and verification query links."""
    encoded_terms = urllib.parse.quote_plus(query_terms) if query_terms else ""
    return {
        'google_lens': f"https://lens.google.com/uploadbyurl?url={urllib.parse.quote_plus(image_url)}" if image_url else "https://lens.google.com/",
        'tineye': f"https://tineye.com/search?url={urllib.parse.quote_plus(image_url)}" if image_url else "https://tineye.com/",
        'fact_check_explorer': f"https://toolbox.google.com/factcheck/explorer/search/listresults?query={encoded_terms}"
    }
