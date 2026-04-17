from ..src.google_search import search_yoga_schools
from ..src.url_cleaner import clean_urls
from config import Config
import json
import os
import argparse
from ..src.content_extractor import extract_website_content
from ..src.llm_processor import process_website_data
from ..src.email_extractor import extract_emails_from_structured_data
from ..src.gmail_sender import GmailSender
from app import app

def scrape_urls():
    """Scrape raw URLs and save to JSON"""
    config = Config()
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    
    raw_urls = search_yoga_schools(config.RAW_DATA_DIR)
    raw_output_file = os.path.join(config.RAW_DATA_DIR, 'yoga_schools.json')
    with open(raw_output_file, 'w') as f:
        json.dump({'urls': raw_urls}, f, indent=4)
    print(f"Raw results saved to: {raw_output_file}")
    print(f"Raw URLs found: {len(raw_urls)}")

def clean_url_data():
    """Clean URLs from JSON and save cleaned version"""
    config = Config()
    os.makedirs(config.INTERIM_DATA_DIR, exist_ok=True)
    
    # Read raw URLs from JSON
    raw_output_file = os.path.join(config.RAW_DATA_DIR, 'yoga_schools.json')
    with open(raw_output_file) as f:
        raw_data = json.load(f)
        raw_urls = raw_data['urls']
    
    # Clean and save URLs
    cleaned_urls = clean_urls(raw_urls, config.INTERIM_DATA_DIR)
    interim_output_file = os.path.join(config.INTERIM_DATA_DIR, 'cleaned_yoga_schools.json')
    with open(interim_output_file, 'w') as f:
        json.dump({'cleaned_urls': cleaned_urls}, f, indent=4)
    
    print(f"Cleaned unique URLs: {len(cleaned_urls)}")
    print(f"Cleaned results saved to: {interim_output_file}")

def extract_content():
    """Extract content from URLs and save to JSON"""
    config = Config()
    os.makedirs(config.INTERIM_DATA_DIR, exist_ok=True)
    
    # Read cleaned URLs from JSON
    interim_input_file = os.path.join(config.INTERIM_DATA_DIR, 'cleaned_yoga_schools.json')
    with open(interim_input_file) as f:
        cleaned_data = json.load(f)
        cleaned_urls = cleaned_data['cleaned_urls']
    
    # Extract content and save to JSON
    output_file = os.path.join(config.INTERIM_DATA_DIR, 'website_content.json')
    content_data = extract_website_content(cleaned_urls, output_file)
    
    print(f"Content extracted from {len(cleaned_urls)} URLs")
    print(f"Content saved to: {output_file}")

def process_content_LLM():
    """Process extracted content using LLM and save structured data"""
    config = Config()
    
    input_file = os.path.join(config.INTERIM_DATA_DIR, 'website_content.json')
    output_file = os.path.join(config.PROCESSED_DATA_DIR, 'structured_data.json')
    
    # Process content and extract structured information
    results = process_website_data(input_file, output_file, config.OPENAI_API_KEY)
    
    successful = len([r for r in results.values() if 'error' not in r])
    print(f"\nProcessed {len(results)} websites")
    print(f"Successfully extracted information from {successful} websites")
    print(f"Structured data saved to: {output_file}")

def extract_emails():
    """Extract emails from structured data and save to JSON"""
    config = Config()
    
    # Define input and output paths
    input_file = os.path.join(config.PROCESSED_DATA_DIR, 'structured_data.json')
    output_dir = config.PROCESSED_DATA_DIR
    
    # Extract and save emails
    recipients = extract_emails_from_structured_data(input_file, output_dir)
    
    if not recipients:
        print("No valid emails found")
    else:
        print(f"Successfully extracted {len(recipients)} email addresses")

def send_emails():
    """Send partnership emails to yoga schools"""
    config = Config()
    
    # Initialize Gmail sender
    try:
        gmail = GmailSender()
    except Exception as e:
        print(f"Error initializing Gmail sender: {e}")
        return
    
    # Send partnership emails
    structured_data_file = os.path.join(config.PROCESSED_DATA_DIR, 'structured_data.json')
    gmail.send_partnership_emails(structured_data_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['scrape', 'clean', 'extract', 'process', 'extract_emails','send_emails'])
    args = parser.parse_args()
    
    if args.action == 'scrape':
        scrape_urls()
    elif args.action == 'clean':
        clean_url_data()
    elif args.action == 'extract':
        extract_content()
    elif args.action == 'process':
        process_content_LLM()
    elif args.action == 'extract_emails':
        extract_emails()
    elif args.action == 'send_emails':
        send_emails()

if __name__ == '__main__':
    app.run(debug=True)
