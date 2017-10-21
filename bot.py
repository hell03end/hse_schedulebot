import logging
from argparse import ArgumentParser, Namespace

import schedule
import service
from config import TOKENS
from telegram import Bot
from telegram.ext import Updater


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Starts telegram bot for lessons "
                                        "schedule in HSE")
    parser.add_argument('--token', '-t', type=str, default="TEST",
                        help="api token name (from config) for access to bot")
    return parser.parse_args()


bot = Bot(TOKENS['TEST'])
LOGGING_LEVELS = {"TEST": logging.INFO}


if __name__ == '__main__':
    args = parse_argv()
    token = TOKENS.get(args.token.upper(), TOKENS["TEST"])
    updater = Updater(token)
    bot = Bot(token)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=LOGGING_LEVELS.get(token, logging.DEBUG)
    )

    service.register(updater.dispatcher)
    schedule.register(updater.dispatcher)

    updater.start_polling()
    updater.idle()
