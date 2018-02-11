import logging


def create_tables(*tables) -> None:
    for table in tables:
        if not table.table_exists():
            logging.info("Create table: '%s'.", table)
            table.create_table()
        else:
            logging.info("Table '%s' already exists.", table)


def drop_tables(*tables) -> None:
    for table in reversed(tables):
        if table.table_exists():
            logging.info("Drop table: '%s'.", table)
            table.drop_table(cascade=True)
        else:
            logging.info("Table '%s' doesn't exist.", table)
