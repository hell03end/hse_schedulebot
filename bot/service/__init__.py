from telegram.ext.dispatcher import Dispatcher


def register(dispatcher: Dispatcher) -> None:
    from bot.service.common_handlers import register as common_handlers_reg
    from bot.service.mailing import register as mailing_reg
    from bot.service.settings import register as setting_reg

    setting_reg(dispatcher)
    common_handlers_reg(dispatcher)
    mailing_reg(dispatcher)
