# -*- coding: utf-8 -*-
import functools
import logging; logger = logging.getLogger(__name__)


class ActionException(Exception):

    def __init__(self, message=None, **kwargs):
        super(ActionException, self).__init__(**kwargs)
        self.message = message

    pass


def strategy_exception(handled_errors: list = []):
    def exception_decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as e:
                if type(e.__cause__) not in handled_errors \
                        and type(e) not in handled_errors:
                    # log the exception
                    err = "There was an exception in  "
                    err += function.__name__
                    err += str(e)
                    logger.exception(err)

                    # re-raise the exception
                    raise ActionException(err)
                else:
                    # return do not continue status for Action
                    logger.debug('A Error due to `%s` was handled', e)
                    return None, False

        return wrapper

    return exception_decorator
