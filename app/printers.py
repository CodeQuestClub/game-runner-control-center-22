import json
import secrets
import requests
from collections import defaultdict
import os


def print_aws_tasks(client):
    states = ['STOPPED', 'RUNNING', 'PENDING']
    states_count = defaultdict(int)

    for state in states:
        states_count[state] = len(client.list_tasks(
            cluster='codequest-worker-cluster',
            desiredStatus=state,
            launchType='FARGATE'
        )['taskArns'])

    total_tasks = states_count['PENDING'] + states_count['STOPPED'] + states_count['RUNNING']

    print('-- Total tasks: {} \n'
          '-- Running tasks: {} \n'
          '-- Pending tasks: {} \n'
          '-- Stopped tasks: {}'.format(
                                total_tasks,
                                states_count['RUNNING'],
                                states_count['PENDING'],
                                states_count['STOPPED']))


def get_leaderboard(server_url):
    response = requests.get(server_url).json()
    leaderboard = sorted(response['teams'], key=lambda x: x['score'], reverse=True)

    return leaderboard


def print_matches(server_url):
    response = requests.get(server_url).json()
    matches = response['matches']

    match_count = defaultdict(int)

    for match in matches:
        match_count[match['status']] += 1

    print('-- Done: {} \n'
          '-- In progress: {} \n'
          '-- Queued: {}'.format(match_count['done'], match_count['in_progress'], match_count['queue']))


def print_match_stats(server_url):
    response = requests.get(server_url).json()
    groups = response['groups']
    matches = response['matches']

    for i, group in enumerate(map(sorted, groups)):
        print('Group #{}:'.format(i + 1))
        for match in matches:
            if group == sorted(match['teams']):
                print("Match: team 1: {}, team 2: {}, team 3: {}, team 4: {} --- Status: {} --- results: {}".format(
                    group[0], group[1], group[2], group[3], match['status'], match['results']))


def create_leaderboard_data():
    leaderboard_data = get_leaderboard(server_url=secrets.server_url)
    leaderboard = []
    for rank, team in enumerate(leaderboard_data):
        row = [rank + 1, team['name'], team['score']]
        leaderboard.append(row)

    with open(os.path.abspath(os.getcwd()) + '/app/leaderboard/leaderboard.json', 'w') as leaderboard_json:
        leaderboard_json.write(json.dumps(leaderboard))
