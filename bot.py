import logging
import sys

from telegram.ext import Updater
from telegram import Bot

from config import sentry_handler, TOKENS


bot = Bot(TOKENS['KIMBERBOT'])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        token = sys.argv[-1].upper()
        if token in TOKENS:
            updater = Updater(TOKENS[token])
            bot = Bot(TOKENS[token])
            logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                level=logging.INFO)
    else:
        updater = Updater(TOKENS['TEST'])
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)

    dp = updater.dispatcher


    make_pause.register(dp)
    make_unpause.register(dp)
    delete_client.register(dp)
    stop_task.register(dp)
    all_tasks.register(dp)
    start_planned_task.register(dp)
    start_task.register(dp)
    reports.register(dp)
    add_company.register(dp)
    planned_tasks.register(dp)
    sign_out.register(dp)
    edit_planned_tasks.register(dp)

    admin.register(dp)

    search_docs.register(dp)
    add_doc.register(dp)

    make_act.register(dp)
    make_invoice.register(dp)

    handle_inline.register(dp)
    common.register(dp)
    updater.start_polling()
    updater.idle()
