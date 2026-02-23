"""
Audio folder structures with descriptions support
"""
from pathlib import Path
from config.rules import clean_filename, generate_folder_name, validate_year_folder, validate_date_folder, extract_date_from_name

class AudioStructure:
    """Manage audio folder structures"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def get_recording_path(self, year: int, month: int, day: int, description: str = "") -> Path:
        """Get path for recordings: Recordings/YYYY/YYYY-MM-DD [description]/"""
        date_folder = generate_folder_name(year, month, day, description)
        recordings_dir = self.base_dir / "Recordings"
        return recordings_dir / str(year) / date_folder
    
    def get_podcast_path(self, show: str, year: int, month: int, day: int, description: str = "") -> Path:
        """Get path for podcasts: Podcasts/Show/YYYY/YYYY-MM-DD [description]/"""
        date_folder = generate_folder_name(year, month, day, description)
        podcasts_dir = self.base_dir / "Podcasts"
        return podcasts_dir / clean_filename(show) / str(year) / date_folder
    
    def get_music_path(self, artist: str, album: str) -> Path:
        """Get path for music: Music/Artist/Album/"""
        music_dir = self.base_dir / "Music"
        return music_dir / clean_filename(artist) / clean_filename(album)
    
    def get_audiobook_path(self, author: str, book: str) -> Path:
        """Get path for audiobooks: Audiobooks/Author/Book/"""
        audiobooks_dir = self.base_dir / "Audiobooks"
        return audiobooks_dir / clean_filename(author) / clean_filename(book)
    
    def ensure_category_dirs(self):
        """Ensure all audio category directories exist"""
        categories = ['Music', 'Recordings', 'Podcasts', 'Audiobooks']
        for category in categories:
            (self.base_dir / category).mkdir(parents=True, exist_ok=True)
    
    def find_existing_folder(self, category: str, year: int, month: int, day: int, show: str = None) -> Optional[Path]:
        """
        Find existing folder for a date in audio categories
        """
        if category == "Recordings":
            base_dir = self.base_dir / "Recordings" / str(year)
        elif category == "Podcasts" and show:
            base_dir = self.base_dir / "Podcasts" / clean_filename(show) / str(year)
        else:
            return None
        
        if not base_dir.exists():
            return None
        
        # Look for folders that start with the date
        date_prefix = f"{year}-{month:02d}-{day:02d}"
        for folder in base_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(date_prefix):
                return folder
        
        return None
    
    def validate_structure(self) -> list:
        """Validate audio folder structure"""
        issues = []
        
        if not self.base_dir.exists():
            return issues
        
        # Check each category
        categories = ['Music', 'Recordings', 'Podcasts', 'Audiobooks']
        for category in categories:
            cat_dir = self.base_dir / category
            if not cat_dir.exists():
                continue
            
            if category == "Recordings":
                issues.extend(self._validate_recordings(cat_dir))
            elif category == "Podcasts":
                issues.extend(self._validate_podcasts(cat_dir))
        
        return issues
    
    def _validate_recordings(self, recordings_dir: Path) -> list:
        """Validate recordings structure"""
        issues = []
        
        for year_dir in recordings_dir.iterdir():
            if not year_dir.is_dir():
                continue
            
            valid, error = validate_year_folder(year_dir.name)
            if not valid:
                # Check if it's a date folder in root
                year, month, day, desc = extract_date_from_name(year_dir.name)
                if year is not None:
                    print(f"  ⚠ Date folder in Recordings root: {year_dir.name}")
                    print(f"    (Will be moved to {year}/ folder during organization)")
                continue
            
            year = int(year_dir.name)
            
            for date_dir in year_dir.iterdir():
                if not date_dir.is_dir():
                    continue
                
                valid, error = validate_date_folder(year, date_dir.name)
                if not valid:
                    issues.append(f"Recordings date folder '{date_dir.name}': {error}")
        
        return issues
    
    def _validate_podcasts(self, podcasts_dir: Path) -> list:
        """Validate podcasts structure"""
        issues = []
        
        for show_dir in podcasts_dir.iterdir():
            if not show_dir.is_dir():
                continue
            
            for year_dir in show_dir.iterdir():
                if not year_dir.is_dir():
                    continue
                
                valid, error = validate_year_folder(year_dir.name)
                if not valid:
                    issues.append(f"Podcasts year folder '{year_dir.name}': {error}")
                    continue
                
                year = int(year_dir.name)
                
                for date_dir in year_dir.iterdir():
                    if not date_dir.is_dir():
                        continue
                    
                    valid, error = validate_date_folder(year, date_dir.name)
                    if not valid:
                        issues.append(f"Podcasts date folder '{date_dir.name}': {error}")
        
        return issues