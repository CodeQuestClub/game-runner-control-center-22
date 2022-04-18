import argparse
import boto3
import secrets
from cmd import Cmd
from actions import report, create_instance


class Prompt(Cmd):
    prompt = 'CodeQuest> '
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        print("Bye")
        return True

    def help_exit(self):
        print('exit the application. Shorthand: x q Ctrl-D.')

    def do_report(self, inp):
        report(client)

    def help_report(self):
        print("show task reports and generate leaderboard")

    def do_CI(self, count):
        try:
            create_instance(client, int(count))
        except:
            print("Bad request")

    def help_CI(self):
        print('create <Count> ECS worker instances on AWS')

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

    # create interactive shell
    Prompt().cmdloop()
