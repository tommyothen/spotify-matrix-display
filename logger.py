# logger.py
import os
import logging
from datetime import datetime


class Logger:
    def __init__(self, name, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Create a file handler
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_handler = logging.FileHandler(f"logs/{name}_{timestamp}.log")
        file_handler.setLevel(level)

        # Create a console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # Create a formatter and add it to the handlers
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(CustomFormatter())

        # Add the handlers to the logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors"""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt=None, datefmt=None, style="%"):
        super().__init__(fmt, datefmt, style)

    def format(self, record):
        log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        if record.levelno == logging.DEBUG:
            log_fmt = self.grey + log_fmt + self.reset
        elif record.levelno == logging.INFO:
            log_fmt = self.blue + log_fmt + self.reset
        elif record.levelno == logging.WARNING:
            log_fmt = self.yellow + log_fmt + self.reset
        elif record.levelno == logging.ERROR:
            log_fmt = self.red + log_fmt + self.reset
        elif record.levelno == logging.CRITICAL:
            log_fmt = self.bold_red + log_fmt + self.reset

        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
