# YouTube Downloader

A Kivy desktop app that downloads YouTube videos with quality selection,
organises them into a library, and plays them with the OS default player.

## Run

    pip install -r requirements.txt
    python main.py

## Build a Windows .exe

    pyinstaller --name YouTubeDownloader --windowed main.py

Then edit the generated .spec to add:

    from kivy_deps import sdl2, glew
    ...
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],

inside the COLLECT() call, and rerun `pyinstaller YouTubeDownloader.spec`.

The application icon and splash assets are stored in `assets/`. The Kivy
window uses `assets/icon.png`, while Buildozer packages the same icon,
`presplash.png`, and the adaptive icon layers for Android.