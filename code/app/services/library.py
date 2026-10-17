"""Library: scan a folder for downloaded media files."""
import os

from app.config import MEDIA_EXTENSIONS, VIDEO_EXTENSIONS


class LibraryService:

    @staticmethod
    def list_files(directory):
        """Return a list of dicts (newest first) describing media files."""
        if not directory or not os.path.isdir(directory):
            return []

        items = []
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if not os.path.isfile(path):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in MEDIA_EXTENSIONS:
                continue
            try:
                st = os.stat(path)
            except OSError:
                continue
            items.append({
                "filename": name,
                "path": path,
                "size": st.st_size,
                "mtime": st.st_mtime,
                "kind": "video" if ext in VIDEO_EXTENSIONS else "audio",
            })

        items.sort(key=lambda x: x["mtime"], reverse=True)
        return items

    @staticmethod
    def delete_file(path):
        try:
            os.remove(path)
            return True, ""
        except OSError as exc:
            return False, str(exc)