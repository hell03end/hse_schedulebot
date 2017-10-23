from bot.models import Lecturers


def find(asked_fio: str) -> list:
    try:
        query = Lecturers.select(Lecturers.lecturer_id).\
            where(Lecturers.fio.contains(asked_fio.lower())).\
            order_by(Lecturers.fio)
        return [lect.lecturer_id for lect in query]
    except Lecturers.DoesNotExist:
        return []
