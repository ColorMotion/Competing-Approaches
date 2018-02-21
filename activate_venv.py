#!/usr/bin/env python3
import argparse
import os
from pathlib import Path
import sys
import subprocess
import venv


def parse_environment(environment):
    '''Build a dictionary from the env command output.'''
    key_values = [x.partition('=') for x in environment.splitlines()]
    return {key: value for key, _, value in key_values if key}


def bash_env(filename):
    '''Run source && env in bash and return its output.'''
    return parse_environment(subprocess.check_output([
        'bash', '-c', 'source {} && env'.format(filename)
    ], universal_newlines=True))


def bash_source(filename):
    '''Update the current process' environment with bash's source command.'''
    os.environ.update(bash_env(filename))


def main(args):
    if not Path('setup.py').exists():
        raise RuntimeError('setup.py not found; run this script in a directory with a Python package source')
    venv.create('venv', system_site_packages=True, with_pip=True)
    bash_source('venv/bin/activate')

    requirements = Path('requirements.txt')
    if requirements.exists():
        subprocess.check_call(['pip', 'install', '-r', requirements])
    else:
        print('No requirements.txt file found, installing latest versions')
    subprocess.check_call(['pip', 'install', '-e', '.'])

    os.execvp(args.command[0], args.command)


def parse_args():
    parser = argparse.ArgumentParser(description='Activates a venv for the project.')
    parser.add_argument('command', nargs='*', default=['/bin/sh'],
                        help='command to execute in the venv, with optional arguments')
    return parser.parse_args()


if __name__ == '__main__':
    assert sys.version_info.major == 3 and sys.version_info.minor >= 6, 'Use python3 >= 3.6'
    main(parse_args())
