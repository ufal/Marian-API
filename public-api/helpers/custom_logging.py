import logging
import time


def update_logger_with_new_format(name, new_format):
    logger = logging.getLogger(name)
    formatter = logging.Formatter(new_format)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    for hdlr in logger.handlers[:]:  # remove all old handlers
        logger.removeHandler(hdlr)
    logger.addHandler(handler)


def setup_custom_logger(name, new_format):
    logging.Formatter.converter = time.gmtime
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(new_format)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
