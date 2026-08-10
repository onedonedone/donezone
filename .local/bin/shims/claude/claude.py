#!/usr/bin/env python3
import argparse
import json
import os
import subprocess

LINESEP = "\n"

CLAUDE = "claude"
FOLDER = ".config/claude"

SETTINGS_FALLBACK = "settings.fallback.json"
SETTINGS_IRONCLAD = "settings.ironclad.json"
SETTINGS_TAILORED = "settings.json"

COUNTRY = "SG"
EFFORT = "max"
TIMEZONE = "Asia/Singapore"
TRACE = "https://www.cloudflare.com/cdn-cgi/trace"


def _merge(base: dict, override: dict) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge(base[key], value)
            continue

        if key in base and isinstance(base[key], list) and isinstance(value, list):
            base[key] = [*base[key], *[item for item in value if item not in base[key]]]
            continue

        base[key] = value


if __name__ == "__main__":
    _, arguments = argparse.ArgumentParser(add_help=False).parse_known_args()

    options = arguments[: arguments.index("--")] if "--" in arguments else arguments

    adjusted = any(option == "--effort" or option.startswith("--effort=") for option in options)
    headless = any(option == "--print" or option == "-p" for option in options)

    if not adjusted and not headless:
        arguments[:0] = ["--effort", EFFORT]

    try:
        trace = subprocess.run(
            ["curl", "--fail", "--max-time", "5", "--show-error", "--silent", TRACE],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
        )
    except FileNotFoundError:
        raise SystemExit("fatal: no command curl found")

    if trace.returncode:
        raise SystemExit(f"fatal: {trace.stderr.decode().strip()}")

    country = None

    for line in trace.stdout.decode().splitlines():
        key, _, value = line.partition("=")

        if key == "loc":
            country = value
            break

    if not country:
        raise SystemExit("fatal: no country code found")

    if country != COUNTRY:
        raise SystemExit(f"fatal: country code {country} is not {COUNTRY}")

    command = None

    for directory in os.get_exec_path():
        candidate = os.path.join(directory, CLAUDE)

        if os.path.realpath(candidate) == os.path.realpath(__file__):
            continue

        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            command = candidate
            break

    if not command:
        raise SystemExit("fatal: no command claude found")

    zone = os.environ.get("ZONE")

    if zone:
        folder = os.path.join(zone, FOLDER)

        merged: dict = {}

        for name in [SETTINGS_FALLBACK, SETTINGS_TAILORED, SETTINGS_IRONCLAD]:
            path = os.path.join(folder, name)

            if os.path.isfile(path):
                with open(path) as file:
                    _merge(merged, json.load(file))

        with open(os.path.join(folder, SETTINGS_TAILORED), "w") as file:
            json.dump(merged, file, ensure_ascii=False, indent=4, sort_keys=True)
            file.write(LINESEP)

        os.environ["CLAUDE_CONFIG_DIR"] = folder

    os.environ["TZ"] = TIMEZONE

    os.execve(command, [command, *arguments], env=os.environ)
