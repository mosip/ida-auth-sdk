import logging
import sys

def init_logger(config):
    logger = logging.getLogger()
    logger.setLevel(getattr(logging,config.logging.loglevel))
    fileHandler = logging.FileHandler(config.logging.log_file_name)
    streamHandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(config.logging.log_format)
    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    return logger
