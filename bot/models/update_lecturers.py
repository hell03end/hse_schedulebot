import re
from multiprocessing import Pool
from peewee import IntegrityError
from ruz import RUZ

from bot.models.models import Lecturers
from bot.utils.messages import MESSAGES

MESSAGES = MESSAGES['models:update_schedules']
api = RUZ()

patterns = (re.compile('ераспределенная'), re.compile('акансия'),
            re.compile('!'), re.compile('нагрузка'))

def save_lecturers(lecturer: dict) -> None:
    # Checking data
    match = False
    if not lecturer:
        match = True
    for key in ['fio', 'chair']:
        for p in patterns:
            match = p.search(lecturer[key])
    for word in lecturer['fio'].split()[:1]:
        match = not re.match(r'[A-ZА-Я].*', word)

    if match:
        return
    lect_dict = {
        'fio': lecturer['fio'],
        'chair': lecturer['chair'],
        'lecturer_id': lecturer['lecturerOid']
    }
    try:
        lect_obj, _ = Lecturers.get_or_create(lecturer_id=lect_dict['lecturer_id'],
                                              fio=lect_dict['fio'],
                                              chair=lect_dict['chair'],)
        Lecturers.update(**lect_dict).where(Lecturers.lecturer_id == lect_obj.lecturer_id).execute()
    except IntegrityError:
        print('!!!!!!!!!!!!!!!!!!!!!!', lect_dict)

def get_lecturers() -> list:
    return api.lecturers()


def main() -> None:
    pool = Pool(5)
    pool.map(save_lecturers, get_lecturers(), chunksize=35)
