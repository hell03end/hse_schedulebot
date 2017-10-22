from telegram.ext.dispatcher import Dispatcher


def register(dispatcher: Dispatcher) -> None:
    from bot import buses, schedule, service, trains

    buses.register(dispatcher)
    schedule.register(dispatcher)
    service.register(dispatcher)
    trains.register(dispatcher)


def init_db() -> None:
    from bot.models.tools import create_tables, drop_tables
    from bot.models import TABLES

    drop_tables(TABLES)
    create_tables(TABLES)


def run(token: str, logger_level: int=0) -> None:
    from telegram import Bot
    from telegram.ext import Updater
    import logging

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logger_level
    )

    updater = Updater(token)
    api = Bot(token)
    register(updater.dispatcher)

    updater.start_polling()
    updater.idle()
