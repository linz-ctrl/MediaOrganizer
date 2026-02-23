# 📁 Media Organizer

Hey there! Welcome to the **Media Organizer**. 

If you're tired of scrolling through thousands of photos and videos dumped into a single giant folder, or if you've ever copied a backup and lost all your file creation dates—this tool is for you!

The Media Organizer automatically sorts your photos, videos, and audio files into neat, chronological folders. But instead of relying on the unreliable file system "Date Created" timestamp (which often breaks when you move files), it actually peaks inside the files to read the embedded metadata (like EXIF data in photos). 

This means your memories end up exactly where they belong: in simple, device-agnostic `YYYY/MM/DD` folders.

## ✨ Why You'll Love It

- **Actually Chronological**: It reads the *real* creation dates hidden inside your files.
- **Visual Interface**: Use the neat graphical interface to point-and-click your way to organization.
- **Date-based Sanity**: No more folders with 10,000 items. Everything goes into folders like `2024/2024-01-15`.
- **Smart Audio Sorting**: It knows the difference between a voice memo, a podcast, an audiobook, and music, sorting them appropriately!
- **Play It Safe**: It includes a "Dry-run" mode so you can see what it *would* do before it actually moves a single file.

---

## 📁 What Your Folders Will Look Like

Say goodbye to chaos. Here is an example of what your library will look like after running the organizer:

```text
Photos/
└── 2023/
    ├── 2023-12-25/
    │   └── christmas.jpg
    └── 2023-11-10/
        └── vacation.mp4

Audio/
├── Music/
│   └── Artist Name/
│       └── Album Name/
│           └── track.mp3
├── Recordings/
│   └── 2024/
│       └── 2024-03-12/
│           └── voice_memo.m4a
└── Podcasts/
    └── Some Show/
        └── 2023/
            └── 2023-09-15/
                └── episode.mp3
```

---

## 🚀 Getting Started

It only takes a minute to get set up!

1. **Install dependencies**:
   Make sure you have Python installed, then run this in your terminal:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch the App!**
   Simply run the main script. The graphical interface will pop right up!
   ```bash
   python main.py
   ```

3. **Configure Your Folders**:
   In the app, click over to the **Configuration** tab. Here you can tell the organizer exactly where your messy `_RawData` lives, and where you want your clean `Photos`, `Videos`, and `Audio` folders to be stored. Don't forget to hit **Save**!

4. **Drop in your files and hit Organize**:
   Dump all your messy, unorganized media into the Raw Data folder. Then, hop over to the **Actions & Output** tab in the app and hit **Organize Files**. Sit back and watch the console do the heavy lifting!

---

## 🛠️ Power User? Prefer the Terminal?

If you prefer keeping your hands on the keyboard, you can absolutely run the Media Organizer in CLI mode. Just add the `--cli` flag:

```bash
python main.py --cli
```

From there, you'll get an interactive terminal menu where you can run:
- **Setup**: Create your base folder structure.
- **Dry run**: Simulate the moving process safely.
- **Organize**: Run the actual sorting pipeline.
- **Validate**: Check your folders and make sure nothing is broken.
- **Fix Existing**: Have files already in your folders that are in the wrong date folder? This will fix them.

---

## ⚙️ Advanced Configuration

If you're feeling adventurous and want to tweak how the magic works, you can open up `config.yaml` in your favorite text editor. You can customize:
-   The exact folder paths.
-   Date extraction priorities (e.g. tell it to check Video Metadata before EXIF).
-   Audio categorization rules.
-   Safety checks (like file size limits and backup behaviors).

---

## 🤝 Contributing & Acknowledgments

Feel free to fork the repository and submit pull requests if you have any awesome ideas to improve the tool. Large chunks of this magic wouldn't be possible without `exifread`, `Pillow`, and `mutagen`!

Happy organizing! 🎉