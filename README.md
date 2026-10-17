
YouTube Downloader

A modern, cross-platform desktop application for downloading YouTube videos and audio with a clean Kivy-based interface. Built with Python, Kivy, and yt-dlp, it offers quality selection with estimated file sizes, an integrated library manager, and native folder picking.
---

Features

· Video and audio downloads — Choose between MP4 (video) or MP3 (audio) with a segmented toggle.
· Quality selection — After fetching a URL, pick from available resolutions with estimated file sizes (e.g., 1080p ~245.3 MB).
· Integrated library — Browse, play, reveal, and delete downloaded files from within the app.
· Native folder picker — Uses the OS dialog (Windows Explorer / macOS Finder / GTK) instead of a bundled chooser.
· Download progress — Real-time progress bar with percentage and speed readouts.
· Error handling — Clear, actionable status messages instead of raw tracebacks.
· Confirmation dialogs — Prevents accidental deletion with a proper confirmation prompt.
· Bundled ffmpeg — Ships with ffmpeg so merging and MP3 extraction work out of the box on Windows.
· Portable — No Python installation required for end users. The EXE runs standalone.

---

Tech Stack

Layer Technology
UI Framework Kivy 2.3.1
Downloader yt-dlp
Media Processing ffmpeg
Packaging PyInstaller + Inno Setup

---

Installation

For End Users (Windows)

1. Download YouTubeDownloader_Setup.exe from the Releases page.
2. Run the installer and follow the prompts.
3. Launch YouTube Downloader from the Start Menu.

Note on antivirus: Because the executable is not code-signed, Windows SmartScreen and some antivirus products may flag it on the first run. Click More info → Run anyway. This is normal for any unsigned PyInstaller application.

For Developers (from source)

Requirements:

· Python 3.11 or newer
· ffmpeg on your system PATH (or bundled in assets/ffmpeg/)

```bash
# Clone the repository
git clone https://github.com/yourusername/youtube-downloader.git
cd youtube-downloader

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

requirements.txt:

```
kivy>=2.2.0
yt-dlp>=2024.1.0
```

---

Usage

1. Paste a URL into the input field and click Fetch (or press Enter).
2. Choose a quality from the dropdown. File sizes are approximate and shown for reference.
3. Select a format: MP4 for video, MP3 for audio.
4. Pick a folder using the native Browse dialog, or keep the default (~/Downloads).
5. Click Download and watch the progress bar.
6. Switch to the Library tab to play, reveal, or delete downloaded files.

---

Building from Source

Windows EXE

1. Install build dependencies:
   ```powershell
   pip install pyinstaller pillow kivy_deps.sdl2 kivy_deps.glew
   ```
2. Place ffmpeg.exe and ffprobe.exe in assets/ffmpeg/.
3. Convert the icon:
   ```powershell
   python -c "from PIL import Image; Image.open('assets/icon.png').save('assets/icon.ico', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
   ```
4. Build:
   ```powershell
   pyinstaller --clean YouTubeDownloader.spec
   ```
5. The packaged app will be in dist/YouTubeDownloader/.

Windows Installer

1. Install Inno Setup.
2. Open installer_script.iss in Inno Setup Compiler.
3. Click Compile (F9).
4. The installer will be at Output/YouTubeDownloader_Setup.exe.

---

Project Structure

```
youtube-downloader/
├── main.py                     # Entry point
├── requirements.txt
├── YouTubeDownloader.spec      # PyInstaller build spec
├── installer_script.iss        # Inno Setup installer script
├── assets/
│   ├── icon.png                # 512x512 app icon
│   ├── icon.ico                # Windows icon
│   ├── icon_fg.png             # Android adaptive foreground
│   ├── icon_bg.png             # Android adaptive background
│   ├── presplash.png           # Android splash screen
│   └── ffmpeg/
│       ├── ffmpeg.exe
│       └── ffprobe.exe
└── app/
    ├── app.py                  # Kivy App + RootWidget
    ├── config.py               # Constants, palette, extensions
    ├── kv/                     # KV language files
    │   ├── common.kv
    │   ├── download.kv
    │   ├── library.kv
    │   └── root.kv
    ├── screens/
    │   ├── download_screen.py
    │   └── library_screen.py
    ├── services/
    │   ├── downloader.py       # yt-dlp download wrapper
    │   ├── fetcher.py          # Format discovery
    │   ├── library.py          # File scanning
    │   ├── player.py           # OS file handlers
    │   ├── folder_picker.py    # Native folder dialog
    │   └── ytdlp_helpers.py    # Shared utilities
    └── widgets/
        ├── field.py
        ├── progress.py
        ├── file_entry.py
        ├── nav_tab.py
        └── confirm_popup.py
```

---

Known Limitations

· Android support is currently blocked. The Buildozer toolchain requires a version of Python (3.14) that Kivy does not support. The Windows desktop build works perfectly. Android support will return when Kivy adds Python 3.14 support or when the ffmpeg binary is bundled via a manual recipe.
· No playlist support. The app is designed for single video downloads. Playlist support may be added in a future version.
· No code signing. The Windows installer is unsigned, which triggers SmartScreen warnings on first run.
· Requires internet. Obviously, but worth noting—no offline mode.

---

Roadmap

☐ Playlist downloads
☐ Download history with persistent metadata
☐ Custom thumbnail display in the library
☐ Subtitle download support
☐ Batch download queue
☐ macOS and Linux installers
☐ Code signing for Windows

---

Contributing

Contributions are welcome. To get started:

1. Fork the repository.
2. Create a feature branch: git checkout -b feature/your-feature.
3. Commit your changes: git commit -m "Add your feature".
4. Push to your branch: git push origin feature/your-feature.
5. Open a Pull Request.

Please open an issue first for major changes so we can discuss the approach.

---

Legal Notice

This tool is provided for personal, educational, and fair-use purposes only. Downloading copyrighted content without permission may violate YouTube's Terms of Service and local copyright laws. The authors of this project are not responsible for how you use it.

If you are a content creator or rights holder and believe this tool is being used to infringe your content, please open an issue and we'll address it.

---

License

This project is licensed under the MIT License. See LICENSE for details.

---

Acknowledgments

· Kivy — the UI framework that makes cross-platform Python apps possible.
· yt-dlp — the best YouTube downloader library available.
· ffmpeg — media processing backbone.
· shadcn/ui — for the design inspiration behind the interface.

---

Contact

· Author: Abdul Raqueb Nasif 
· Email: nasifabdul6@gmail.com
· GitHub: @Abdul-Nasif
