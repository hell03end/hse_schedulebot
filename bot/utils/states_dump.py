# [feature] TODO: finish saving/loading dialogs sates

import logging
import pickle
import time
from threading import Thread
from typing import NoReturn

from telegram import Bot
from telegram.ext import ConversationHandler, Dispatcher


def load_data(conv_path: str, user_data_path: str) -> NoReturn:
    try:
        with open(conv_path, 'rb') as reader:
            ConversationHandler.conversations = pickle.load(reader)
        with open(user_data_path, 'rb') as reader:
            Dispatcher.user_data = pickle.load(reader)
    except FileNotFoundError as excinfo:
        logging.error("Data file not found: %s", excinfo)
    except BaseException as excinfo:
        logging.error(excinfo)


def save_data(period: float or int,
              conv_path: str,
              user_data_path: str) -> NoReturn:
    """ Infinite loop for with saving bot state """
    while True:
        time.sleep(period)
        # Before pickling
        resolved = {}
        for k, v in ConversationHandler.conversations.items():
            if isinstance(v, tuple) and len(v) is 2:
                try:
                    # Result of async function
                    new_state = v[1].result()
                except:
                    # In case async function raised an error,
                    # fall back to old state
                    new_state = v[0]
                resolved[k] = new_state
            else:
                resolved[k] = v
        try:
            with open(conv_path, 'wb+') as writer:
                pickle.dump(resolved, writer)
            with open(user_data_path, 'wb+') as writer:
                pickle.dump(Dispatcher.user_data, writer)
        except BaseException as excinfo:
            logging.error(excinfo)


def save_state(period: float or int=60, **kwargs) -> NoReturn:
    """ Start infinite state saving in separate thread """
    thread = Thread(
        name="save_data",
        args=period,
        kwargs=kwargs,
        target=save_data
    )
    thread.start()
