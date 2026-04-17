import json
import os
from typing import Dict, Any, Optional
from openai import OpenAI
import tiktoken
from config import Config
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import re

def count_tokens(text: str) -> int:
    """Count tokens in the given text using GPT-4 tokenizer"""
    try:
        enc = tiktoken.encoding_for_model("gpt-4")
        return len(enc.encode(text))
    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

def create_extraction_prompt(context: str) -> str:
    """Create a structured prompt for extracting website information"""
    prompt = f"""Extract key information about the yoga school/ashram from the following website content.
    Focus on accurate, factual details only. If information is not found, use null.

    Provide a JSON response with this structure:
    {{
        "basic_information": {{
            "institute_name": "Full name of the institute",
            "location": "City, State, Country",
            "established_year": "Year or null",
            "contact_details": {{
                "email": "Email or null",
                "phone": ["List of phone numbers"],
                "website": "Website URL",
                "address": "Full address"
            }}
        }},
        "programs": {{
            "yoga_teacher_training": [
                {{
                    "name": "Course name",
                    "duration": "Duration in hours/days",
                    "style": "Yoga style",
                    "certification": "Certification type (e.g., RYT 200)",
                    "price": "Price in USD or INR"
                }}
            ],
            "other_courses": [
                {{
                    "name": "Course name",
                    "duration": "Duration",
                    "description": "Brief description"
                }}
            ]
        }},
        "facilities": ["List of available facilities"],
        "highlights": ["Key unique features or specialties"]
    }}

    Website Content:
    {context}

    Instructions:
    1. Extract only factual information present in the content
    2. Use null for missing information
    3. Ensure all prices are in either USD or INR (specify currency)
    4. Include complete contact details when available
    5. List all programs with accurate durations and certifications
    """
    return prompt

def extract_website_info(content: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Extract structured information from website content using OpenAI API
    
    Args:
        content: Raw website content
        api_key: OpenAI API key
    
    Returns:
        Dictionary containing structured information or None if extraction fails
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # Create extraction prompt
        extraction_prompt = create_extraction_prompt(content)
        token_count = count_tokens(extraction_prompt)
        
        if token_count > 128000:  # Safe limit for GPT-4-turbo
            print(f"Warning: Content too long ({token_count} tokens). Truncating...")
            content = content[:int(len(content) * (128000 / token_count))]
            extraction_prompt = create_extraction_prompt(content)
        
        # Generate response using OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4-turbo
            messages=[
                {"role": "system", "content": "You are a precise data extraction assistant. Extract only factual information and use null for missing data. Provide response in valid JSON format."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.1,  # Lower temperature for more consistent output
            response_format={"type": "json_object"}  # GPT-4-turbo supports this parameter
        )
        
        # Parse and validate JSON response
        try:
            extracted_info = json.loads(response.choices[0].message.content)
            return extracted_info
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    except Exception as e:
        print(f"Error in extraction: {str(e)}")
        return None

def process_website_data(input_data:Dict, output_file: str, api_key: str) -> Dict[str, Any]:
    """
    Process website content and extract structured information
    
    Args:
        input_data: Either path to input JSON file or dictionary containing website content
        output_file: Path to save extracted information
        api_key: OpenAI API key
    
    Returns:
        Dictionary containing processed results
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Handle input data
        if isinstance(input_data, str):
            with open(input_data, 'r', encoding='utf-8') as f:
                website_data = json.load(f)
        else:
            website_data = input_data
        
        print(f"Processing {len(website_data)} websites...")
        
        # Extract information for each website
        parsed_results = {}
        for url, content in website_data.items():
            print(f"\nProcessing: {url}")
            
            # Skip if content has error
            if isinstance(content, dict) and 'error' in content:
                print(f"Skipping due to previous error: {content['error']}")
                parsed_results[url] = {"error": content['error']}
                continue
            
            # Combine all text content for processing
            combined_content = ""
            if isinstance(content, dict):
                combined_content = f"Title: {content.get('title', '')}\n"
                combined_content += f"Description: {content.get('meta_description', '')}\n"
                combined_content += "Headers:\n" + "\n".join(content.get('h1_headers', []) + content.get('h2_headers', [])) + "\n"
                combined_content += "Content:\n" + "\n".join(content.get('paragraphs', []))
            
            # Extract structured information
            parsed_info = extract_website_info(combined_content, api_key)
            if parsed_info:
                parsed_results[url] = parsed_info
            else:
                parsed_results[url] = {"error": "Failed to extract information"}
        
        # Save results
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_results, f, indent=2, ensure_ascii=False)
        
        print(f"\nProcessing complete. Results saved to {output_file}")
        return parsed_results
    
    except Exception as e:
        print(f"Error processing website data: {str(e)}")
        return {}