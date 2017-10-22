import logging
from argparse import ArgumentParser, Namespace

from bot import schedule, service
from bot.models import TABLES, update_schedules
from bot.models.tools import create_tables, drop_tables
from config import TOKENS
from telegram import Bot
from telegram.ext import Updater

LOGGING_LEVELS = {
    'TEST': logging.INFO,
    'PROD': logging.DEBUG
}


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Starts telegram bot for lessons "
                                        "schedule in HSE")
    parser.add_argument('action', type=str,
                        help="run|update_schedules|init_db")
    parser.add_argument('--token', '-t', type=str, default="TEST",
                        help="api token name (from config) for access to bot")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argv()
    if args.action == "update_schedules":
        update_schedules.main()
        exit(0)
    elif args.action == "init_db":
        drop_tables(TABLES)
        create_tables(TABLES)
        print("DONE")
        exit(0)
    elif args.action != "run":
        exit(1)
    token = TOKENS.get(args.token.upper(), TOKENS["TEST"])
    updater = Updater(token)
    bot = Bot(token)
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=LOGGING_LEVELS.get(args.token.upper(), logging.DEBUG)
    )

    service.register(updater.dispatcher)
    schedule.register(updater.dispatcher)

    updater.start_polling()
    updater.idle()
