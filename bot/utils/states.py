""" Collection of conversation states, used in bot """

DAY_OF_WEEK = 1
WHOM_TO_SEND = 2
PREPARE_MAILING = 3
ASK_EMAIL = 4
ASK_CITY = 5
SCHEDULE = 6
SETTINGS = 7

# regexpr triggers
TRIGGERS = {
    'info': r"(инфо|о боте|функции)",
    'all': r".*"
}
