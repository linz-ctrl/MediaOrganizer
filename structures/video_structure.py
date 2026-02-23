"""
Video folder structure: Videos/YYYY/YYYY-MM-DD [description]/
"""
from pathlib import Path
from config.rules import validate_year_folder, validate_date_folder, extract_date_from_name

class VideoStructure:
    """Manage video folder structure"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def get_path_for_date(self, year: int, month: int, day: int, description: str = "") -> Path:
        """Get folder path for specific date"""
        from config.rules import generate_folder_name
        date_folder = generate_folder_name(year, month, day, description)
        return self.base_dir / str(year) / date_folder
    
    def ensure_structure(self, year: int, month: int, day: int, description: str = "") -> Path:
        """Ensure folder structure exists for date"""
        target_dir = self.get_path_for_date(year, month, day, description)
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir
    
    def find_existing_folder(self, year: int, month: int, day: int) -> Optional[Path]:
        """
        Find existing folder for a date, even if it has description
        """
        if not self.base_dir.exists():
            return None
        
        year_dir = self.base_dir / str(year)
        if not year_dir.exists():
            return None
        
        # Look for folders that start with the date
        date_prefix = f"{year}-{month:02d}-{day:02d}"
        for folder in year_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(date_prefix):
                return folder
        
        return None
    
    def validate_structure(self) -> list:
        """Validate video folder structure"""
        issues = []
        
        if not self.base_dir.exists():
            return issues
        
        for year_dir in self.base_dir.iterdir():
            if not year_dir.is_dir():
                continue
            
            valid, error = validate_year_folder(year_dir.name)
            if not valid:
                # Check if it's a date folder in root
                year, month, day, desc = extract_date_from_name(year_dir.name)
                if year is not None:
                    print(f"  ⚠ Date folder in Videos root: {year_dir.name}")
                    print(f"    (Will be moved to {year}/ folder during organization)")
                continue
            
            year = int(year_dir.name)
            
            for date_dir in year_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                valid, error = validate_date_folder(year, date_dir.name)
                if not valid:
                    issues.append(f"Date folder '{date_dir.name}': {error}")
        
        return issues