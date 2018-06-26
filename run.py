import logging
from argparse import ArgumentParser, Namespace

import bot
from config import TOKEN


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Starts telegram bot for lessons "
                                        "schedule in HSE",
                            prog="HSE schedule bot")
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="%(prog)s 1.0"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=10,
        help="number of workers for running action"
    )
    parser.add_argument(
        "--token", "-t",
        type=str,
        default=TOKEN,
        help="telegram bot API token"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=None,
        help="webhook port"
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argv()
    bot.run(args.token, args.workers, args.port)
