import logging
from pathlib import Path
from datetime import datetime
import sys


class AppLogger:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.logger = logging.getLogger("voice_image_tool")
        self.logger.setLevel(logging.DEBUG)
        self._configure_handlers()

    def _configure_handlers(self):
        if self.logger.handlers:
            return

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console_fmt = logging.Formatter(
            '%(levelname)s | %(asctime)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console.setFormatter(console_fmt)
        self.logger.addHandler(console)
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)

            log_file = log_dir / f"tool_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)

            file_fmt = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_fmt)
            self.logger.addHandler(file_handler)
        except OSError as error:
            print(f"Warning: Unable to create log file - {error}")

    def get_logger(self):
        return self.logger


def setup_logging():
    app_logger = AppLogger()
    return app_logger.get_logger()


def validate_audio_format(filename: str) -> bool:
    supported_extensions = {
        'mp3', 'mp4', 'webm'
    }

    if not filename:
        return False

    extension = Path(filename).suffix.lstrip('.').lower()
    return extension in supported_extensions


def format_file_size(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

