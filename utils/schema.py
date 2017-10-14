# api v1
DATA_SCHEMA = [
    {
        'auditorium': str,
        'auditoriumOid': int,
        'beginLesson': str,
        'building': str,
        'date': str,
        'dateOfNest': str,
        'dayOfWeek': int,
        'dayOfWeekString': str,
        'detailInfo': str,
        'discipline': str,
        'disciplineinplan': str,
        'disciplinetypeload': int,
        'endLesson': str,
        'group': None,
        'groupOid': int,
        'isBan': bool,
        'kindOfWork': str,
        'lecturer': str,
        'lecturerOid': int,
        'stream': str,
        'streamOid': int,
        'subGroup': None,
        'subGroupOid': int
    }
]

# api v2
DATA_SCHEMA2 = {
    'Count': int,
    'Lessons': DATA_SCHEMA,
    'StatusCode': {
        'Code': int,
        'Description': str
    }
}

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

MESSAGE_SCHEMA = \
    "{time}\n**{name}**\n__{type}__\n{teacher}\n{room}, `{place}`"

POST_SCHEMA = "**{date}**\n~~~~~~~~~~~~~~~\n{messages}"
