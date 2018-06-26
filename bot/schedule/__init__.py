from typing import NoReturn

from telegram.ext.dispatcher import Dispatcher


def register(dispatcher: Dispatcher) -> NoReturn:
    from bot.schedule.start import register as start_schedule_reg

    start_schedule_reg(dispatcher)
