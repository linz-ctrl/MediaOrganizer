"""
Command-line interface
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

from core.organizer import MediaOrganizer
from structures.photo_structure import PhotoStructure
from structures.video_structure import VideoStructure
from structures.audio_structure import AudioStructure
from config.settings import PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR

class CLI:
    """Command-line interface handler"""
    
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            description='Media Organizer - Organize photos, videos, and audio by date\nStructure: YYYY/YYYY-MM-DD/'
        )
        
        parser.add_argument(
            '--sort',
            action='store_true',
            help='Sort all files from _RawData'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simulate without moving files'
        )
        
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate folder structure'
        )
        
        parser.add_argument(
            '--setup',
            action='store_true',
            help='Create folder structure'
        )
        
        parser.add_argument(
            '--path',
            type=str,
            help='Custom path to organize (instead of current directory)'
        )
        
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show statistics'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None):
        """Run CLI with arguments"""
        if args is None:
            args = sys.argv[1:]
        
        parsed_args = self.parser.parse_args(args)
        
        # Set working directory - REMOVE BANNER FROM HERE
        if parsed_args.path:
            try:
                target_path = Path(parsed_args.path).resolve()
                print(f"📁 Working directory: {target_path}")
            except Exception as e:
                print(f"✗ Error setting path: {e}")
                return
    

        
        # Setup
        if parsed_args.setup:
            self._setup_folders()
            return
        
        # Validate
        if parsed_args.validate:
            self._validate_structure()
            return
        
        # Sort
        if parsed_args.sort:
            organizer = MediaOrganizer(dry_run=parsed_args.dry_run)
            organizer.ensure_folder_structure()
            count = organizer.process_raw_data()
            organizer.print_stats()
            return
        
        # Stats
        if parsed_args.stats:
            self._show_statistics()
            return
        
        # No arguments - show help
        self.parser.print_help()
    
    def _setup_folders(self):
        """Create folder structure"""
        print("🗂️  Setting up folder structure...")
        
        organizer = MediaOrganizer()
        organizer.ensure_folder_structure()
        
        print("✅ Folder structure created:")
        print(f"   - {PHOTOS_DIR}")
        print(f"   - {VIDEOS_DIR}")
        print(f"   - {AUDIO_DIR}")
        print("   - Music/, Recordings/, Podcasts/, Audiobooks/")
        print(f"\n📁 Put your files in: {Path('_RawData')}")
    
    def _validate_structure(self):
        """Validate folder structure"""
        print("🔍 Validating folder structure...")
        
        issues = []
        
        # Check photos
        photo_structure = PhotoStructure(PHOTOS_DIR)
        photo_issues = photo_structure.validate_structure()
        if photo_issues:
            issues.append("Photos:")
            issues.extend([f"  - {issue}" for issue in photo_issues])
        
        # Check videos
        video_structure = VideoStructure(VIDEOS_DIR)
        video_issues = video_structure.validate_structure()
        if video_issues:
            issues.append("Videos:")
            issues.extend([f"  - {issue}" for issue in video_issues])
        
        # Check audio
        audio_structure = AudioStructure(AUDIO_DIR)
        audio_issues = audio_structure.validate_structure()
        if audio_issues:
            issues.append("Audio:")
            issues.extend([f"  - {issue}" for issue in audio_issues])
        
        if issues:
            print("⚠ Found issues:")
            for issue in issues:
                print(issue)
        else:
            print("✅ All folder structures are valid!")
    
    def _show_statistics(self):
        """Show file statistics"""
        print("📊 Gathering statistics...")
        
        stats = {
            'Photos': {'count': 0, 'size': 0},
            'Videos': {'count': 0, 'size': 0},
            'Audio': {'count': 0, 'size': 0}
        }
        
        # Count photos
        if PHOTOS_DIR.exists():
            for file_path in PHOTOS_DIR.rglob("*"):
                if file_path.is_file():
                    stats['Photos']['count'] += 1
                    stats['Photos']['size'] += file_path.stat().st_size
        
        # Count videos
        if VIDEOS_DIR.exists():
            for file_path in VIDEOS_DIR.rglob("*"):
                if file_path.is_file():
                    stats['Videos']['count'] += 1
                    stats['Videos']['size'] += file_path.stat().st_size
        
        # Count audio
        if AUDIO_DIR.exists():
            for file_path in AUDIO_DIR.rglob("*"):
                if file_path.is_file():
                    stats['Audio']['count'] += 1
                    stats['Audio']['size'] += file_path.stat().st_size
        
        # Print statistics
        total_files = 0
        total_size = 0
        
        for media_type, data in stats.items():
            count = data['count']
            size_mb = data['size'] / (1024 * 1024)
            total_files += count
            total_size += data['size']
            
            if count > 0:
                print(f"{media_type}: {count:,} files ({size_mb:,.1f} MB)")
        
        if total_files == 0:
            print("No files found in organized folders")
        else:
            total_size_gb = total_size / (1024 * 1024 * 1024)
            print(f"\nTotal: {total_files:,} files ({total_size_gb:.2f} GB)")