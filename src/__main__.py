import logging
from src.models import BBombsBot

try:
    from .config import Config
except ImportError:
    logging.fatal('Config file not found aborting.')
    exit(1)

bot = BBombsBot(Config())

if __name__ == '__main__':
    bot.run()