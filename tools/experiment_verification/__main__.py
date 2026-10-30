import argparse
from pathlib import Path
from .core import load_json, verify, write_report
from .records import validate_project, resume_report


def main():
    parser = argparse.ArgumentParser(description="Local research verification and continuity")
    sub = parser.add_subparsers(dest="command", required=True)
    v = sub.add_parser("verify")
    v.add_argument("spec", type=Path); v.add_argument("run", type=Path)
    v.add_argument("--root", required=True, type=Path); v.add_argument("--output", required=True, type=Path)
    r = sub.add_parser("resume"); r.add_argument("root", type=Path); r.add_argument("--output", required=True, type=Path)
    c = sub.add_parser("records"); c.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "verify":
            report = verify(load_json(args.spec), load_json(args.run), args.root, args.spec)
            write_report(args.output, report)
            print(report["status"])
            return 0 if report["status"] == "verified" else 1
        if args.command == "records":
            _, errors = validate_project(args.root)
            print("\n".join(errors) if errors else "Records valid")
            return int(bool(errors))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(resume_report(args.root))
        print(args.output)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Invalid/unreadable input: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
