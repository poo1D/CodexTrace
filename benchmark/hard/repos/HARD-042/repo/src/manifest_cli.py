import argparse
import sys

from snapshot_manifest import write_manifest


def main(argv=None):
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-manifest")
    build.add_argument("root")
    build.add_argument("--output", required=True)
    build.add_argument("--include-empty-dirs", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "build-manifest":
        write_manifest(args.root, args.output, include_empty_dirs=args.include_empty_dirs)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
