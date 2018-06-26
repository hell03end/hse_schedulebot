import logging
from typing import NoReturn

from telegram import Bot
from telegram.ext import Filters, MessageHandler, Updater
from telegram.ext import messagequeue as mq

from bot import schedule, service


class MQBot(Bot):
    def __init__(self,
                 *args,
                 is_queued_def: bool=True,
                 mqueue: mq.MessageQueue=None,
                 **kwargs) -> NoReturn:
        super(MQBot, self).__init__(*args, **kwargs)
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except BaseException as exc:
            logging.warning(exc)
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs) -> NoReturn:
        super(MQBot, self).send_message(*args, **kwargs)


def run(token: str, workers: int=10, port: int=None) -> NoReturn:
    # [feature] TODO: load previous state to continue chats correctly

    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    bot = MQBot(token, mqueue=q)
    updater = Updater(bot=bot, workers=workers)

    service.register(updater.dispatcher)
    schedule.register(updater.dispatcher)
    updater.dispatcher.add_handler(MessageHandler(Filters.text, start))

    if port:
        updater.start_webhook(port=port)
    else:
        updater.start_polling()
    updater.idle()
