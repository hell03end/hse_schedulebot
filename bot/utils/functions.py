import logging
from functools import wraps
from typing import Callable

import telegram
from telegram import ParseMode
from telegram.bot import Bot
from telegram.ext import ConversationHandler
from telegram.update import Update

from bot.service.common_handlers import on_stop, send_cancel
from bot.utils.keyboards import BACK_KEY
from bot.utils.messages import MESSAGES

MESSAGES = MESSAGES['utils:functions']


def is_cancelled(msg: str) -> bool:
    """ Check message is a command, which interrupts workflow """
    return msg.strip('/').lower() in ('back', 'start', 'stop')


def is_stopped(msg: str) -> bool:
    """ Check message is a stop command """
    return msg.strip('/').lower() in ('stop')


def is_back(msg: str) -> bool:
    """ Check message is 'go back' action """
    return msg == BACK_KEY[0] or msg.strip('/').lower() in ('back')


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


def check_canceled(func: Callable) -> Callable:
    """ Check bot action is canceled """
    @wraps(func)
    def decorator(bot: Bot, update: Update, *args, **kwargs) -> object:
        if is_cancelled(update.message.text):
            send_cancel(
                bot,
                update.message.chat.id,
                user_data=kwargs.get('user_data')
            )
            logging.debug("Chat %d was canceled.", update.message.chat.id)
            return ConversationHandler.END
        return func(bot, update, *args, **kwargs)
    return decorator


def check_stopped(func: Callable) -> Callable:
    """ Check bot is stopped """
    @wraps(func)
    def decorator(bot: Bot, update: Update, *args, **kwargs) -> object:
        if is_stopped(update.message.text):
            logging.debug("Chat %d was stopped.", update.message.chat.id)
            on_stop(bot, update)
            return ConversationHandler.END
        return func(bot, update, *args, **kwargs)
    return decorator


def check_back(func: Callable) -> Callable:
    """ Check back action is sent to bot """
    @wraps(func)
    def decorator(bot: Bot, update: Update, *args, **kwargs) -> object:
        user_data = kwargs.get('user_data')
        if is_back(update.message.text):
            bot.send_message(
                update.message.chat.id,
                MESSAGES['check_back:msg'],
                ParseMode.HTML,
                reply_markup=user_data['reply_markup'] if user_data else None
            )
            return user_data['previous_state']
        return func(bot, update, *args, **kwargs)
    return decorator
