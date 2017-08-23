import argparse
from nplusone.parser import Parser, FREQUENCY_LIMIT_MAX

VERSION='1.0.0'

def parse(args):
    parser = Parser()
    parser.parse(args.input, args.output, args.column, args.increment, args.limit, args.known)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.set_defaults(func=parse)

    arg_parser.add_argument('-v', '--version', action='version', version='NPlusOne Japanese Sentence Miner v' + VERSION)
    arg_parser.add_argument('-c', '--column', type=int, default=1, help='Column of sentence in input TSV. Default=1')
    arg_parser.add_argument('-i', '--increment', type=int, default=100, help='Increments to scan frequency of vocabulary. Default=100')
    arg_parser.add_argument('-l', '--limit', type=int, default=None, help='Maximum frequency index of vocabulary to allow. Default=None, Maximum={}'.format(FREQUENCY_LIMIT_MAX))
    arg_parser.add_argument('-k', '--known', default=None, help='Text file of known vocabulary, one word per line.')
    arg_parser.add_argument('input', help='Path of TSV file to read')
    arg_parser.add_argument('output', help='Path of TSV file to write')

    args = arg_parser.parse_args()
    args.func(args)  # call the default function