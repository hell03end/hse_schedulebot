from collections import Callable
from functools import wraps

import telegram
from bot.utils.keyboards import BACK_KEY
from telegram.bot import Bot
from telegram.update import Update


def is_cancelled(msg: str) -> bool:
    """ Check message is a command, which interrupts workflow """
    return msg.strip('/').lower() in ('back', 'start', 'cancel')


def is_back(msg: str) -> bool:
    """ Check message is 'go back' action """
    return msg == BACK_KEY[0]


def typing(func: Callable) -> Callable:
    """ Add typing status to bot actions """
    @wraps(func)
    def decorator(bot: Bot, update: Update, *args, **kwargs) -> object:
        bot.send_chat_action(
            chat_id=update.message.chat.id,
            action=telegram.ChatAction.TYPING
        )
        return func(bot, update, *args, **kwargs)
    return decorator
