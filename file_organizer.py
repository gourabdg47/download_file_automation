from concurrent.futures import ThreadPoolExecutor
from os import scandir, rename, makedirs
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging
import os

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DEFAULT_DOWNLOAD_PATH = 'C:/Users/Shamik/Downloads'

DEST_DIR_IMAGES = join(DEFAULT_DOWNLOAD_PATH, 'Images')
DEST_DIR_VIDEOS = join(DEFAULT_DOWNLOAD_PATH, 'Videos')
DEST_DIR_MUSIC = join(DEFAULT_DOWNLOAD_PATH, 'Music')
DEST_DIR_SOFTWARES = join(DEFAULT_DOWNLOAD_PATH, 'Softwares')
DEST_DIR_SFX = join(DEFAULT_DOWNLOAD_PATH, 'SFX')
DEST_DIR_DOCS = join(DEFAULT_DOWNLOAD_PATH, 'Docs')
DEST_DIR_COMPRESSED: join(DEFAULT_DOWNLOAD_PATH, 'Compressed')
DEST_DIR_TORRENT: join(DEFAULT_DOWNLOAD_PATH, 'Torrent')

# supported image types
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# supported Video types
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# supported Audio types
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# supported Document types
document_extensions = [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]
# supported Torrent files
torrent_extensions = ['.torrent']

windows_extensions = [
    '.exe',
    '.msi',
    '.bat',
    '.cmd',
    '.ps1',
    '.jar',
    '.cab',
    '.dll',
    '.ocx',
    '.sys',
    '.msi',
    '.msix',
    '.msixbundle',
    '.appx',
    '.appxbundle',
    '.gz',
    '.7z'
]

macos_extensions = [
    '.dmg',
    '.pkg',
    '.app',
    '.zip'
]

linux_extensions = [
    '.deb',
    '.rpm',
    '.tar.gz',
    '.tgz',
    '.tar.bz2',
    '.tbz2',
    '.snap',
    '.AppImage',
    '.run'
]

# supported Software extentions
software_extensions = [windows_extensions, macos_extensions, linux_extensions]


def create_folder_check(folder_path: str) -> None:
    if not os.path.exists(folder_path):
        makedirs(folder_path)


def make_unique(dest: str, name: str):
    filename, extension = splitext(name)
    counter = 1
    while exists(join(dest, name)):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

def move_file(dest, entry, name):
    create_folder_check(dest)
    full_path = entry.path

    if exists(join(dest, name)):
        unique_name = make_unique(dest, name)
        old_name = join(dest, name)
        new_name = join(dest, unique_name)
        rename(old_name, new_name)

    move(full_path, dest)



class FileMoveHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(max_workers=5)  # Adjust the number of workers as needed

    def process_file(self, entry, name):
        # try:
        self.check_video_file(entry, name)
        self.check_audio_file(entry, name)
        self.check_image_file(entry, name)
        self.check_document_file(entry, name)
        self.check_executable_file(entry, name)

        # except Exception as e:
        #     logging.error(f"Error processing file {name}: {e}")

    def on_modified(self, event):
        with scandir(DEFAULT_DOWNLOAD_PATH) as files:
            for file in files:
                FILE_NAME = file.name
                self.executor.submit(self.process_file, file, FILE_NAME)


    def check_audio_file(self, entry, name):  # * Checks all Audio Files
        for audio_extension in audio_extensions:

            # audio_extensions_set = {ext.lower() for ext in audio_extensions}
            # if name.lower().endswith(audio_extensions_set):
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 10_000_000 or "SFX" in name:  # 10Megabytes
                    
                    dest = DEST_DIR_SFX
                else:
                    
                    dest = DEST_DIR_MUSIC

                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")
    
    def check_video_file(self, entry, name):  # Checks all Video Files
        for video_extension in video_extensions:

            if name.endswith(video_extension) or name.endswith(video_extension.upper()):

                move_file(DEST_DIR_VIDEOS, entry, name)
                logging.info(f"Moved video file: {name}")

    def check_image_file(self, entry, name):  # Checks all Image Files
        for image_extension in image_extensions:

            if name.endswith(image_extension) or name.endswith(image_extension.upper()):

                move_file(DEST_DIR_IMAGES, entry, name)
                logging.info(f"Moved image file: {name}")

    def check_document_file(self, entry, name):  # Checks all Document Files
        for documents_extension in document_extensions:

            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):

                move_file(DEST_DIR_DOCS, entry, name)
                logging.info(f"Moved document file: {name}")
                
    def check_executable_file(self, entry, name):  # Checks all Executable Files
        all_extensions = [ext for sublist in software_extensions for ext in sublist]
        
        for extension in all_extensions:
            file_extension = extension[(extension.rfind('.')) + 1 :]
            if name.endswith(file_extension) or name.endswith(file_extension.upper()):
                move_file(DEST_DIR_SOFTWARES, entry, name)
                logging.info(f"Moved document file: {name}")


    # def check_executable_file(self, entry, name):  # Checks all Executable Files
    #     all_extensions_set = set(ext for sublist in software_extensions for ext in sublist)

    #     file_extension = name[name.rfind('.') + 1:].lower()  # convert to lowercase for case-insensitive comparison
    #     if file_extension in all_extensions_set:
    #         move_file(DEST_DIR_SOFTWARES, entry, name)
    #         logging.info(f"Moved document file: {name}")


# Method to get called from Flask app
def start_file_observer():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    file_organizer_logger = logging.getLogger(__name__)

    path = DEFAULT_DOWNLOAD_PATH
    event_handler = FileMoveHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    file_organizer_logger = logging.getLogger(__name__)
    
    path = DEFAULT_DOWNLOAD_PATH
    event_handler = FileMoveHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
