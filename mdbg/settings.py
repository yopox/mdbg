import os
import sys
import logging
from pathlib import Path
import shutil

from logging.handlers import RotatingFileHandler


APP_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = True

if DEBUG:
    DATA_DIR = APP_DIR
else:
    DATA_DIR = os.path.join(str(Path.home()), ".mdbg", "")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

# Logger stuff
logger = logging.getLogger()

if DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

# File log

file_handler = RotatingFileHandler(
    os.path.join(DATA_DIR, 'log.txt'), 'a', 1000000, 1)


if DEBUG:
    file_handler.setLevel(logging.DEBUG)
else:
    file_handler.setLevel(logging.INFO)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


stream_handler = logging.StreamHandler()

if DEBUG:
    stream_handler.setLevel(logging.DEBUG)
else:
    stream_handler.setLevel(logging.INFO)

stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
