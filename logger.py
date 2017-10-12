import logging
import functools


def log(func):
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    def decorator(*args, **kwargs):
        logger.info('Entering: %s', func.__name__)
        for a in args:
            logger.info(a)
        result = func(*args, **kwargs)
        logger.info('Exiting: %s', func.__name__)
        return result

    return decorator
