youtube_downloader/
├── main.py
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py
│   ├── app.py                      # App + RootWidget + nav
│   ├── config.py                   # constants, palette, extensions
│   ├── kv/
│   │   ├── __init__.py             # load_all()
│   │   ├── common.kv               # shared widget styles
│   │   ├── download.kv             # <DownloadScreen>
│   │   ├── library.kv              # <LibraryScreen> + <FileEntry>
│   │   └── root.kv                 # <RootWidget> + ScreenManager
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── download_screen.py
│   │   └── library_screen.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ytdlp_helpers.py        # logger, stream guard, formatters
│   │   ├── fetcher.py              # format discovery
│   │   ├── downloader.py           # yt-dlp download wrapper
│   │   ├── library.py              # scan folder for videos
│   │   └── player.py               # open / reveal files via OS
│   └── widgets/
│       ├── __init__.py
│       ├── field.py
│       ├── progress.py
│       ├── file_entry.py
│       └── nav_tab.py
└── downloads/                      # created at runtime