from datetime import datetime
from collections import Collection

from config import PG_CONN
from mixins import LoggerMixin
from peewee import (CharField, DateTimeField, ForeignKeyField, IntegerField,
                    Model, PrimaryKeyField)
from playhouse.pool import PostgresqlDatabase
from playhouse.shortcuts import RetryOperationalError


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
    student = ForeignKeyField(
        Users,
        to_field='telegrma_id',
        on_update='CASCADE',
        db_column='student_tg_id'
    )
    monday = CharField()
    tuesday = CharField()
    wednesday = CharField()
    thursday = CharField()
    friday = CharField()
    saturday = CharField()
    sunday = CharField()
    upd_dt = DateTimeField()


TABLES = [
    Users,
    Lessons
]


class DBManager(LoggerMixin):
    ''' Handle db actions with ability to log them '''

    def __init__(self, db: ..., tables: Collection, **kwargs):
        self.db = db
        self.tables = list(tables)  # to make field mutable
        super(DBManager, self).__init__(**kwargs)

    def create(self) -> None:
        ''' Create all tables '''
        for table in self.tables:
            self._logger.info("create %s", table)
            table.create_table()

    def drop(self) -> None:
        ''' Remove all tables '''
        for table in reversed(self.tables):
            if table.table_exists():
                self._logger.info("drop %s", table)
                table.drop_table()

    def init(self, rebase: bool=True) -> None:
        if rebase:
            try:
                self.drop()
                self._logger.info("Tables [%s] dropped", self.tables)
            except BaseException as excinfo:
                self._logger.error(excinfo)
        try:
            self.create()
            self._logger.info("Tables [%s] created", self.tables)
        except BaseException as excinfo:
            self._logger.error(excinfo)

    def save(self, data: list, table_name: object) -> None:
        '''
            Upsert (insert many rows for some condition) database.

            :param data: list, required. A list of dicts: Each dict must
                correlate with field_name of the given table
            :param table_name: object, required. a class of a table
            :return None

            Example:
                table_name: Lessons,
                data = [{'monday': '', 'tuesday':''…}, {…}]
        '''
        with self.db.atomic():
            table_name.insert_many(data).upsert().execute()


if __name__ == '__main__':
    db_manager = DBManager(db, TABLES)
    db_manager.init()
