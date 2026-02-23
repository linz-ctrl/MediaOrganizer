"""
Folder structure rules and validation - ALLOWS DESCRIPTIONS FOR ALL MEDIA TYPES
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional

def validate_year_folder(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate year folder name (YYYY format)
    """
    if not name.isdigit():
        return False, "Year folder must be numeric"
    
    if len(name) != 4:
        return False, "Year folder must be 4 digits"
    
    year = int(name)
    current_year = datetime.now().year
    
    if year < 1990 or year > current_year + 1:
        return False, f"Suspicious year: {year}"
    
    return True, None

def validate_date_folder(year: int, name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date folder name - ALLOWS TEXT AFTER YYYY-MM-DD
    """
    # Check if starts with YYYY-MM-DD pattern
    date_pattern = r'^(\d{4}-\d{2}-\d{2})'
    match = re.match(date_pattern, name)
    
    if not match:
        return False, f"Folder must start with YYYY-MM-DD: {name}"
    
    date_part = match.group(1)
    
    try:
        folder_year = int(date_part[:4])
        
        # Check year consistency
        if folder_year != year:
            return False, f"Year mismatch: folder {folder_year} vs parent {year}"
        
        return True, None
        
    except ValueError as e:
        return False, f"Invalid date in folder name: {date_part} ({str(e)})"

def extract_date_from_name(name: str) -> Tuple[Optional[int], Optional[int], Optional[int], str]:
    """
    Extract date from folder or filename that may have description
    Returns: (year, month, day, description)
    """
    pattern = r'^(\d{4})[-_]?(\d{2})[-_]?(\d{2})(?:[ _\-]+(.*))?$'
    match = re.match(pattern, name)
    
    if not match:
        return None, None, None, ""
    
    try:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        description = match.group(4) or ""
        
        # Validate date
        datetime(year, month, day)
        return year, month, day, description.strip()
    except (ValueError, TypeError):
        return None, None, None, ""

def clean_filename(name: str) -> str:
    """
    Clean filename for safe filesystem use
    """
    # Remove invalid characters
    illegal_chars = r'[<>:"/\\|?*\x00-\x1f]'
    name = re.sub(illegal_chars, '', name)
    name = name.strip()
    
    # Limit length
    if len(name) > 200:
        name = name[:195] + '...' + name[-5:]
    
    return name

def generate_folder_name(year: int, month: int, day: int, description: str = "") -> str:
    """
    Generate folder name in YYYY-MM-DD format with optional description
    """
    base_name = f"{year}-{month:02d}-{day:02d}"
    if description and description.strip():
        clean_desc = description.strip()[:50]  # Limit description length
        return f"{base_name} {clean_desc}"
    return base_name