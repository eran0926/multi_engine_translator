import logging
import sys
from logging.handlers import TimedRotatingFileHandler
import configparser
from pathlib import Path

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


def get_logger(logger_name="main", log_file=None, level=logging.DEBUG, propagate=False):
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(log_file=log_file))
    logger.propagate = propagate
    return logger


if __name__ == "__main__":
    main_logger = get_logger("main", log_file="testlogfile")
    main_logger.debug("test")
