class CliArgError(ValueError):
    pass


def parse_args(argv):
    result = {"limit": 10, "verbose": False}
    index = 0
    while index < len(argv):
        item = argv[index]
        if item == "--verbose":
            result["verbose"] = True
            index += 1
        elif item == "--limit":
            result["limit"] = int(argv[index + 1])
            index += 2
        else:
            index += 1
    return result
