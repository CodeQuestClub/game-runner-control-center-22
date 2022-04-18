import argparse
import boto3
import json
import secrets
import requests
from time import sleep


def create_instance(client, instance_count=1):
    with open('./run_task_request.json') as request_file:
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


def print_aws_tasks(client):
    stopped = client.list_tasks(
        cluster='codequest-worker-cluster',
        desiredStatus='STOPPED',
        launchType='FARGATE'
    )
    running = client.list_tasks(
        cluster='codequest-worker-cluster',
        desiredStatus='RUNNING',
        launchType='FARGATE'
    )
    pending = client.list_tasks(
        cluster='codequest-worker-cluster',
        desiredStatus='PENDING',
        launchType='FARGATE'
    )

    stopped_tasks = len(stopped['taskArns'])
    pending_tasks = len(pending['taskArns'])
    running_tasks = len(running['taskArns'])

    total_tasks = stopped_tasks + pending_tasks + running_tasks

    print('Total tasks: {} \n'
          'Running tasks: {} \n'
          'Pending tasks: {} \n'
          'Stopeed tasks: {}'.format(total_tasks, running_tasks, pending_tasks, stopped_tasks))


def get_leaderboard(server_url):
    response = requests.get(server_url).json()
    leaderboard = sorted(response['teams'], key=lambda x: x['score'], reverse=True)

    return leaderboard


def print_games(server_url):
    response = requests.get(server_url).json()
    groups = response['groups']
    matches = response['matches']

    for i, group in enumerate(map(sorted, groups)):
        print('Group #{}:'.format(i+1))
        for match in matches:
            if group == sorted(match['teams']):
                print("Match: team 1: {}, team 2: {}, team 3: {}, team 4: {} --- Status: {} --- results: {}".format(group[0], group[1], group[2], group[3], match['status'], match['results']))


def create_leaderboard_data():
    leaderboard_data = get_leaderboard(server_url=secrets.server_url)
    leaderboard = []
    for rank, team in enumerate(leaderboard_data):
        row = [rank+1, team['name'], team['score']]
        leaderboard.append(row)

    with open('./leaderboard/leaderboard.json', 'w') as leaderboard_json:
        leaderboard_json.write(json.dumps(leaderboard))


def report(client):
    create_leaderboard_data()
    print('============================================')
    print('TASKS:')
    print_aws_tasks(client)
    print('============================================')
    # print('LEADERBOARD:')
    # print('============================================')
    # print('MATCH SUMMARY:')
    # print_games(server_url=secrets.server_url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ci', '--create-instance', help='Create AWS ECS instance', type=int)
    parser.add_argument('-r', '--report', help='Show report of AWS instances', action='store_true')
    args = vars(parser.parse_args())

    client = boto3.client(
        'ecs',
        region_name='ap-southeast-2',
        aws_access_key_id=secrets.aws_access_key_id,
        aws_secret_access_key=secrets.aws_secret_access_key,
    )

    if args['create_instance'] is not None:
        create_instance(client, args['create_instance'])
    if args['report']:
        report(client)
