from bot.utils.keyboards import BACK_KEY


def is_cancelled(msg: str) -> bool:
    return msg.strip('/').lower() in ('back', 'start')


def is_back(msg: str) -> bool:
    return msg == BACK_KEY[0]
