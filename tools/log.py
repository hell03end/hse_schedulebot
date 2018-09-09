import logging
import os
from logging import Logger
from logging.handlers import RotatingFileHandler

FORMAT = "[%(asctime)s] %(levelname)s " \
    "[%(name)s.{%(filename)s}.%(funcName)s:%(lineno)d] %(message)s"


def get_file_handler(level: int=logging.WARNING,
                     fmt: str=FORMAT,
                     path: str="./",
                     filename: str=".log",
                     max_bytes: int=1024 * 100,
                     backup_count: int=10) -> RotatingFileHandler:
    if not os.path.exists(path):
        logging.info("create dir:\t%s", path)
        os.mkdir(path)
    log_path = os.path.join(path, filename)

    handler = RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(level)
    return handler


def get_stream_handler(level: int=logging.WARNING,
                       fmt: str=FORMAT) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    handler.setLevel(level)
    return handler


def get_file_logger(name: str,
                    level: int=logging.WARNING,
                    fmt: str=FORMAT,
                    path: str="./",
                    filename: str=".log",
                    max_bytes: int=1024 * 100,
                    backup_count: int=10,
                    **params) -> Logger:
    handler = get_file_handler(level, fmt, path, filename,
                               max_bytes, backup_count)
    logger = logging.getLogger(name, **params)
    logger.addHandler(handler)
    return logger


def get_stream_logger(name: str,
                      level: int=logging.WARNING,
                      fmt: str=FORMAT,
                      **params) -> Logger:
    handler = get_stream_handler(level, fmt)
    logger = logging.getLogger(name, **params)
    logger.addHandler(handler)
    return logger
