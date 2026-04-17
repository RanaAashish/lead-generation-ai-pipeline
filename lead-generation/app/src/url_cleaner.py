import re
from typing import List
import json
import os

def clean_urls(urls: List[str], output_dir: str) -> List[str]:
    """
    Clean and normalize URLs, removing duplicates
    
    Args:
        urls: List of URLs to clean
        output_dir: Directory to store any debug information
        
    Returns:
        List of cleaned, unique URLs
    """
    # Using the same pattern from the notebook
    pattern = re.compile(r"(https?://[a-zA-Z0-9.-]+?(\.com|\.in|\.org))(/.*)?")
    unique_urls = set()
    duplicates_found = False
    skipped_urls = []
    
    print(f"Starting with {len(urls)} raw URLs")
    
    for url in urls:
        if not url:  # Skip empty URLs
            continue
            
        url = url.strip()
        match = pattern.match(url)
        
        if match:
            # Use the same cleaning logic from notebook
            cleaned_url = match.group(1) + '/'
            if cleaned_url in unique_urls:
                duplicates_found = True
            else:
                unique_urls.add(cleaned_url)
        else:
            skipped_urls.append(url)
            print(f"Skipped URL (didn't match pattern): {url}")
    
    # Save debug information
    debug_info = {
        'total_input_urls': len(urls),
        'cleaned_urls_count': len(unique_urls),
        'skipped_urls_count': len(skipped_urls),
        'skipped_urls': skipped_urls,
        'duplicates_found': duplicates_found
    }
    
    debug_file = os.path.join(output_dir, 'url_cleaning_debug.json')
    with open(debug_file, 'w') as f:
        json.dump(debug_info, f, indent=4)
    
    sorted_urls = sorted(list(unique_urls))
    print(f"Cleaned {len(sorted_urls)} unique URLs")
    if duplicates_found:
        print("Duplicate URLs were found and removed.")
    print(f"Debug information saved to: {debug_file}")
    
    return sorted_urls