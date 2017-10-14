from collections import Collection
from datetime import datetime

from config import PG_CONN
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
        to_field='telegram_id',
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


TABLES = (Users, Lessons)


def create_tables(tables: Collection) -> None:
    for table in tables:
        if not table.table_exists():
            print("create table: {}".format(table))
            table.create_table()


def drop_tables(tables: Collection) -> None:
    for table in reversed(tables):
        if table.table_exists():
            print("drop table: {}".format(table))
            table.drop_table()


def save(data: Collection, table: object) -> None:
    """
        :param data - a collection of dicts: Each dict must correlate with
            field_name of the given table
        :param table - a class of a table

        Example:
        table: Lessons, data = [{'monday': '', 'tuesday':''…}, {…}]
    """
    with db.atomic():
        if table.table_exists():
            table.insert_many(data).upsert().execute()


if __name__ == '__main__':
    drop_tables(TABLES)
    create_tables(TABLES)
    print("DONE")
