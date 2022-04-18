from time import sleep
import json
import secrets
from printers import print_matches, print_aws_tasks
import os
import boto3
import requests


def create_aws_client(type):
    return boto3.client(
        type,
        region_name='ap-southeast-2',
        aws_access_key_id=secrets.aws_access_key_id,
        aws_secret_access_key=secrets.aws_secret_access_key,
    )


def create_task_instance(instance_count=1):
    client = create_aws_client(type='ecs')
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


def get_leaderboard(server_url):
    response = requests.get(server_url).json()
    leaderboard = sorted(response['teams'], key=lambda x: x['score'], reverse=True)

    return leaderboard


def create_leaderboard_data():
    leaderboard_data = get_leaderboard(server_url=secrets.server_url)
    leaderboard = []
    for rank, team in enumerate(leaderboard_data):
        row = [rank + 1, team['name'], team['score']]
        leaderboard.append(row)

    with open(os.path.abspath(os.getcwd()) + '/app/leaderboard/leaderboard.json', 'w') as leaderboard_json:
        leaderboard_json.write(json.dumps(leaderboard))


def general_report():
    client = create_aws_client(type='ecs')

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


def download_replay(object_name):
    client = create_aws_client(type='s3')
    client.download_file('codequest-replays', object_name + '/replay.txt', os.path.abspath(os.getcwd()) + '/app/replays/' + object_name + '_replay.txt')


def delete_all_replays():
    s3 = boto3.resource(
        's3',
        aws_access_key_id=secrets.aws_access_key_id,
        aws_secret_access_key=secrets.aws_secret_access_key)

    bucket = s3.Bucket('codequest-replays')
    bucket.objects.all().delete()