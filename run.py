import logging
import sys
from argparse import ArgumentParser, Namespace

import bot
from config import TOKENS

LOGGING_LEVELS = {
    'TEST': logging.DEBUG,
    'PROD': logging.INFO
}


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Starts telegram bot for lessons "
                                        "schedule in HSE")
    parser.add_argument('action', type=str,
                        help="run|update_schedules|init_db")
    parser.add_argument('--token', '-t', type=str, default="TEST",
                        help="api token name (from config) for access to bot")
    parser.add_argument('--workers', '-w', type=int, default=10,
                        help="number of workers for running bot")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argv()
    if args.action == "update_schedules":
        bot.update_schedules.main()
    elif args.action == "init_db":
        bot.init_db()
    elif args.action == "update_lecturers":
        bot.update_lecturers.main()
    elif args.action == "run":
        bot.run(
            token=TOKENS.get(args.token.upper(), TOKENS["TEST"]),
            logger_level=LOGGING_LEVELS.get(args.token.upper(), logging.DEBUG),
            workers=args.workers
        )
    else:
        print(f"Wrong command: {args.action}", file=sys.stderr)
