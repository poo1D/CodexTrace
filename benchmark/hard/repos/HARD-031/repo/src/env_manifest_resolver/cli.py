import argparse
import json

from .resolver import resolve_manifest


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--set", dest="sets", action="append", default=[])
    args = parser.parse_args(argv)

    overrides = {}
    for item in args.sets:
        if "=" not in item:
            parser.error("--set must use KEY=VALUE")
        key, value = item.split("=", 1)
        overrides[key] = value

    resolved = resolve_manifest(args.manifest, overrides)
    print(json.dumps(resolved, sort_keys=True))


if __name__ == "__main__":
    main()
