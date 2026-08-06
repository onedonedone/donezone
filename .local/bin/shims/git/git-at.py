#!/usr/bin/env python3
import argparse
import datetime
import os
import subprocess
import sys

GIT = "git"

DATE_AUTHOR = "GIT_AUTHOR_DATE"
DATE_COMMIT = "GIT_COMMITTER_DATE"


class Arguments(argparse.Namespace):
    timestamp: str
    remainder: list[str]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("timestamp")
    parser.add_argument("remainder", nargs=argparse.REMAINDER)

    arguments = parser.parse_args(namespace=Arguments())

    now = datetime.datetime.now()

    match len(arguments.timestamp):
        case 12:
            time = datetime.datetime.strptime(arguments.timestamp, r"%Y%m%d%H%M")
        case 10:
            time = datetime.datetime.strptime(arguments.timestamp, r"%y%m%d%H%M")
        case 8:
            time = datetime.datetime.strptime(arguments.timestamp, r"%m%d%H%M").replace(now.year)
        case 6:
            time = datetime.datetime.strptime(arguments.timestamp, r"%m%d%H").replace(now.year)
        case 4:
            time = datetime.datetime.strptime(arguments.timestamp, r"%H%M").replace(now.year, now.month, now.day)
        case 2:
            time = datetime.datetime.strptime(arguments.timestamp, r"%H").replace(now.year, now.month, now.day)
        case _:
            sys.exit("error: invalid timestamp format.")

    time = time.isoformat()

    command = [GIT, *arguments.remainder]

    env = os.environ.copy()
    env.update({DATE_AUTHOR: time})
    env.update({DATE_COMMIT: time})

    sys.exit(subprocess.run(command, env=env).returncode)
