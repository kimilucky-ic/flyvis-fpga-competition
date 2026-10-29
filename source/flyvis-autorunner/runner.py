#!/usr/bin/env python3
"""Bounded camera609 orchestration. Never implements neural equations."""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
from autorunner import Engine, RunnerError, audit, load_json, own_path


def main():
    parser = argparse.ArgumentParser(prog="runner")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("preflight", "run"):
        p = sub.add_parser(command)
        p.add_argument("--config", required=True)
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--cache-only", action="store_true")
        p.add_argument("--mode", choices=("fast", "dev", "formal"))
        p.add_argument("--id")
    p = sub.add_parser("status")
    p.add_argument("id")
    p = sub.add_parser("audit")
    p.add_argument("--run", required=True)
    args = parser.parse_args()
    try:
        if args.command == "status":
            result = load_json(own_path("runs", args.id) / "job.json")
        elif args.command == "audit":
            job = own_path("runs", args.run)
            if (job / "plugin_seal.json").exists():
                from plugin_runner import audit_plugin
                result = audit_plugin(job)
            else:
                result = audit(job)
        else:
            if load_json(args.config).get("schema") == "flyvis-autorunner/cli-science-v2":
                from plugin_runner import PluginEngine
                engine = PluginEngine(Path(args.config), args.mode)
            else:
                engine = Engine(Path(args.config), args.mode)
            result = engine.execute(preflight=args.command == "preflight",
                                    dry_run=args.dry_run, cache_only=args.cache_only,
                                    run_id=args.id)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except RunnerError as exc:
        print(json.dumps({"status": "FAILED", "code": exc.code,
                          "message": str(exc), "run_id": exc.run_id}, ensure_ascii=False))
        return 2
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "FAILED", "code": "INPUT_OR_JOB_ERROR",
                          "message": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
