# src/logger.py
from loguru import logger

# Basic logger that prints to stdout
logger.add(lambda msg: print(msg, end=""))
