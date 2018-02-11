import logging
from argparse import ArgumentParser, Namespace

import bot
from config import TOKENS


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
    action = args.action.lower()
    if action == "update_schedules":
        bot.update_schedules.main()
    elif action == "init_db":
        bot.init_db()
    elif action == "run":
        bot.run(token=TOKENS.get(args.token.upper(), TOKENS["TEST"]),
                workers=args.workers)
    else:
        logging.error("Wrong command '%s'", args.action)
