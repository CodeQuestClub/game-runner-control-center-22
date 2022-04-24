import argparse
import boto3
import secrets
from cmd import Cmd
from actions import general_report, create_task_instance, download_replay, delete_all_replays, get_team_matches
import os
import shutil
import glob
import requests
import random
import time


class Prompt(Cmd):
    prompt = 'CodeQuest> '
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        print("Bye")
        return True

    def help_exit(self):
        print('exit the application. Shorthand: x q Ctrl-D.')

    def do_report(self, inp):
        general_report()

    def help_report(self):
        print("show task reports and generate leaderboard")

    def do_get_team_matches(self, team):
        get_team_matches(team)

    def help_get_team_matches(self):
        print("Get all match indices for the team in input")

    def do_unzip_submissions(self, inp):
        if os.path.isdir('bots'):
            shutil.rmtree('bots')
        os.makedirs('bots')
        zips = glob.glob('submissions/*.zip')
        for submission in zips:
            file_name = submission[len('submissions/'):]
            team_name = file_name.split('.')[0]
            os.makedirs(f'bots/{team_name}')
            shutil.unpack_archive(submission, f'bots/{team_name}')
    
    def help_unzip_submissions(self):
        print("Unzip")

    def do_CI(self, count):
        try:
            create_task_instance(int(count))
        except:
            print("Bad request")

    def help_CI(self):
        print('create <Count> ECS worker instances on AWS')

    def do_get_replays(self, inp=None):
        if inp is not None and inp.strip() != '':
            print("Hereeee")
            print(inp)
            download_replay(f'match_{inp}')
            return
        response = requests.get(secrets.server_url).json()
        print("CHANGE WIFI")
        time.sleep(20)
        team_selected = dict()
        for team in response['teams']:
            team = team['name']
            with open(f'mappings/{team}.txt', 'r') as f:
                selected_replays = random.sample(list(f.readlines()), 10)
                selected_replays = list(map(lambda x: x.strip(), selected_replays))
            with open(f'mappings_selected/{team}.txt', 'w') as f:
                f.write('\n'.join(selected_replays))
            team_selected[team] = selected_replays
        print("Here")
        for selected_list in team_selected.values():
            for game in selected_list:
                try:
                    game = game.strip()
                    download_replay(f'match_{game}')
                except Exception as e:
                    print(f'Match {game} could not download')

    def help_get_replays(self):
        print('download all replay files')

    def do_DAR(self, inp):
        delete_all_replays()

    def help_DAR(self):
        print('delete all replays in the codequest_replay bucket')

    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)

        print("Default: {}".format(inp))

    do_EOF = do_exit
    help_EOF = help_exit


if __name__ == '__main__':
    # for running program from command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-ci', '--create-instance', help='Create AWS ECS instance', type=int)
    parser.add_argument('-r', '--report', help='Show report of AWS instances', action='store_true')
    args = vars(parser.parse_args())

    if args['create_instance'] is not None:
        create_task_instance(args['create_instance'])
    if args['report']:
        general_report()

    # create interactive shell
    Prompt().cmdloop()
