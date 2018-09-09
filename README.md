HSE Schedule Bot
================

[![Telegram Group](https://img.shields.io/badge/Telegram-Group-blue.svg)](https://t.me/joinchat/A2Ahbgvbg3mq2b_WnDvWVw "Telegram support group")

Telegram bot to view the schedule of students/lecturers of the Scientific Research University [Higher School of Economics](https://www.hse.ru/). It uses [RUZ API](https://pypi.org/project/hse-ruz/).

**[Add on Telegram](https://t.me/hseschedule_bot)**.

**Any questions?** Please, [create an issue](https://github.com/evstratbg/hse_schedulebot/issues/new) or write ask a question in [Telegram Group](https://t.me/joinchat/A2Ahbgvbg3mq2b_WnDvWVw).


[What's new?](https://telegram.me/hse_bot_info)


Requirements
------------
* Python >= 3.6
* PostgreSQL


Installation
------------
```bash
    git clone https://github.com/evstratbg/hse_schedulebot.git
    cd hse_schedulebot
    pip install -p requirements.txt
    # modify config.py
    pytest -v
```


Usage
-----
**Don't forget to change `config.py!`**

```bash
    python run.py -h
    # or
    python run.py init_db  # create tables
    python run.py update_schedules
    python run.py run
```
