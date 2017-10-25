from bot.logger import log
from bot.models import Lecturers
from bot.service.common_handlers import send_cancel
from bot.utils.functions import is_back, is_cancelled, typing
from bot.utils.keyboards import SCHEDULE_KEYBOARD_STUDENT

from telegram import ParseMode, ReplyKeyboardMarkup
from telegram.bot import Bot
from telegram.ext import MessageHandler
from telegram.update import Update

def find(asked_fio: str) -> list:
    try:
        query = Lecturers.select().\
            where(Lecturers.fio.contains(asked_fio.lower())).\
            order_by(Lecturers.fio)
        return [{'fio': lect.fio} for lect in query]
    except Lecturers.DoesNotExist as err:
        print(err)
        return []


@log
@typing
def get_lecturers(bot: Bot, update: Update) -> None:
    lect_name = update.message.text
    bot.send_message(
        update.message.from_user.id,
        'Список найденных преподавателей. Выбери нужного:',
        reply_markup=ReplyKeyboardMarkup(find(lect_name), True)
    )
    return
