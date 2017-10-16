LESSON_SCHEMA = {
    'beginLesson': str,
    'endLesson': str,
    'discipline': str,
    'kindOfWork': str,
    'lecturer': str,
    'building': str,
    'auditorium': str,
    'date': str,
    'dayOfWeek': int
}

TABLE_MAPPING = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday'
]

MESSAGE_SCHEMA = \
    "{time}\n**{name}**\n__{type}__\n{teacher}\n{room}, `{place}`"

POST_SCHEMA = "**{date}**\n~~~~~~~~~~~~~~~\n{messages}"
