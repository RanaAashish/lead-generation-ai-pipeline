from typing import List
import time
import json
import os
from googlesearch import search
import requests
from bs4 import BeautifulSoup
from config import Config

def search_yoga_schools(query, max_results=10):
    """Search for yoga schools using Google"""
    try:
        urls = []
        # Updated search parameters to match the current API
        for url in search(query, 
                         tld="com",  # Top level domain
                         num=max_results,  # Number of results
                         stop=max_results,  # Stop after max_results
                         pause=2):  # Delay between requests
            urls.append(url)
        return urls
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []

def get_content(url):
    """Get content from a URL"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Get text content
        text = ' '.join([p.text for p in soup.find_all('p')])
        return text
    except Exception as e:
        print(f"Error fetching content from {url}: {str(e)}")
        return None