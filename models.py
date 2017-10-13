from peewee import *
from datetime import datetime
from config import PG_CONN
from playhouse.shortcuts import RetryOperationalError
from playhouse.pool import PostgresqlDatabase


class MyRetryDB(RetryOperationalError, PostgresqlDatabase):
    pass


db = MyRetryDB('hse_schedule', **PG_CONN)


class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db


class Users(BaseModel):
    telegram_id = IntegerField(unique=1)
    username = CharField(unique=1)
    email = CharField()
    dt = DateTimeField(default=datetime.now())


class Lessons(BaseModel):
    student = ForeignKeyField(Users,
                              to_field='telegram_id',
                              on_update='CASCADE',
                              db_column='student_tg_id')
    monday = CharField()
    tuesday = CharField()
    wednesday = CharField()
    thursday = CharField()
    friday = CharField()
    saturday = CharField()
    sunday = CharField()
    upd_dt = DateTimeField()


tables = [
    Users,
    Lessons
]


def init_db():
    for t in tables:
        print(t)
        t.create_table()


def del_tables():
    for t in reversed(tables):
        if t.table_exists():
            t.drop_table()


def save(data, table_name):
    """

    :param data:list, required. A list of dicts: Each dict must correlate
    with field_name of the given table
    :param table_name: object, required. a class of a table
    :return: None

    Example:
    table_name: Lessons,
    data = [{'monday': '', 'tuesday':''…}, {…}]
    """

    with db.atomic():
        table_name.insert_many(data).upsert().execute()
    return True


if __name__ == '__main__':
    del_tables()
    print('Таблицы удалил')
    init_db()
    print('Таблицы создал')
