from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from threading import Thread
import json

# Update imports to use relative paths
from .src.google_search import search_yoga_schools
from .src.url_cleaner import clean_urls
from .src.content_extractor import extract_website_content
from .src.llm_processor import process_website_data
from .src.email_extractor import extract_emails_from_structured_data
from .src.gmail_sender import GmailSender
from config import Config

main = Blueprint('main', __name__)

def process_leads_async(search_query, max_results):
    try:
        # Execute your existing pipeline
        fetch_urls = search_yoga_schools(search_query, max_results)
        cleaned_urls = clean_urls(fetch_urls)
        website_content = extract_website_content(cleaned_urls)
        structured_data = process_website_data(website_content)
        contacts = extract_emails_from_structured_data(structured_data)
        
        # Send emails
        gmail_sender = GmailSender()
        gmail_sender.send_partnership_emails(contacts)
        
        return True
    except Exception as e:
        print(f"Error in lead generation: {str(e)}")
        return False

@main.route('/')
def index():
    contacts = []
    try:
        file_path = 'lead-generation/data/processed/extracted_contacts.json'
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Extract the contacts from the nested structure
                contacts = data.get('contacts', [])
                print(f"Loaded contacts: {contacts}")  # Debug print
        else:
            print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error loading contacts: {str(e)}")
        
    return render_template('index.html', contacts=contacts)

@main.route('/process', methods=['POST'])
def process():
    try:
        data = request.get_json()
        print("Received query:", data)
        query = data.get('query')

        # Get URLs
        fetch_urls = search_yoga_schools(query)
        cleaned_urls = clean_urls(fetch_urls,output_dir="/home/aashish/repos/krishna-djembe/lead-generation/data/interim")
        website_content = extract_website_content(cleaned_urls,output_file="/home/aashish/repos/krishna-djembe/lead-generation/data/interim/website_content.json")
        structured_data = process_website_data(website_content,output_file="/home/aashish/repos/krishna-djembe/lead-generation/data/interim/LLM_processed_data.json",api_key=Config.OPENAI_API_KEY)
        contacts = extract_emails_from_structured_data(structured_data, output_dir="/home/aashish/repos/krishna-djembe/lead-generation/data/processed")
        
        # Since contacts is already a list of dictionaries, we can send it directly
        print("Final contacts data being sent:", contacts)
        return jsonify({
            'status': 'success',
            'contacts': contacts  # contacts is already a list of dictionaries
        })

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({
            'status': 'error',
            'error': str(e),
            'contacts': []
        }), 500

@main.route('/generate', methods=['POST'])
def generate_leads():
    search_query = request.form.get('search_query')
    max_results = int(request.form.get('max_results', 50))
    
    if not search_query:
        flash('Please enter a search query', 'danger')
        return redirect(url_for('main.index'))
    
    # Start processing in background
    thread = Thread(target=process_leads_async, args=(search_query, max_results))
    thread.start()
    
    flash('Lead generation process started! You will be notified when complete.', 'success')
    return redirect(url_for('main.index'))

@main.route('/status')
def status():
    # Add status checking logic here
    return jsonify({'status': 'processing'})