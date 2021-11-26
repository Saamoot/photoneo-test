import os
import sys
from zipfile import ZipFile
from dotenv import dotenv_values
import argparse

import psycopg2


def parse_arguments():
    parser = argparse.ArgumentParser(description='Dump postgresql database to file and compress it.')
    parser.add_argument(
        '--env-file',
        default='/data/projects/photoneo-test/src/docker-compose/.env',
        help='Configuration ".env" file',
        nargs='?'
    )

    parser.add_argument(
        '--output-file',
        default='/tmp/db-dump.sql.zip',
        help='Location of compressed file containing table dumps',
        nargs='?'
    )

    parser.add_argument(
        '--database-host',
        default=False,
        help='Overrides value from .env file - docker, internal container network',
        nargs='?'
    )

    return parser.parse_args()


def parse_env_file(file_name):
    config = dotenv_values(file_name)

    return config


def create_connection_to_database(database_config):
    database_host = database_config['DB_HOST']
    if arguments.database_host:
        database_host = arguments.database_host

    try:
        con = psycopg2.connect(
            user=f"{database_config['DB_USER']}",
            password=f"{database_config['DB_PASS']}",
            host=f"{database_host}",
            port=f"{database_config['DB_PORT']}",
            database=f"{database_config['DB_NAME']}"
        )
    except psycopg2.DatabaseError as e:
        print('Error %s' % e)
        sys.exit(1)

    return con


def get_database_tables(database_cursor):
    result = []

    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    rows = execute_query(database_cursor, query)

    for row in rows:
        result.append(row[0])

    return result


def execute_query(database_cursor, query):
    database_cursor.execute(query)
    return database_cursor.fetchall()


def get_table_column_names(database_cursor, table_name):
    result = []
    query = f'SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = \'{table_name}\';'

    rows = execute_query(database_cursor, query)

    for row in rows:
        result.append(row[0])

    return result


def get_table_dump(database_cursor, table_name):
    result = f'use {env_config["DB_NAME"]};\n'
    result += '\n'
    result += f'CREATE TABLE {table_name};\n'
    result += '\n'

    column_names = get_table_column_names(database_cursor, table_name)
    column_names = ', '.join(column_names)

    query = f'SELECT * FROM "{table_name}";'

    rows = execute_query(database_cursor, query)

    sub_result = []
    for row in rows:
        row_items = []
        for index in row:
            row_items.append(str(index))
        sub_result.append("'" + "','".join(row_items) + "'")

    sub_result = '(' + '),\n('.join(sub_result) + ')'
    result += f'INSERT INTO {table_name} ({column_names}) VALUES {sub_result};'

    return result


def dump_database_to_file(database_cursor, file_name):
    tables = get_database_tables(database_cursor)

    reset_file(file_name)
    base_dir = os.path.dirname(file_name)

    files = []
    for table in tables:
        table_file_name = base_dir + os.path.sep + table + '.sql'
        files.append(table_file_name)
        table_dump = get_table_dump(database_cursor, table)
        write_to_file(table_file_name, table_dump)

    zip_files(file_name, files)
    clean_files(files)


def reset_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


def write_to_file(file_name, data):
    file_handle = open(file_name, 'w')
    file_handle.write(data)
    file_handle.close()


def clean_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def zip_files(zip_file_name, file_names):
    print(zip_file_name)
    zip_file_handle = None
    try:
        with ZipFile(zip_file_name, 'a') as zip_file_handle:
            for file_name in file_names:
                zip_file_handle.write(file_name)
    except Exception as e:
        print('Error %s' % e)
        sys.exit(2)
    finally:
        if zip_file_handle:
            zip_file_handle.close()


def main():
    connection = create_connection_to_database(env_config)
    cursor = connection.cursor()

    dump_database_to_file(cursor, arguments.output_file)

    cursor.close()
    connection.close()
    sys.exit(0)


arguments = parse_arguments()
env_config = parse_env_file(arguments.env_file)

main()
