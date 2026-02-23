import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import sys
import threading
from pathlib import Path

# Add project root to python path is handled in main.py, but we'll import here
from config.settings import load_config, save_config, update_paths
from config.settings import ROOT_DIR, RAW_DATA_DIR, PHOTOS_DIR, VIDEOS_DIR, AUDIO_DIR
from structures.photo_structure import PhotoStructure
from structures.video_structure import VideoStructure
from structures.audio_structure import AudioStructure
from core.organizer import MediaOrganizer


class RedirectStdout:
    """Redirects stdout to a tkinter text widget"""
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.original_stdout = sys.stdout

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()
        
    def flush(self):
        pass

    def restore(self):
        sys.stdout = self.original_stdout


class MediaOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Organizer")
        self.root.geometry("800x600")
        
        # Load current config
        self.config = load_config()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.welcome_tab = ttk.Frame(self.notebook)
        self.settings_tab = ttk.Frame(self.notebook)
        self.actions_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.welcome_tab, text="Welcome")
        self.notebook.add(self.settings_tab, text="Configuration")
        self.notebook.add(self.actions_tab, text="Actions & Output")
        
        self.setup_welcome_tab()
        self.setup_settings_tab()
        self.setup_actions_tab()
        
    def setup_welcome_tab(self):
        title_font = ("Helvetica", 16, "bold")
        heading_font = ("Helvetica", 12, "bold")
        
        tk.Label(self.welcome_tab, text="Welcome to Media Organizer", font=title_font).pack(pady=20)
        
        info_text = (
            "This application organizes your media files automatically into a clean,\n"
            "date-based structure (YYYY/MM/DD) by reading embedded metadata.\n\n"
        )
        tk.Label(self.welcome_tab, text=info_text, justify=tk.LEFT).pack(padx=20, anchor="w")
        
        tk.Label(self.welcome_tab, text="Why this system?", font=heading_font).pack(padx=20, anchor="w", pady=(10, 5))
        
        why_text = (
            "1. Metadata over Creation Date:\n"
            "   File 'creation dates' on your operating system change when you copy or move files.\n"
            "   This system cracks open the file and reads the real creation date from the EXIF data \n"
            "   (for photos) or multimedia tags (for videos/audio). This ensures files stay organized\n"
            "   by when they were actually shot, not when you copied them to a new hard drive.\n\n"
            "2. YYYY/MM/DD Structure:\n"
            "   Organizing directly into year, month, and day folders prevents any single folder \n"
            "   from becoming too large to open quickly. It provides a naturally chronological \n"
            "   browsing experience that is compatible with all devices without needing special software."
        )
        tk.Label(self.welcome_tab, text=why_text, justify=tk.LEFT).pack(padx=30, anchor="w")

    def setup_settings_tab(self):
        # We need vars to track paths
        self.path_vars = {
            'raw_data': tk.StringVar(value=str(RAW_DATA_DIR)),
            'photos': tk.StringVar(value=str(PHOTOS_DIR)),
            'videos': tk.StringVar(value=str(VIDEOS_DIR)),
            'audio': tk.StringVar(value=str(AUDIO_DIR))
        }
        
        settings_frame = ttk.LabelFrame(self.settings_tab, text="Folder Locations")
        settings_frame.pack(fill=tk.X, padx=20, pady=20)
        
        row = 0
        for key, var in self.path_vars.items():
            label_text = key.replace('_', ' ').title() + ":"
            ttk.Label(settings_frame, text=label_text).grid(row=row, column=0, padx=5, pady=10, sticky="e")
            entry = ttk.Entry(settings_frame, textvariable=var, width=50)
            entry.grid(row=row, column=1, padx=5, pady=10, sticky="we")
            
            browse_btn = ttk.Button(
                settings_frame, 
                text="Browse", 
                command=lambda k=key, v=var: self.browse_folder(k, v)
            )
            browse_btn.grid(row=row, column=2, padx=5, pady=10)
            row += 1
            
        settings_frame.columnconfigure(1, weight=1)
        
        save_btn = ttk.Button(self.settings_tab, text="Save Configuration", command=self.save_settings)
        save_btn.pack(pady=20)
        
        self.status_label = ttk.Label(self.settings_tab, text="")
        self.status_label.pack()

    def browse_folder(self, key, var):
        directory = filedialog.askdirectory(initialdir=var.get(), title=f"Select {key.title()} Folder")
        if directory:
            var.set(directory)

    def save_settings(self):
        if 'paths' not in self.config:
            self.config['paths'] = {}
            
        for key, var in self.path_vars.items():
            self.config['paths'][key] = var.get()
            
        try:
            save_config(self.config)
            update_paths(self.config)
            self.status_label.config(text="Configuration saved successfully!", foreground="green")
        except Exception as e:
            self.status_label.config(text=f"Error saving: {e}", foreground="red")

    def setup_actions_tab(self):
        # Buttons frame
        btn_frame = ttk.Frame(self.actions_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Setup Folders", command=self.run_setup).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Dry Run", command=self.run_dry_run).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Organize Files", command=self.run_organize).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Fix Existing", command=self.run_fix).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Validate", command=self.run_validate).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Statistics", command=self.run_stats).pack(side=tk.LEFT, padx=5)
        
        # Console output
        ttk.Label(self.actions_tab, text="Console Output:").pack(anchor="w", padx=10)
        
        self.console = scrolledtext.ScrolledText(self.actions_tab, wrap=tk.WORD, height=20, bg="black", fg="white")
        self.console.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.stdout_redirect = RedirectStdout(self.console)
        
    def _run_in_thread(self, func):
        """Run a function in a separate thread so GUI doesn't freeze"""
        def wrapper():
            sys.stdout = self.stdout_redirect
            self.console.insert(tk.END, "-"*60 + "\n")
            try:
                func()
            except Exception as e:
                print(f"Error: {e}")
            sys.stdout = self.stdout_redirect.original_stdout
            
        thread = threading.Thread(target=wrapper)
        thread.start()

    def run_setup(self):
        def task():
            print("\n🗂️ Setting up folder structure...")
            organizer = MediaOrganizer()
            organizer.ensure_folder_structure()
            print("✅ Folder structure created!")
        self._run_in_thread(task)

    def run_dry_run(self):
        def task():
            print("\n🔍 Running dry run (no files will be moved)...")
            organizer = MediaOrganizer(dry_run=True)
            organizer.ensure_folder_structure()
            count = organizer.process_raw_data()
            if count > 0:
                print(f"\n✅ Would organize {count} files")
            else:
                print("\n⚠ No files to organize")
        self._run_in_thread(task)

    def run_organize(self):
        def task():
            print("\n🚀 Organizing files from _RawData...")
            organizer = MediaOrganizer(dry_run=False)
            organizer.ensure_folder_structure()
            organizer.process_raw_data()
            organizer.print_stats()
        self._run_in_thread(task)
        
    def run_fix(self):
        def task():
            print("\n🔧 FIXING EXISTING FILES")
            organizer = MediaOrganizer(dry_run=False)
            fixed_count = organizer.fix_existing_files()
            if fixed_count > 0:
                print(f"\n✅ Fixed {fixed_count} files")
            else:
                print("\n✅ No files needed fixing")
        self._run_in_thread(task)

    def run_validate(self):
        def task():
            print("\n✅ Validating folder structure...")
            issues = []
            if Path(self.path_vars['photos'].get()).exists():
                photo_issues = PhotoStructure(Path(self.path_vars['photos'].get())).validate_structure()
                if photo_issues: issues.extend([f"Photos: {i}" for i in photo_issues])
            if Path(self.path_vars['videos'].get()).exists():
                video_issues = VideoStructure(Path(self.path_vars['videos'].get())).validate_structure()
                if video_issues: issues.extend([f"Videos: {i}" for i in video_issues])
            if Path(self.path_vars['audio'].get()).exists():
                audio_issues = AudioStructure(Path(self.path_vars['audio'].get())).validate_structure()
                if audio_issues: issues.extend([f"Audio: {i}" for i in audio_issues])
                
            if issues:
                print("\n⚠ Issues found:")
                for i in issues: print(f"  - {i}")
            else:
                print("\n✅ All folders are valid")
        self._run_in_thread(task)

    def run_stats(self):
        def task():
            print("\n📊 Gathering statistics...")
            stats = {'Photos': 0, 'Videos': 0, 'Audio': 0}
            
            p_dir = Path(self.path_vars['photos'].get())
            if p_dir.exists():
                stats['Photos'] = sum(1 for f in p_dir.rglob("*") if f.is_file())
                
            v_dir = Path(self.path_vars['videos'].get())
            if v_dir.exists():
                stats['Videos'] = sum(1 for f in v_dir.rglob("*") if f.is_file())
                
            a_dir = Path(self.path_vars['audio'].get())
            if a_dir.exists():
                stats['Audio'] = sum(1 for f in a_dir.rglob("*") if f.is_file())
                
            total = sum(stats.values())
            print("\n📁 File counts:")
            for k, v in stats.items():
                if v > 0: print(f"  {k}: {v:,} files")
            print(f"\n📈 TOTAL: {total:,} files")
        self._run_in_thread(task)


def launch_gui():
    root = tk.Tk()
    app = MediaOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()
