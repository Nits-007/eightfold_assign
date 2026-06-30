import re
from datetime import datetime
from typing import Optional

def normalize_phone(raw_phone: str) -> Optional[str]:
    
    #Strips non-digits and formats to E.164.
    #If no country code is present, defaults to US (+1) for this assignment scope.

    if not raw_phone:
        return None
        
    digits = re.sub(r'\D', '', str(raw_phone))
    if not digits:
        return None
        
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) > 10:
        return f"+{digits}"
        
    return None

def normalize_date(raw_date: str) -> Optional[str]:

    #Attempts to parse various date strings into YYYY-MM format.
    
    if not raw_date:
        return None
        
    clean_date = str(raw_date).strip()
    
    if re.match(r'^\d{4}-\d{2}$', clean_date) or re.match(r'^\d{4}$', clean_date):
        return clean_date

    formats_to_try = ['%b %Y', '%B %Y', '%m/%Y', '%m/%y']
    
    for fmt in formats_to_try:
        try:
            parsed_date = datetime.strptime(clean_date, fmt)
            return parsed_date.strftime('%Y-%m')
        except ValueError:
            continue
            
    return None

def normalize_skill(raw_skill: str) -> str:

    #Lowercases and trims whitespace to ensure ' Python ' matches 'python'.
    
    if not raw_skill:
        return ""
    return str(raw_skill).strip().lower()

def normalize_dob(raw_dob: str) -> Optional[str]:
   
    #Parses date of birth into YYYY-MM-DD.
    
    if not raw_dob:
        return None
    
    clean_dob = str(raw_dob).strip()

    if re.match(r'^\d{4}-\d{2}-\d{2}$', clean_dob):
        return clean_dob

    formats_to_try = ['%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%B %d, %Y', '%b %d, %Y', '%d %b %Y']
    for fmt in formats_to_try:
        try:
            parsed_date = datetime.strptime(clean_dob, fmt)
            return parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    return None

def normalize_location(raw_location) -> Optional[dict]:

    #Normalizes a location and maps the country name to ISO-3166 alpha-2.
    
    if not raw_location:
        return None
        
    result = {}
    country_str = ""

    if isinstance(raw_location, dict):
        result["city"] = raw_location.get("city")
        result["region"] = raw_location.get("region")
        country_str = str(raw_location.get("country", "")).strip().upper()
    else:
        country_str = str(raw_location).strip().upper()

    mapping = {
        "UNITED STATES": "US",
        "USA": "US",
        "INDIA": "IN",
        "UNITED KINGDOM": "UK",
        "UK": "UK",
    }
    if country_str:
        result["country"] = mapping.get(country_str, country_str)
        
    return result if result else None