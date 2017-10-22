from multiprocessing import Pool
from threading import Thread

from config import ADMINS
from logger import log
from models import Users
from service.common_handlers import start
from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler)
from utils.functions import is_cancelled
from utils.keyboards import BACK_KEY, MAILING_WHOM_KEYBOARD, START_KEYBOARD
from utils.messages import MESSAGES
from utils.states import PREPARE_MAILING, WHOM_TO_SEND

MESSAGES = MESSAGES['mailing']


@log
def do_mailing(bot: object, recipients: object, msg: str, author: str) -> None:
    pool = Pool(10)
    data = set()
    for recipient in recipients:
        # maybe markdown?
        data.add((recipient.telegram_id, msg, ParseMode.HTML))
    result = pool.starmap(bot.send_message, data)
    bot.send_message(author, MESSAGES['do_mailing:end'].format(len(result)))


@log
def whom_to_send(bot: object, update: object, user_data: object) -> (int, str):
    uid = update.message.from_user.id
    if uid in ADMINS:
        send_params = {
            'text': MESSAGES['whom_to_send:ask'],
            'chat_id': uid,
            'reply_markup': ReplyKeyboardMarkup(MAILING_WHOM_KEYBOARD)
        }
        user_data['whom_to_send_sp'] = send_params

        bot.send_message(**send_params)
        return WHOM_TO_SEND
    return ConversationHandler.END


@log
def recipients(bot: object, update: object, user_data: object) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(**user_data['whom_to_send_sp'])
        return ConversationHandler.END
    if message == MAILING_WHOM_KEYBOARD[0][0]:
        user_data['recipients'] = 'all'
    elif message == MAILING_WHOM_KEYBOARD[1][-1]:
        user_data['recipients'] = 'lecturers'
    elif message == MAILING_WHOM_KEYBOARD[1][0]:
        user_data['recipients'] = 'students'

    send_params = {
        'text': MESSAGES['recipients:ask'],
        'chat_id': uid,
        'reply_markup': ReplyKeyboardMarkup([BACK_KEY], resize_keyboard=1)
    }

    user_data['recipients_sp'] = send_params

    bot.send_message(**send_params)
    return PREPARE_MAILING


@log
def prepare_mailing(bot: object, update: object,
                    user_data: object) -> (int, str):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(**user_data['recipients_sp'])
        return WHOM_TO_SEND

    recipients = Users.select()
    if user_data['recipients'] == 'students':
        recipients = recipients.where(Users.is_student == 1)
    elif user_data['recipients'] == 'lecturers':
        recipients = recipients.where(Users.is_student == 0)

    if recipients.exists():
        t = Thread(target=do_mailing, args=(bot, recipients, message, uid))
        t.start()
        bot.send_message(
            uid,
            MESSAGES['prepare_mailing:start'],
            reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
        )
    else:
        bot.send_message(uid, MESSAGES['prepare_mailing:empty'])
    return ConversationHandler.END


def register(dispatcher: object) -> None:
    start_admin = ConversationHandler(
        entry_points=[
            CommandHandler('mail', whom_to_send, pass_user_data=True)
        ],
        states={
            WHOM_TO_SEND: [
                MessageHandler(
                    Filters.text,
                    recipients,
                    pass_user_data=True
                )
            ],
            PREPARE_MAILING: [
                MessageHandler(
                    Filters.text,
                    prepare_mailing,
                    pass_user_data=True
                )
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dispatcher.add_handler(start_admin)
