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
        '--database-container',
        default='photoneo-test_database_1',
        help='Name of container in which database is running'
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


def execute_command(command):
    process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    return process.communicate()


def dump_database(database_container, database_name, user_name, output_file):
    docker_dump_file_path = '/tmp/dump.sql'

    dump_database_command = f'sudo docker exec {database_container} pg_dump {database_name} -U {user_name}'
    dump_database_command += f'-Fc > {docker_dump_file_path}'

    copy_dump_from_container_command = f'sudo docker cp {database_container}:{docker_dump_file_path} {output_file}'

    execute_command(dump_database_command)
    execute_command(copy_dump_from_container_command)

    zip_file = output_file + '.zip'
    zip_files(zip_file, [output_file])

    print('raw sql dump: ' + output_file)
    print('zip sql dump: ' + zip_file)
    print('"/vagrant/python" is virtual host directory mapped on host directory ".../{project-root}/src/python"')


def restore_database(database_container, database_name, user_name, input_file):
    docker_dump_file = '/tmp/dump.sql'
    stop_database_container_command = 'sudo docker stop {database_container}}'
    start_database_container_command = 'sudo docker start {database_container}}'
    drop_database_command = f'sudo docker exec {database_container} dropdb {database_name} -U {user_name}'
    create_database_command = f'sudo docker exec {database_container} createdb -U {user_name} {database_name}'
    copy_input_file_command = f'sudo docker cp {input_file} {database_container}:{docker_dump_file}'
    restore_database_command = 'sudo docker exec {database_container}} psql '
    restore_database_command += f' -U {user_name} {database_name} < {docker_dump_file}'

    print('preparing container for restore: re-starting container, dropping and creating empty database')
    execute_command(stop_database_container_command)  # drops active connections
    execute_command(start_database_container_command)
    execute_command(drop_database_command)
    execute_command(create_database_command)
    print(f'restoring database from file {input_file} / {database_container}:{docker_dump_file}')
    execute_command(copy_input_file_command)
    execute_command(restore_database_command)


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
            database_container=arguments.database_container,
            database_name=arguments.database_name,
            user_name=arguments.database_user,
            output_file=arguments.dump_file
        )
    elif 'restore' == arguments.action:
        restore_database(
            database_container=arguments.database_container,
            database_name=arguments.database_name,
            user_name=arguments.database_user,
            input_file=arguments.dump_file
        )
    else:
        print(f'Invalid action supplied, allowed: dump, restore; got {arguments.action}')
        sys.exit(1)

    sys.exit(1)


main()
