import logging
from collections import Callable
from functools import wraps


def log(func: Callable) -> Callable:
    logger = logging.getLogger(func.__module__)

    @wraps(func)
    def decorator(*args, **kwargs) -> object:
        logger.info("Entering: {}".format(func.__name__))
        for arg in args:
            logger.info(arg)
        func._logger = logger
        result = func(*args, **kwargs)
        logger.info("Exiting: {}".format(func.__name__))
        return result

    return decorator
