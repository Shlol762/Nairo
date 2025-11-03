import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from discord.utils import _ColourFormatter as DiscordColourFormatter


LOG_FORMAT = (
    "[%(asctime)s] [%(levelname)-8s] [%(name)-25s] %(message)s (%(filename)s:%(lineno)d)"
)


def setup_logging(log_level=logging.INFO):

    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"Error creating log directory: {e}")
            sys.exit(1)

    log_file_path = os.path.join(log_dir, 'nairo.log')

    root_logger = logging.getLogger()

    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    root_logger.setLevel(log_level)


    try:
        console_handler = logging.StreamHandler(sys.stdout)

        console_formatter = DiscordColourFormatter(
            LOG_FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S",
            style="%"
        )

        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(log_level)
        root_logger.addHandler(console_handler)

    except Exception as e:
        print(f"Error setting up console logging: {e}")
    

    try:
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding='utf-8'
        )

        file_formatter = logging.Formatter(
            LOG_FORMAT,
            datefmt="%Y-%m-%d %H:%M:%S",
            style="%",
        )

        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
    
    except Exception as e:
        print(f"Error setting up file logging: {e}")
    
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)


    initial_logger = logging.getLogger(__name__)
    initial_logger.info(f"Logger configured. Log file at: {log_file_path}")


if __name__ == "__main__":
    setup_logging(log_level=logging.DEBUG)
    log = logging.getLogger("logger_test")
    log.debug("This is a debug message.")
    log.info("This is an info message.")
    log.warning("This is a warning message.")
    log.error("This is an error message.")
    log.critical("This is a critical message.")
