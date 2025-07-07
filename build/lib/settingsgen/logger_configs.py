import sys
import os
import logging

from load_dotenv import load_dotenv

try:
    import coloredlogs
except ImportError:
    coloredlogs = None

try:
    from .application_settings import loaded_settings
except ImportError:
    
    
    class Settings:
        mode: str = 'development'
    

    loaded_settings = Settings()

load_dotenv()

# Text Reset
RESET = "\033[0m"

# Text Styles
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
INVERT = "\033[7m" 

# Foreground Colors
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Bright Foreground Colors
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background Colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

# Bright Background Colors
BG_BRIGHT_BLACK = "\033[100m"
BG_BRIGHT_RED = "\033[101m"
BG_BRIGHT_GREEN = "\033[102m"
BG_BRIGHT_YELLOW = "\033[103m"
BG_BRIGHT_BLUE = "\033[104m"
BG_BRIGHT_MAGENTA = "\033[105m"
BG_BRIGHT_CYAN = "\033[106m"
BG_BRIGHT_WHITE = "\033[107m"


class CustomLogFormatter(logging.Formatter):
    
    def format(self, record):
        """Manually replace log parts and color them based on log level."""
        
        # Adjust the format dynamically based on log level
        if record.levelname == "DEBUG":
            log_format = f'{DIM}%(asctime)-5s{RESET} {BOLD}{GREEN}[%(levelname)-4s]{RESET}' \
                 f': {BOLD}"%(message)s"{RESET} {DIM}{UNDERLINE}%(name)-0s.%(filename)-5s {RESET}{BOLD}{GREEN}line %(lineno)d{RESET}'
        
        elif record.levelname == "ERROR":
            log_format = f'{DIM}{RED}%(asctime)-5s{RESET} {RED}[%(levelname)-4s]{RESET}' \
                 f': {BOLD}{BRIGHT_RED}"%(message)s"{RESET} {DIM}{RED}{UNDERLINE}%(name)-0s.{BRIGHT_RED}%(filename)-5s  {RESET}{BOLD}{RED}line %(lineno)d{RESET}'
        
        elif record.levelname == "WARNING":
            log_format = f'{DIM}{YELLOW}%(asctime)-5s{RESET} {YELLOW}[%(levelname)-4s]{RESET}' \
                 f': {BOLD}{BRIGHT_YELLOW}"%(message)s"{RESET} {DIM}{YELLOW}{UNDERLINE}%(name)-0s.{BRIGHT_YELLOW}%(filename)-5s {RESET}{BOLD}{YELLOW}line %(lineno)d{RESET}'
        
        elif record.levelname == "INFO":
            log_format = f'{DIM}%(asctime)-5s{RESET} [%(levelname)-4s]' \
                 f': {BOLD}"%(message)s"{RESET} {DIM}{UNDERLINE}%(name)-0s.%(filename)-5s  {RESET}line %(lineno)d'
        
        else:
            log_format = '%(asctime)-5s : %(levelname)-8s | %(name)-5s.%(filename)-5s ___ %(message)s'

        self._style._fmt = log_format
        return super().format(record)
    

class AppLogger:
    LOG_FORMAT_DEBUG = '%(asctime)-5s : %(levelname)-8s | %(name)-5s.%(filename)-5s :: %(message)s'
    LOG_FORMAT_PROD = '%(asctime)-15s %(levelname)s:%(name)s: %(message)s'
    LOG_LEVEL_PROD = logging.WARNING

    def __init__(self, settings) -> None:
        """Initialize logging configuration based on the environment."""
        self.settings = settings
        self.console_handler = logging.StreamHandler()
        self.date_format = "%Y-%m-%d %H:%M:%S"

        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.INFO)

        # Remove all existing handlers
        if werkzeug_logger.hasHandlers():
            werkzeug_logger.handlers.clear()

        if self.is_production():
            formatter = logging.Formatter(self.LOG_FORMAT_PROD, datefmt=self.date_format)
            self.console_handler.setFormatter(formatter)
            logging.basicConfig(level=self.LOG_LEVEL_PROD, handlers=[self.console_handler])
        else:
            formatter = CustomLogFormatter(self.LOG_FORMAT_DEBUG, datefmt=self.date_format)
            self.console_handler.setFormatter(formatter)
            logging.basicConfig(level=logging.DEBUG, handlers=[self.console_handler])

    def is_production(self) -> bool:
        """Determine if the environment is set to production."""
        return self.settings.mode.lower() == 'production'
    
    @staticmethod
    def disable_external_package_logging(package_names):
        for name in package_names:
            logging.getLogger(name).setLevel(logging.WARNING)

    @staticmethod
    def is_color_terminal() -> bool:
        """Check if terminal supports color output."""
        print(sys.stdout.isatty() and os.getenv('TERM') not in ('dumb', 'unknown'))
        return True


logger = AppLogger(loaded_settings)
