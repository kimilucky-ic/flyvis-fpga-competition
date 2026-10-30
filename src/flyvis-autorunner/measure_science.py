"""Measure one explicit CLI command and retain complete output; no retry."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from autorunner import HERE, own_path, require, utc, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--command", choices=("preflight", "dry-run", "run", "cache-only"), required=True)
    args = parser.parse_args()
    record = own_path("verification", "phase2_" + args.id + "_command.json")
    require(not record.exists() and not own_path("runs", args.id).exists(), "ATTEMPT_EXISTS", "Never repeat an existing command/run")
    command = [sys.executable, "-B", str(HERE / "runner.py"), "preflight" if args.command == "preflight" else "run",
               "--config", str(Path(args.config).resolve()), "--id", args.id]
    if args.command in ("dry-run", "cache-only"):
        command.append("--" + args.command)
    record.parent.mkdir(parents=True, exist_ok=True)
    started_utc = utc()
    started = time.perf_counter()
    with record.with_suffix(".stdout.log").open("w", encoding="utf-8") as out, record.with_suffix(".stderr.log").open("w", encoding="utf-8") as err:
        result = subprocess.run(command, stdout=out, stderr=err)
    value = {"command": command, "started_utc": started_utc, "ended_utc": utc(),
             "CLI_wall_s": time.perf_counter() - started, "exit_code": result.returncode,
             "run_id": args.id, "stdout": str(record.with_suffix(".stdout.log")), "stderr": str(record.with_suffix(".stderr.log"))}
    write_json(record, value)
    print(json.dumps(value, indent=2))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
