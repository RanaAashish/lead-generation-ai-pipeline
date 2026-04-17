# lead-generation-ai-pipeline

Krishna Djembe is an automated lead generation system focused on yoga schools in Rishikesh. It scrapes and processes website data, applies LLM-based analysis to extract key insights, and enables personalized outreach through integrated email.

The project showcases how AI and automation can be used to build scalable data pipelines for lead generation system.

## Key Highlights

- Built an end-to-end data pipeline from scraping to outreach
- Processed and analyzed unstructured website data using LLMs
- Automated personalized communication workflows (Email + WhatsApp)
- Applied real-world use case for lead generation

## Features

- **Web Scraping**: Automated collection of yoga school information
- **Data Processing**: Cleaning and structuring of collected data
- **LLM Analysis**: AI-powered content analysis using GPT-4
- **Communication**:
  - Automated email sending via Gmail API
  - WhatsApp messaging integration
- **Data Storage**: Organized data pipeline (raw → interim → processed)

## Project Structure

```
krishna-djembe/
├── src/                    # Source code
│   ├── scraping/          # Web scraping modules
│   │   ├── google_search.py
│   │   └── website_scraper.py
│   ├── processing/        # Data processing modules
│   │   ├── url_cleaner.py
│   │   └── content_extractor.py
│   ├── analysis/          # Analysis modules
│   │   ├── llm_processor.py
│   │   └── data_analyzer.py
│   ├── communication/     # Communication modules
│   │   ├── gmail_sender.py
│   │   └── whatsapp_sender.py
│   └── utils/             # Utility functions
│       └── config.py
├── data/                  # Data files
│   ├── raw/              # Raw scraped data
│   ├── interim/          # Intermediate data
│   └── processed/        # Final processed data
├── notebooks/            # Jupyter notebooks
├── tests/                # Unit tests
├── credentials/          # API credentials (gitignored)
├── .env                  # Environment variables
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## 🚀 Setup Guide

### Prerequisites

- Python 3.9+
- Git
- Google Cloud account (for Gmail API)
- OpenAI API key

### 1. Clone the Repository

```bash
git clone https://github.com/RanaAashish/krishna-djembe.git
cd krishna-djembe
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create `.env` file in the root directory:

```env
# API Keys
OPENAI_API_KEY=your_openai_key_here

# File Paths
DATA_DIR=data
RAW_DATA_DIR=data/raw
INTERIM_DATA_DIR=data/interim
PROCESSED_DATA_DIR=data/processed

# Scraping Settings
MAX_RESULTS=100
SEARCH_DELAY=2

# Gmail Configuration
GMAIL_CREDENTIALS_FILE=credentials/gmail_credentials.json
GMAIL_TOKEN_FILE=credentials/token.pickle
GMAIL_SENDER_EMAIL=your.email@gmail.com
```

### 5. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials and save as `credentials/gmail_credentials.json`
6. First run will open browser for authentication

## Usage

### Web Scraping

```python
# Scrape yoga school data
from src.scraping.google_search import search_yoga_schools
from src.scraping.website_scraper import scrape_websites

# Search for yoga schools
urls = search_yoga_schools()

# Scrape website content
website_data = scrape_websites(urls)
```

### Data Processing

```python
from src.processing.url_cleaner import clean_urls
from src.processing.content_extractor import extract_content

# Clean URLs
cleaned_urls = clean_urls(urls)

# Extract relevant content
processed_data = extract_content(website_data)
```

### Email Communication

```python
from src.communication.gmail_sender import GmailSender

# Initialize sender
gmail = GmailSender()

# Send bulk emails
recipients = [
    {
        'email': 'example@email.com',
        'name': 'John Doe',
        'yoga_school': 'Himalayan Yoga',
        'course': '200 Hour YTT'
    }
]

gmail.send_bulk_emails(
    recipients=recipients,
    subject_template="Course Inquiry - {yoga_school}",
    message_template="Dear {name},\n\nInquiring about {course}..."
)
```

### Updating Environment Variables

1. Add new variable to `.env`
2. Update `src/utils/config.py`
3. Update documentation

## Security Notes

- Never commit `.env` file
- Keep API keys secure
- Regularly rotate credentials
- Use `.gitignore` for sensitive files

## Contact

Aashish Rana - [aashish.rana.27@gmail.com](mailto:aashish.rana.27@gmail.com)
