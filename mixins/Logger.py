from collections import Callable
from functools import wraps

LEVELS = {
    "NOTSET": 0,
    "DEBUG": 10,
    "INFO": 20,
    "WARN": 30,
    "WARNING": 30,
    "ERROR": 40,
    "FATAL": 50,
    "CRITICAL": 50
}


def Logger(name: str, level: int=LEVELS["DEBUG"], **kwargs) -> ...:
    '''Create new logger instance (lazy import evaluation)'''
    import logging
    logging.basicConfig(
        format=kwargs.pop(
            "format",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        level=level
    )
    return logging.getLogger(name)


def log(func: Callable):
    '''
        Wrapper for logging function actions.

        Also add _logger attribute to wrapped function to enable logging
        while execution.
    '''
    logger = Logger(func.__module__)

    @wraps(func)
    def decorator(*args, **kwargs):
        logger.info("Entering: {}".format(func.__name__))
        for arg in args:
            logger.info(arg)
        if "_logger" not in func.__dict__:
            func._logger = logger
        result = func(*args, **kwargs)
        logger.info("Exiting: {}".format(func.__name__))
        return result

    return decorator


class LoggerMixin(object):
    '''Add logger to class'''

    def __init__(self, **kwargs):
        params = {}
        level = kwargs.pop("level", None)
        if level:
            params['level'] = level
        fmt = kwargs.pop("format", None)
        if fmt:
            params['format'] = fmt
        self._logger = Logger(str(self.__class__), **params)
        super(LoggerMixin, self).__init__()
