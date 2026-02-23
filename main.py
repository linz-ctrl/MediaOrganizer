"""
Main Media Organizer - CLEAN OUTPUT VERSION
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.organizer import MediaOrganizer
from structures.photo_structure import PhotoStructure
from structures.video_structure import VideoStructure
from structures.audio_structure import AudioStructure
from config.settings import PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR

def print_banner():
    """Print application banner"""
    print("="*60)
    print("📁 MEDIA ORGANIZER")
    print("Organize photos, videos, and audio by date")
    print("Structure: YYYY/YYYY-MM-DD [description]/")
    print("="*60)

def show_menu():
    """Display interactive menu"""
    print("\n" + "="*60)
    print("📋 MAIN MENU")
    print("="*60)
    print("\nWhat would you like to do?")
    print()
    print("1. 🗂️  Setup folder structure")
    print("2. 🔍 Dry run (test without moving)")
    print("3. 🚀 Organize files from _RawData")
    print("4. 🔧 Fix existing files")
    print("5. ✅ Validate folder structure")
    print("6. 📊 Show statistics")
    print("7. ❌ Exit")
    print("\n" + "="*60)

def setup_folders():
    """Setup folder structure"""
    print("\n🗂️  Setting up folder structure...")
    try:
        organizer = MediaOrganizer()
        organizer.ensure_folder_structure()
        print("✅ Folder structure created!")
        print("\nFolders:")
        print("  _RawData/       (put your files here)")
        print("  Photos/         (organized photos)")
        print("  Videos/         (organized videos)")
        print("  Audio/          (organized audio)")
    except Exception as e:
        print(f"❌ Error: {e}")

def dry_run():
    """Run organizer in dry-run mode"""
    print("\n🔍 Running dry run (no files will be moved)...")
    print("-"*40)
    try:
        organizer = MediaOrganizer(dry_run=True)
        organizer.ensure_folder_structure()
        count = organizer.process_raw_data()
        print("\n" + "-"*40)
        if count > 0:
            print(f"✅ Would organize {count} files")
        else:
            print("⚠ No files to organize")
    except Exception as e:
        print(f"❌ Error: {e}")

def organize_files():
    """Organize files for real"""
    print("\n🚀 Organizing files from _RawData...")
    print("-"*40)
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("  Cancelled")
        return
    
    try:
        organizer = MediaOrganizer(dry_run=False)
        organizer.ensure_folder_structure()
        count = organizer.process_raw_data()
        organizer.print_stats()
    except Exception as e:
        print(f"❌ Error: {e}")

def fix_existing_files():
    """Fix existing files in organized folders"""
    print("\n🔧 FIXING EXISTING FILES")
    print("="*60)
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        print("  Cancelled")
        return
    
    print("\n" + "="*60)
    
    try:
        organizer = MediaOrganizer(dry_run=False)
        fixed_count = organizer.fix_existing_files()
        
        if fixed_count > 0:
            print(f"\n✅ Fixed {fixed_count} files")
        else:
            print("\n✅ No files needed fixing")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def validate_structure():
    """Validate folder structure"""
    print("\n✅ Validating folder structure...")
    
    issues = []
    
    # Check photos
    if PHOTOS_DIR.exists():
        photo_structure = PhotoStructure(PHOTOS_DIR)
        photo_issues = photo_structure.validate_structure()
        if photo_issues:
            issues.append("Photos:")
            issues.extend([f"  - {issue}" for issue in photo_issues])
    
    # Check videos
    if VIDEOS_DIR.exists():
        video_structure = VideoStructure(VIDEOS_DIR)
        video_issues = video_structure.validate_structure()
        if video_issues:
            issues.append("Videos:")
            issues.extend([f"  - {issue}" for issue in video_issues])
    
    # Check audio
    if AUDIO_DIR.exists():
        audio_structure = AudioStructure(AUDIO_DIR)
        audio_issues = audio_structure.validate_structure()
        if audio_issues:
            issues.append("Audio:")
            issues.extend([f"  - {issue}" for issue in audio_issues])
    
    if issues:
        print("\n⚠ Issues found:")
        for issue in issues:
            print(issue)
    else:
        print("\n✅ All folders are valid")

def show_statistics():
    """Show file statistics"""
    print("\n📊 Gathering statistics...")
    
    stats = {
        'Photos': 0,
        'Videos': 0,
        'Audio': 0
    }
    
    # Count photos
    if PHOTOS_DIR.exists():
        for file_path in PHOTOS_DIR.rglob("*"):
            if file_path.is_file():
                stats['Photos'] += 1
    
    # Count videos
    if VIDEOS_DIR.exists():
        for file_path in VIDEOS_DIR.rglob("*"):
            if file_path.is_file():
                stats['Videos'] += 1
    
    # Count audio
    if AUDIO_DIR.exists():
        for file_path in AUDIO_DIR.rglob("*"):
            if file_path.is_file():
                stats['Audio'] += 1
    
    # Print statistics
    total_files = 0
    
    print("\n📁 File counts:")
    for media_type, count in stats.items():
        total_files += count
        if count > 0:
            print(f"  {media_type}: {count:,} files")
    
    if total_files == 0:
        print("\n📭 No files found")
    else:
        print(f"\n📈 TOTAL: {total_files:,} files")

import argparse

def main():
    """Main interactive menu loop"""
    parser = argparse.ArgumentParser(description="Media Organizer")
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode instead of GUI')
    args, unknown = parser.parse_known_args()
    
    if args.cli:
        print_banner()
        
        # Check if _RawData exists
        from config.settings import RAW_DATA_DIR
        
        if not RAW_DATA_DIR.exists():
            print("\n⚠ _RawData folder not found")
            setup = input("  Setup folders? (Y/n): ").strip().lower()
            if setup in ['y', 'yes', '']:
                setup_folders()
        
        while True:
            try:
                show_menu()
                choice = input("\nEnter choice (1-7): ").strip()
                
                if choice == "1":
                    setup_folders()
                elif choice == "2":
                    dry_run()
                elif choice == "3":
                    organize_files()
                elif choice == "4":
                    fix_existing_files()
                elif choice == "5":
                    validate_structure()
                elif choice == "6":
                    show_statistics()
                elif choice == "7":
                    print("\n👋 Goodbye!")
                    print("="*60)
                    break
                else:
                    print("\n❌ Invalid choice")
                
                # Pause
                if choice != "7":
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("\nPress Enter to continue...")
    else:
        # Launch GUI
        from interfaces.gui import launch_gui
        launch_gui()

if __name__ == "__main__":
    main()