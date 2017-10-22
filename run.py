import logging
from argparse import ArgumentParser, Namespace

import bot
from config import TOKENS

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
        bot.models.update_schedules.main()
    elif args.action == "init_db":
        bot.init_db()
        print("DONE")
    elif args.action == "run":
        bot.run(
            token=TOKENS.get(args.token.upper(), TOKENS["TEST"]),
            logger_level=LOGGING_LEVELS.get(args.token.upper(), logging.DEBUG)
        )
