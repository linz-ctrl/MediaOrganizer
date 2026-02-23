"""
Audio file categorization
"""
import re
from pathlib import Path
from typing import Tuple, Optional, Dict
from config.rules import clean_filename

try:
    import mutagen
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False

class AudioCategorizer:
    """Categorize audio files into Music, Recordings, Podcasts, or Audiobooks"""
    
    def __init__(self):
        self.patterns = {
            'podcast': [
                r'episode[_\s\-]*\d+',
                r'ep[_\s\-]*\d+',
                r'#\d+',
                r's\d+e\d+',
                r'podcast',
                r'show[_\s\-]*\d+'
            ],
            'audiobook': [
                r'chapter[_\s\-]*\d+',
                r'ch[_\s\-]*\d+',
                r'part[_\s\-]*\d+',
                r'book[_\s\-]*\d+',
                r'audiobook'
            ],
            'recording': [
                'recording', 'voice memo', 'memo', 'voice note',
                'meeting', 'interview', 'lecture', 'class',
                'note', 'dictation', 'audio note'
            ],
            'music': [
                'song', 'track', 'music', 'single', 'album'
            ]
        }
    
    def get_metadata(self, file_path: Path) -> Dict:
        """Extract audio metadata"""
        if not HAS_MUTAGEN:
            return {}
        
        try:
            audio = mutagen.File(file_path)
            if not audio:
                return {}
            
            metadata = {}
            tag_mappings = {
                'artist': ['artist', 'performer', 'albumartist'],
                'album': ['album'],
                'title': ['title'],
                'track': ['tracknumber', 'track'],
                'date': ['date', 'year', 'originaldate'],
                'genre': ['genre'],
                'show': ['show', 'podcast', 'series']
            }
            
            for key, tag_list in tag_mappings.items():
                for tag in tag_list:
                    if tag in audio:
                        value = audio[tag]
                        if isinstance(value, list):
                            metadata[key] = str(value[0])
                        else:
                            metadata[key] = str(value)
                        break
            
            return metadata
        except:
            return {}
    
    def categorize_by_metadata(self, metadata: Dict) -> Optional[Tuple[str, str]]:
        """Categorize based on metadata"""
        # Check for podcast indicators
        podcast_keywords = ['podcast', 'show', 'series', 'episode']
        for keyword in podcast_keywords:
            for tag, value in metadata.items():
                if keyword in str(value).lower():
                    show = metadata.get('show') or metadata.get('album') or 'Unknown Show'
                    return "Podcasts", show
        
        # Check for audiobook indicators
        audiobook_keywords = ['audiobook', 'chapter', 'book', 'narrated']
        for keyword in audiobook_keywords:
            for tag, value in metadata.items():
                if keyword in str(value).lower():
                    author = metadata.get('artist', 'Unknown Author')
                    book = metadata.get('album', 'Unknown Book')
                    return "Audiobooks", f"{author}/{book}"
        
        # Check for music
        if metadata.get('artist') and metadata.get('album'):
            return "Music", f"{metadata['artist']}/{metadata['album']}"
        
        return None
    
    def categorize_by_filename(self, filename: str) -> Tuple[str, str]:
        """Categorize based on filename patterns"""
        filename_lower = filename.lower()
        
        # Check patterns
        for pattern in self.patterns['podcast']:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                show = self._extract_show_name(filename)
                return "Podcasts", show
        
        for pattern in self.patterns['audiobook']:
            if re.search(pattern, filename_lower, re.IGNORECASE):
                book = self._extract_book_name(filename)
                return "Audiobooks", book
        
        for keyword in self.patterns['recording']:
            if keyword in filename_lower:
                return "Recordings", ""
        
        for keyword in self.patterns['music']:
            if keyword in filename_lower:
                return "Music", "Unknown Artist/Unknown Album"
        
        # Default to Recordings
        return "Recordings", ""
    
    def _extract_show_name(self, filename: str) -> str:
        """Extract show name from filename"""
        patterns_to_remove = [
            r'episode[_\s\-]*\d+',
            r'ep[_\s\-]*\d+',
            r'#\d+',
            r's\d+e\d+',
            r'\d+',
            r'podcast',
            r'show[_\s\-]*\d+',
            r'\.mp3$', r'\.m4a$', r'\.flac$', r'\.wav$'
        ]
        
        show_name = filename.lower()
        for pattern in patterns_to_remove:
            show_name = re.sub(pattern, '', show_name, flags=re.IGNORECASE)
        
        show_name = re.sub(r'[_\-\.,]+', ' ', show_name).strip()
        
        if show_name:
            show_name = ' '.join(word.capitalize() for word in show_name.split())
        
        return show_name if show_name else "Unknown Show"
    
    def _extract_book_name(self, filename: str) -> str:
        """Extract book name from filename"""
        patterns_to_remove = [
            r'chapter[_\s\-]*\d+',
            r'ch[_\s\-]*\d+',
            r'part[_\s\-]*\d+',
            r'\d+',
            r'audiobook',
            r'\.mp3$', r'\.m4a$', r'\.m4b$'
        ]
        
        book_name = filename.lower()
        for pattern in patterns_to_remove:
            book_name = re.sub(pattern, '', book_name, flags=re.IGNORECASE)
        
        book_name = re.sub(r'[_\-\.,]+', ' ', book_name).strip()
        
        if book_name:
            book_name = ' '.join(word.capitalize() for word in book_name.split())
        
        return book_name if book_name else "Unknown Book"
    
    def categorize(self, file_path: Path) -> Tuple[str, str]:
        """
        Categorize audio file
        Returns: (category, subpath)
        """
        # Try metadata first
        metadata = self.get_metadata(file_path)
        if metadata:
            result = self.categorize_by_metadata(metadata)
            if result:
                return result
        
        # Fallback to filename analysis
        filename = file_path.stem
        return self.categorize_by_filename(filename)