import json
from typing import List, Dict
import os

def extract_emails_from_structured_data(input_data:Dict, output_dir: str) -> List[Dict[str, str]]:
    """
    Extract emails, phone numbers and related information from structured data and save to JSON
    
    Args:
        input_data: Either path to structured_data.json or dictionary containing structured data
        output_dir: Directory to save the extracted contact info
        
    Returns:
        List of dictionaries containing contact and institute info
    """
    contact_data = []
    
    try:
        # Handle input data
        if isinstance(input_data, str):
            with open(input_data, 'r', encoding='utf-8') as f:
                structured_data = json.load(f)
        else:
            structured_data = input_data
        
        print("\nProcessing Structured Data:")
        for url, data in structured_data.items():
            print(f"\nURL: {url}")
            try:
                if 'error' in data:
                    print(f"Error in data: {data['error']}")
                    continue
                
                basic_info = data.get('basic_information', {})
                contact_details = basic_info.get('contact_details', {})
                email = contact_details.get('email')
                phone_numbers = contact_details.get('phone', [])
                
                # Convert single phone number to list if needed
                if isinstance(phone_numbers, str):
                    phone_numbers = [phone_numbers]
                elif phone_numbers is None:
                    phone_numbers = []
                
                # Only add if either email or phone is available
                if (email and email != "null") or phone_numbers:
                    contact_info = {
                        'email': email if email and email != "null" else None,
                        'phone_numbers': phone_numbers,
                        'institute_name': basic_info.get('institute_name', 'Yoga Institute'),
                        'location': basic_info.get('location', 'your location'),
                        'website': url,
                        'contact_name': 'Sir/Madam',  # Default salutation
                        'address': contact_details.get('address')
                    }
                    contact_data.append(contact_info)
                    print(f"Institute: {contact_info['institute_name']}")
                    print(f"Email: {contact_info['email']}")
                    print(f"Phone: {', '.join(contact_info['phone_numbers']) if contact_info['phone_numbers'] else 'None'}")
            
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save contact info to JSON file
        output_file = os.path.join(output_dir, 'extracted_contacts.json')
        output_data = {
            'total_contacts': len(contact_data),
            'contacts': contact_data,
            'summary': {
                'with_email': len([c for c in contact_data if c['email']]),
                'with_phone': len([c for c in contact_data if c['phone_numbers']]),
                'with_both': len([c for c in contact_data if c['email'] and c['phone_numbers']])
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nContact Information Summary:")
        print(f"Total contacts found: {len(contact_data)}")
        print(f"Contacts with email: {len([c for c in contact_data if c['email']])}")
        print(f"Contacts with phone: {len([c for c in contact_data if c['phone_numbers']])}")
        print(f"Contacts with both: {len([c for c in contact_data if c['email'] and c['phone_numbers']])}")
        print(f"\nData saved to: {output_file}")
        
        return contact_data
    
    except Exception as e:
        print(f"Error reading structured data: {str(e)}")
        return []

def save_contacts(contacts):
    try:
        with open('lead-generation/data/processed/extracted_contacts.json', 'w') as f:
            json.dump(contacts, f, indent=4)
    except Exception as e:
        print(f"Error saving contacts: {e}")