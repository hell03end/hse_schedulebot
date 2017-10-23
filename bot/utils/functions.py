from collections import Callable
from functools import wraps

import telegram
from bot.utils.keyboards import BACK_KEY
from telegram.bot import Bot
from telegram.update import Update


def is_cancelled(msg: str) -> bool:
    return msg.strip('/').lower() in ('back', 'start')


def is_back(msg: str) -> bool:
    return msg == BACK_KEY[0]


def typing(func: Callable) -> Callable:
    @wraps(func)
    def decorator(bot: Bot, update: Update, *args, **kwargs) -> object:
        bot.send_chat_action(
            chat_id=update.message.chat.id,
            action=telegram.ChatAction.TYPING
        )
        return func(bot, update, *args, **kwargs)
    return decorator
