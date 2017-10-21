from multiprocessing import Pool
from threading import Thread

from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, RegexHandler, CommandHandler, \
    Filters, MessageHandler
from models import Users
from config import ADMINS
from utils.functions import is_cancelled
from utils.keyboards import START_KEYBOARD
from service.common_handlers import start
from utils.states import WHOM_TO_SEND, PREPARE_MAILING
from logger import log


@log
def do_mailing(bot, recipients, msg, author):
    pool = Pool(10)
    data = set()
    for recipient in recipients:
        data.add((recipient.telegram_id, msg, ParseMode.HTML))
    result = pool.starmap(bot.send_message, data)
    bot.send_message(
        author,
        f'Разослал. Сообщение получили {len(result)}'
    )


@log
def whom_to_send(bot, update, user_data):
    uid = update.message.from_user.id
    if uid in ADMINS:
        send_params = {
            'text': 'Кому будем рассылать',
            'chat_id': uid,
            'reply_markup': ReplyKeyboardMarkup([
                ['Всем'],
                [['Студентам', 'Преподавателям']],
                ['Назад']
            ])
        }
        user_data['whom_to_send_sp'] = send_params

        bot.send_message(**send_params)
        return WHOM_TO_SEND
    return ConversationHandler.END


@log
def recipients(bot, update, user_data):
    uid = update.message.from_user.id
    message = update.message.text
    if is_cancelled(message):
        bot.send_message(**user_data['whom_to_send_sp'])
        return ConversationHandler.END
    if message == 'Всем':
        user_data['recipients'] = 'all'
    elif message == 'Преподавателям':
        user_data['recipients'] = 'lecturers'
    elif message == 'Студентам':
        user_data['recipients'] = 'students'

    send_params = {
        'text': 'Напиши, что будем отправлять',
        'chat_id': uid,
        'reply_markup': ReplyKeyboardMarkup([
            ['Назад']],
            resize_keyboard=1
        )
    }

    user_data['recipients_sp'] = send_params

    bot.send_message(**send_params)
    return PREPARE_MAILING


@log
def prepare_mailing(bot, update, user_data):
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
            'Начал рассылку. Я напишу тебе, когда закончу',
            reply_markup=ReplyKeyboardMarkup(START_KEYBOARD)
        )
    else:
        bot.send_message(uid, 'Некому отправлять :(')
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
