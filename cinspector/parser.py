import argparse
from cinspector.interfaces import CCode


def main():
    parser = argparse.ArgumentParser(description='Print the parsed tree')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", action="store_true")
    group.add_argument("-s", "--string", action="store_true")
    parser.add_argument("target", type=str)
    args = parser.parse_args()

    target = args.target
    content = target
    if args.file:
        with open(target, 'r', errors='ignore') as r:
            content = r.read()

    cc = CCode(content)
    cc.node.print_tree()


if __name__ == '__main__':
    main()
