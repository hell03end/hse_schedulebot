import logging
from functools import wraps
from typing import Any, Callable


def log(func: Callable) -> Callable:
    """ Log function call details as DEBUG level """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        logging.debug("[%s]\tENTER", func_name)
        for arg in args:
            logging.debug("[%s]\tARG\t%s", func_name, arg)
        for key, value in kwargs.items():
            logging.debug("[%s]\tKWARG\t%s=%s", func_name, key, value)
        try:
            result = func(*args, **kwargs)
            logging.debug("[%s]\tEXIT", func_name)
            return result
        except BaseException as exc:
            logging.error(exc)
            raise exc
    return wrapper


def ilog(func: Callable) -> Callable:
    """ Log function call details as INFO level """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        logging.info("[%s]\tENTER", func_name)
        for arg in args:
            logging.info("[%s]\tARG\t%s", func_name, arg)
        for key, value in kwargs.items():
            logging.info("[%s]\tKWARG\t%s=%s", func_name, key, value)
        try:
            result = func(*args, **kwargs)
            logging.info("[%s]\tEXIT", func_name)
            return result
        except BaseException as exc:
            logging.error(exc)
            raise exc
    return wrapper
