import logging

from functools import wraps
from typing import Callable, Type


def singleton(_):
    """
    This decorator can only be used above the __new__ function of a class. It's responsible for returning a pre-created
    instance of the respective class or create a new one, if not have happened before.

    :param _: The __new__ function.
    """

    def apply_pattern(cls: Type, *args, **kwargs):
        # attention: *args and **kwargs must be included even if not used!
        if not hasattr(cls, 'instance'):
            cls.instance = super(cls.__class__, cls).__new__(cls)
        return cls.instance

    return apply_pattern


def log(logger_name: str):
    """
    This decorator can only be set on a FastAPI route function.

    It logs the request and response of the respective route.

    :param logger_name:
    """
    logger = logging.getLogger(logger_name)

    def log_func(route: Callable):

        @wraps(route)
        def wrapper(*args, **kwargs):
            logger.debug('>>>> Entering route with following arguments:')

            for arg in args:
                logger.debug(arg)

            for k, w in kwargs.items():
                logger.debug('{}: {}'.format(k, w))

            response = route(*args, **kwargs)

            logger.debug('<<<< Exiting route with following response:')
            logger.debug('{}'.format(response))

            return response

        return wrapper

    return log_func
