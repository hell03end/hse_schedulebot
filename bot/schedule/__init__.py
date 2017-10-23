from telegram.ext.dispatcher import Dispatcher


def register(dispatcher: Dispatcher) -> None:
    from bot.schedule.start import register as start_schedule_reg

    start_schedule_reg(dispatcher)
