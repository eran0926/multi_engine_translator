import logging
import sys
import queue
from logging.handlers import TimedRotatingFileHandler, QueueHandler, QueueListener
import configparser
from pathlib import Path
from os.path import join

# read config
config = configparser.ConfigParser(interpolation=None)
# config.read(Path("app\config\config.ini"))
# print(Path(__file__).parent.parent.joinpath('config','config.ini'))
# print(Path(__file__).parent.parent.joinpath('config','config.ini').is_file)
config.read(Path(__file__).parent.parent.joinpath('config', 'config.ini'))
# print(config.sections())
FORMAT = config["logger"]["log_format"]
FORMATTER = logging.Formatter(config["logger"]["log_format"])
LOG_FILE = config["logger"]["log_file"]
LOG_FILE = join("Logs", LOG_FILE)

# logging.basicConfig(level=logging.DEBUG, format=FORMAT)


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler(log_file=LOG_FILE):
    log_file = log_file or LOG_FILE
    file_handler = TimedRotatingFileHandler(
        log_file, when='midnight', encoding="utf-8")
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_queue_handler(que):
    queue_handler = QueueHandler(que)
    queue_handler.setFormatter(FORMATTER)
    return queue_handler


def get_logger(logger_name="main", log_file=None, level=logging.DEBUG, propagate=False, queue_handler=False):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(get_console_handler())
    if not queue_handler:
        logger.addHandler(get_file_handler(log_file=log_file))
    else:
        que = queue.Queue(-1)
        logger.addHandler(get_queue_handler(que))
        listener = QueueListener(
            que, get_file_handler(log_file=log_file))
        listener.start()
    logger.propagate = propagate
    return logger


if __name__ == "__main__":
    # main_logger = get_logger("main", log_file="testlogfile")
    main_logger = get_logger("main")
    main_logger.debug("test")
    main_logger.debug("test")
