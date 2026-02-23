"""
Fixed Media Organizer - NO PATH DISPLAY ERRORS
"""
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from config.settings import RAW_DATA_DIR, PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR
from config.rules import clean_filename, generate_folder_name, extract_date_from_name
from core.file_utils import safe_move, get_file_info
from core.date_extractor import get_media_date
from detectors.media_detector import MediaDetector
from detectors.audio_categorizer import AudioCategorizer

class MediaOrganizer:
    """Fixed organizer with no path display errors"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.media_detector = MediaDetector()
        self.audio_categorizer = AudioCategorizer()
        self.stats = {
            'processed': 0,
            'moved': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def ensure_folder_structure(self):
        """Create necessary folder structure"""
        for folder in [RAW_DATA_DIR, PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Create audio subfolders
        audio_categories = ['Music', 'Recordings', 'Podcasts', 'Audiobooks']
        for category in audio_categories:
            (AUDIO_DIR / category).mkdir(exist_ok=True)
    
    def get_existing_folder_for_date(self, base_dir: Path, year: int, month: int, day: int) -> Optional[Path]:
        """
        Check if a folder already exists for this date (even with description)
        """
        if not base_dir.exists():
            return None
        
        year_dir = base_dir / str(year)
        if not year_dir.exists():
            return None
        
        # Look for folders starting with the date
        date_prefix = f"{year}-{month:02d}-{day:02d}"
        for folder in year_dir.iterdir():
            if folder.is_dir() and folder.name.startswith(date_prefix):
                return folder
        
        return None
    
    def get_destination_for_file(self, file_path: Path, year: int, month: int, day: int, media_type: str) -> Path:
        """
        Get destination path, using existing folder if available
        """
        if media_type == 'photo':
            base_dir = PHOTOS_DIR
        elif media_type == 'video':
            base_dir = VIDEOS_DIR
        else:  # audio
            base_dir = AUDIO_DIR
        
        # First, check for existing folder
        existing_folder = self.get_existing_folder_for_date(base_dir, year, month, day)
        if existing_folder:
            # Use existing folder (even if it has description)
            return existing_folder / file_path.name
        
        # No existing folder, create standard one
        date_folder = generate_folder_name(year, month, day)
        dest_dir = base_dir / str(year) / date_folder
        return dest_dir / file_path.name
    
    def organize_audio_file(self, file_path: Path, year: int, month: int, day: int) -> Optional[Path]:
        """
        Organize audio file with categorization
        """
        category, subpath = self.audio_categorizer.categorize(file_path)
        
        if category == "Recordings":
            # Check for existing recordings folder
            existing = self.get_existing_folder_for_date(AUDIO_DIR / "Recordings", year, month, day)
            if existing:
                return existing / file_path.name
            
            # Create new folder
            dest_dir = AUDIO_DIR / "Recordings" / str(year) / generate_folder_name(year, month, day)
        
        elif category == "Podcasts":
            show = clean_filename(subpath) if subpath else "Unknown Show"
            
            # Check for existing podcast folder
            podcast_base = AUDIO_DIR / "Podcasts" / show / str(year)
            existing = None
            if podcast_base.exists():
                date_prefix = f"{year}-{month:02d}-{day:02d}"
                for folder in podcast_base.iterdir():
                    if folder.is_dir() and folder.name.startswith(date_prefix):
                        existing = folder
                        break
            
            if existing:
                return existing / file_path.name
            
            # Create new folder
            dest_dir = podcast_base / generate_folder_name(year, month, day)
        
        elif category in ["Music", "Audiobooks"]:
            # Structured folders
            dest_dir = AUDIO_DIR / category / clean_filename(subpath)
        else:
            # Fallback to Recordings
            existing = self.get_existing_folder_for_date(AUDIO_DIR / "Recordings", year, month, day)
            if existing:
                return existing / file_path.name
            
            dest_dir = AUDIO_DIR / "Recordings" / str(year) / generate_folder_name(year, month, day)
        
        dest_path = dest_dir / file_path.name
        return dest_path
    
    def get_simple_display_path(self, dest_path: Path) -> str:
        """
        Get simple display path without complex relative calculations
        """
        try:
            # Show the last 3 parts of the path (e.g., 2023/2023-03-17/filename.mp4)
            parts = dest_path.parts
            if len(parts) >= 3:
                return f"{parts[-3]}/{parts[-2]}/{parts[-1]}"
            elif len(parts) == 2:
                return f"{parts[-2]}/{parts[-1]}"
            else:
                return dest_path.name
        except:
            return dest_path.name
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single file - SIMPLE DISPLAY, NO PATH ERRORS
        """
        try:
            self.stats['processed'] += 1
            
            # Detect media type
            media_type = self.media_detector.detect(file_path)
            
            if media_type == 'unknown':
                print(f"⚠ Skipping unknown file type: {file_path.name}")
                self.stats['skipped'] += 1
                return False
            
            # Get date
            year, month, day, source = get_media_date(file_path)
            
            # Get destination path
            if media_type == 'audio':
                dest_path = self.organize_audio_file(file_path, year, month, day)
            else:
                dest_path = self.get_destination_for_file(file_path, year, month, day, media_type)
            
            # Ensure directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file is already in correct location
            if file_path.resolve() == dest_path.resolve():
                return False
            
            # Move file
            success, message = safe_move(file_path, dest_path)
            
            if success:
                self.stats['moved'] += 1
                icon = self._get_icon(media_type)
                display_path = self.get_simple_display_path(dest_path)
                
                # Show if using existing folder with description
                folder_name = dest_path.parent.name
                if ' ' in folder_name and folder_name.count('-') >= 2:
                    print(f"{icon} {media_type.capitalize()}: {file_path.name}")
                    print(f"  Date: {year}-{month:02d}-{day:02d}")
                    print(f"  → {display_path}")
                else:
                    print(f"{icon} {media_type.capitalize()}: {file_path.name}")
                    print(f"  Date: {year}-{month:02d}-{day:02d}")
                    print(f"  → {display_path}")
                
                return True
            else:
                print(f"✗ Error: {file_path.name}")
                self.stats['errors'] += 1
                return False
                
        except Exception as e:
            print(f"✗ Error: {file_path.name}")
            self.stats['errors'] += 1
            return False
    
    def process_raw_data(self) -> int:
        """
        Process all files in _RawData directory - SIMPLIFIED OUTPUT
        """
        if not RAW_DATA_DIR.exists():
            print(f"✗ _RawData folder not found")
            return 0
        
        files = list(RAW_DATA_DIR.rglob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith('.')]
        
        if not files:
            print("✓ No files found in _RawData")
            return 0
        
        print(f"📦 Found {len(files)} files in _RawData to organize")
        print("🔍 Reading dates from metadata...")
        
        batch_size = 50
        for i, file_path in enumerate(files):
            self.process_file(file_path)
            
            # Show progress every batch_size files
            if (i + 1) % batch_size == 0:
                print(f"  Progress: {i + 1}/{len(files)} files processed")
        
        # Clean empty folders
        self._clean_empty_folders(RAW_DATA_DIR)
        
        return self.stats['moved']
    
    def fix_existing_files(self):
        """
        Fix files already in organized folders but in wrong locations
        """
        print("\n🔄 FIXING EXISTING FILES")
        print("="*60)
        
        total_fixed = 0
        
        # Fix Photos
        print("\n📸 Checking Photos...")
        total_fixed += self._fix_folder(PHOTOS_DIR, "photo")
        
        # Fix Videos
        print("\n🎥 Checking Videos...")
        total_fixed += self._fix_folder(VIDEOS_DIR, "video")
        
        # Fix Audio Recordings
        recordings_dir = AUDIO_DIR / "Recordings"
        if recordings_dir.exists():
            print("\n🎙️ Checking Audio Recordings...")
            total_fixed += self._fix_folder(recordings_dir, "audio")
        
        print(f"\n✅ Fixed {total_fixed} existing files")
        return total_fixed
    
    def _fix_folder(self, folder: Path, media_type: str) -> int:
        """
        Fix files in a specific folder
        """
        if not folder.exists():
            return 0
        
        # Get all files
        all_files = list(folder.rglob("*"))
        all_files = [f for f in all_files if f.is_file()]
        
        if not all_files:
            return 0
        
        print(f"  Found {len(all_files)} files to check")
        
        fixed_count = 0
        
        for file_path in all_files:
            try:
                # Get actual date from file
                year, month, day, source = get_media_date(file_path)
                
                # Get where file should go
                if media_type == 'audio' and "Recordings" in str(file_path):
                    # Audio recordings
                    dest_path = self.organize_audio_file(file_path, year, month, day)
                else:
                    # Photos or videos
                    dest_path = self.get_destination_for_file(file_path, year, month, day, media_type)
                
                # Check if already in correct location
                if file_path.resolve() == dest_path.resolve():
                    continue
                
                # Move file
                success, message = safe_move(file_path, dest_path)
                if success:
                    fixed_count += 1
                    print(f"    🔧 Fixed: {file_path.name}")
                    
            except Exception as e:
                print(f"    ❌ Error fixing {file_path.name}")
        
        return fixed_count
    
    def _get_icon(self, media_type: str) -> str:
        """Get icon for media type"""
        icons = {
            'photo': '📸',
            'video': '🎥',
            'audio': '🎵',
            'music': '🎵',
            'recording': '🎙️',
            'podcast': '🎧',
            'audiobook': '📚'
        }
        return icons.get(media_type, '📄')
    
    def _clean_empty_folders(self, start_path: Path):
        """Remove empty folders"""
        for folder in sorted(start_path.rglob("*"), reverse=True):
            if folder.is_dir() and not any(folder.iterdir()):
                try:
                    folder.rmdir()
                except:
                    pass
    
    def print_stats(self):
        """Print statistics"""
        print(f"\n📊 Statistics:")
        print(f"  Total files: {self.stats['processed']}")
        print(f"  Organized: {self.stats['moved']}")
        print(f"  Errors: {self.stats['errors']}")
        print(f"  Skipped: {self.stats['skipped']}")