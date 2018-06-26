import sys
from argparse import ArgumentParser, Namespace
from multiprocessing import Pool
from typing import NoReturn

from config import logging
from models import TABLES, Users
from models.utils import create_tables, drop_tables, update_user_schedule


def parse_argv() -> Namespace:
    parser = ArgumentParser(description="Database actions", prog="db")
    parser.add_argument("action", type=str, help="init | drop | update")
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
        "--noNextWeek",
        action="store_false",
        help="fetch schedule only for current week"
    )
    return parser.parse_args()


def update_user_schedule_next_week(user: Users) -> NoReturn:
    update_user_schedule(user, date_bias=8)


if __name__ == "__main__":
    args = parse_argv()
    action = args.action.strip().lower()
    if action == "init":
        create_tables(*TABLES)
    elif action == "drop":
        drop_tables(*TABLES)
    elif action == "update":
        pool = Pool(args.workers)
        pool.map(
            update_user_schedule,
            map(lambda u: u, Users),
            chunksize=100
        )
        if args.noNextWeek:
            logging.info("Update user schedules for the next week")
            pool.map(
                update_user_schedule_next_week,
                map(lambda u: u, Users),
                chunksize=100
            )
    else:
        print(f"Wrong command:\t{args.action}", file=sys.stderr)
