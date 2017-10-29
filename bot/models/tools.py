from collections import Collection


def create_tables(tables: Collection) -> None:
    for table in tables:
        if not table.table_exists():
            print("create table: {}".format(table))
            table.create_table()


def drop_tables(tables: Collection) -> None:
    for table in reversed(tables):
        if table.table_exists():
            print("drop table: {}".format(table))
            table.drop_table(cascade=True)
