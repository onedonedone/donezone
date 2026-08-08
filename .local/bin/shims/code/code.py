#!/usr/bin/env python3
import argparse
import os
import pathlib
import subprocess


def _mtime(path: pathlib.Path) -> float:
    return path.stat().st_mtime


if __name__ == "__main__":
    _, arguments = argparse.ArgumentParser(add_help=False).parse_known_args()

    outputs = subprocess.check_output(["ss", "--listening", "--no-header", "--processes", "--unix"])

    sockets: dict[pathlib.Path, str] = {}

    for line in outputs.splitlines():
        if b"/vscode-ipc-" not in line:
            continue

        _, found, rest = line.partition(b"pid=")

        if not found:
            continue

        address = next(field for field in line.split() if b"/vscode-ipc-" in field)

        pid = int(rest.split(b",")[0])

        command = str(pathlib.Path(f"/proc/{pid}/exe").readlink().parent / "bin/remote-cli/code")

        if os.access(command, os.X_OK):
            sockets[pathlib.Path(os.fsdecode(address))] = command

    if not sockets:
        raise SystemExit("fatal: no code socket found")

    socket = pathlib.Path(os.environ.get("VSCODE_IPC_HOOK_CLI", "/"))
    socket = socket if socket in sockets else max(sockets, key=_mtime)

    command = sockets[socket]

    os.environ["VSCODE_IPC_HOOK_CLI"] = str(socket)

    os.execve(command, [command, *arguments], env=os.environ)
