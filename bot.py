import logging
import sys

from config import TOKENS
from telegram import Bot
from telegram.ext import Updater

bot = Bot(TOKENS['TEST'])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        token = sys.argv[-1].upper()
        if token in TOKENS:
            updater = Updater(TOKENS[token])
            bot = Bot(TOKENS[token])
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                level=logging.INFO)
    else:
        updater = Updater(TOKENS['TEST'])
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)

    from service import common_handlers

    dp = updater.dispatcher
    common_handlers.register(dp)

    updater.start_polling()
    updater.idle()
