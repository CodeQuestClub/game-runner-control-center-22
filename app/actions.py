from time import sleep
import json
import secrets
from printers import create_leaderboard_data, print_matches, print_aws_tasks
import os


def create_instance(client, instance_count=1):
    with open(os.path.abspath(os.getcwd()) + '/app/run_task_request.json') as request_file:
        request = json.load(request_file)
    request['overrides']['containerOverrides'][0]['environment'].extend([
        {'name': 'client_id', 'value': secrets.aws_access_key_id},
        {'name': 'client_key', 'value': secrets.aws_secret_access_key},
        {'name': 'server_url', 'value': secrets.server_url},
        {'name': 'worker_id', 'value': None}
    ])
    for worker_id in range(instance_count):
        list(filter(
            lambda x: x['name'] == 'worker_id',
            request['overrides']['containerOverrides'][0]['environment']
        ))[0]['value'] = str(worker_id)

        client.run_task(**request, count=1)
        sleep(0.1)


def report(client):
    create_leaderboard_data()
    print('============================================')
    print('TASKS:')
    print_aws_tasks(client)
    print('============================================')
    print('MATCHES:')
    print_matches(secrets.server_url)
    print('============================================')

    # print('MATCH stats:')
    # print_games(server_url=secrets.server_url)
