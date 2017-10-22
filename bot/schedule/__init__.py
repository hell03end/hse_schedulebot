from telegram.ext.dispatcher import Dispatcher


def register(dispatcher: Dispatcher) -> None:
    from bot.schedule.week import register as week_schedule_reg
    from bot.schedule.day import register as day_schedule_reg

    week_schedule_reg(dispatcher)
    day_schedule_reg(dispatcher)
