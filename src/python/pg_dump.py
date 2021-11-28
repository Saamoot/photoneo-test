import os
import sys
from subprocess import PIPE, Popen
import shlex
import argparse
from zipfile import ZipFile


def parse_arguments():
    parser = argparse.ArgumentParser(description='Create wiki js markdown page via graphql api.')

    parser.add_argument(
        '--action',
        help='Database dump action, values: dump, restore'
    )

    parser.add_argument(
        '--database-host',
        default='database',
        help='Database host url/domain/ip'
    )

    parser.add_argument(
        '--database-name',
        default='wiki_js',
        help='Name of database to be dumped/restored'
    )

    parser.add_argument(
        '--database-user',
        default='username',
        help='Username for database authentication'
    )

    parser.add_argument(
        '--database-password',
        default='myPassword',
        help='Password for database authentication'
    )

    parser.add_argument(
        '--dump-file',
        default='/vagrant/python/dump.sql',
        help='Location where to: save file when "dump-ing", look for file when "restore-in"'
    )

    return parser.parse_args()


def dump_database(host_name, database_name, user_name, output_file):
    command = f'sudo docker exec photoneo-test_database_1 pg_dump {database_name} -U {user_name}'

    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    result = process.communicate()

    file_handle = open(output_file, 'w')
    for line in result:
        file_handle.write(bytes(line).decode('utf-8'))
    file_handle.close()

    zip_file = output_file + '.zip'

    zip_files(zip_file, [output_file])

    print('raw sql dump: ' + output_file)
    print('zip sql dump: ' + zip_file)
    print('"/vagrant/python" is virtual host directory mapped on host directory ".../{project-root}/src/python"')


def restore_database(host_name, database_name, user_name, input_file):
    # Remove the '<' from the pg_restore command.
    command = f'sudo docker exec photoneo-test_database_1 '
    command += f'pg_restore -h {host_name} -d {database_name} -U {user_name} {input_file}'

    # Use shlex to use a list of parameters in Popen instead of using the
    # command as is.
    command = shlex.split(command)

    # Let the shell out of this (i.e. shell=False)
    p = Popen(command, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    result = p.communicate()

    print(result)

    return result


def zip_files(zip_file_name, file_names):
    zip_file_handle = None
    try:
        with ZipFile(zip_file_name, 'w') as zip_file_handle:
            for file_name in file_names:
                zip_file_handle.write(file_name)
    except Exception as e:
        print('Error %s' % e)
        sys.exit(2)
    finally:
        if zip_file_handle:
            zip_file_handle.close()


def main():
    arguments = parse_arguments()

    if 'dump' == arguments.action:
        dump_database(
            host_name=arguments.database_host,
            database_name=arguments.database_name,
            user_name=arguments.database_user,
            output_file=arguments.dump_file
        )
    elif 'restore' == arguments.action:
        restore_database(
            host_name=arguments.database_host,
            database_name=arguments.database_name,
            user_name=arguments.database_user,
            input_file=arguments.dump_file
        )
    else:
        print(f'Invalid action supplied, allowed: dump, restore; got {arguments.action}')
        sys.exit(1)

    sys.exit(1)


main()
