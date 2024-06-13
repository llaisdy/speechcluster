#! /usr/bin/env python

import argparse
import json
import os
import pathlib

# from .segDiBo import segDiBoDir
from .segFake import fakeLabel_and_write, fakeLabel_and_write_dir
from .segInter import segInter, segInterDir
from .segMerge import segMerge
from .segReplace import segReplace, segReplaceDir
from .segSwitch import segSwitch, segSwitchDir
from .splitAll import splitAll
from .trim import trim, trimDir

OUTFORMAT_CHOICES = (
    'esps',
    'htkgrm',
    'htklab',
    'htkmlf',
    'lab',
    'seg',
    'TextGrid',
)

def report(name, args):
    return f'{name}:\n\n{args}\n'
    
# def sc_dibo(args):
#     return segDiBoDir(args.directory)
#
# def add_dibo_parser(sp):
#     parser = sp.add_parser('dibo', help='Add diphone boundaries')
#     parser.add_argument('-d', '--directory', type=pathlib.Path,
#                         required=True,
#                         help='directory of TextGrids')
#     parser.set_defaults(func=sc_dibo)

def sc_trim(args):
    if args.directory:
        trimDir(args.directory, args.padding)
    else:
        trim(args.fileish, args.padding)

def sc_trim_validation(args):
    if args.directory and args.fileish:
        raise ValueError('-d and file!?')
    if not args.directory and not args.fileish:
        raise ValueError('no -d and no file!?')

def add_trim_parser(sp):
    parser = sp.add_parser('trim', help='Trim beginning and end silence from wav files')
    parser.add_argument('fileish', help='file name or stem', nargs='?')
    parser.add_argument('-d', '--directory', type=pathlib.Path,
                        help='directory of (wav, TextGrid) pairs')
    parser.add_argument('-p', '--padding', type=float, default=0.5,
                        help='padding in seconds')
    parser.set_defaults(func=sc_trim)

def sc_switch(args):
    if args.directory:
        segSwitchDir(args.directory, args.outFormat)
    else:
        infn = args.file.name
        outfn = f'{os.path.splitext(infn)[0]}.{args.outFormat}'
        segSwitch(infn, outfn)

def sc_switch_validation(args):
    sc_fake_validation(args)

def add_switch_parser(sp):
    parser = sp.add_parser('switch', help='Convert between label file formats')
    add_input_group(parser)
    parser.add_argument('-o', '--outFormat', choices=OUTFORMAT_CHOICES,
                        help='output format')
    parser.set_defaults(func=sc_switch)

def sc_splitall(args):
    splitCriteria = {
        'n': args.number,
        'tier': args.tier,
        'label': args.label,
    }
    return splitAll(splitCriteria, args.dir_in, args.dir_out)

def add_splitall_parser(sp):
    parser = sp.add_parser('splitall', help='Split all files in directory')
    parser.add_argument('dir_in', type=pathlib.Path,
                        help='input directory')
    parser.add_argument('dir_out', type=pathlib.Path,
                        help='output directory')
    parser.add_argument('-t', '--tier', required=True,
                        help='tier to split by')
    parser.add_argument('-n', '--number', type=int, required=True,
                        help='number of segments per split')
    parser.add_argument('-l', '--label', required=False,
                        help='label to split by')
    parser.set_defaults(func=sc_splitall)

def sc_replace(args):
    replaceDict = json.load(args.context)['replaceDict']
    if args.directory:
        segReplaceDir(args.directory, replaceDict)
    else:
        fname = args.file.name
        segReplace(fname, replaceDict)

def sc_replace_validation(args):
    sc_fake_validation(args)

def add_replace_parser(sp):
    parser = sp.add_parser('replace', help='Replace selected symbols in a tier')
    add_input_group(parser)
    parser.add_argument('-c', '--context', type=argparse.FileType('r'),
                        required=True,
                        help='json file with replaceDict')
    parser.set_defaults(func=sc_replace)

def sc_merge(args):
    segMerge(args.pairs)

def sc_merge_validation(args):
    pairs = args.pairs
    if not (pairs and not len(pairs) % 2):
        raise ValueError('Must be positive even number of pairs')

def add_merge_parser(sp):
    parser = sp.add_parser('merge', help='Merge tiers')
    parser.add_argument('pairs', help='(file, tier)s to merge', nargs='*')
    parser.set_defaults(func=sc_merge)

def sc_inter(args):
    if args.directory:
        transDict = json.load(args.context)['transDict']
        segInterDir(args.directory, transDict, args.tier)
    else:
        fname = args.file.name
        segInter(fname, args.labels, args.tier)

def sc_inter_validation(args):
    sc_fake_validation(args)

def add_inter_parser(sp):
    parser = sp.add_parser('inter', help='Interpolate labels')
    parser.add_argument('labels', help='labels to add', nargs='*')
    add_input_group(parser)
    parser.add_argument('-c', '--context', type=argparse.FileType('r'),
                        help='json file with transDict')
    parser.add_argument('-t', '--tier', required=True,
                        help='tier to interpolate into')
    parser.set_defaults(func=sc_inter)

def sc_fake(args):
    if args.directory:
        transDict = json.load(args.context)['transDict']
        fakeLabel_and_write_dir(args.directory, transDict, args.outFormat)
    else:
        fname = args.file.name
        fakeLabel_and_write(fname, args.labels, args.outFormat)

def sc_fake_validation(args):
    if args.directory and not args.context:
        raise ValueError('-d but no -c')
    if args.file and not args.labels:
        raise ValueError('-f but no labels')

def add_fake_parser(sp):
    parser = sp.add_parser('fake', help='Fake segmentation')
    add_input_group(parser)
    parser.add_argument('-o', '--outFormat', choices=OUTFORMAT_CHOICES,
                        required=True,
                        help='output format')
    parser.add_argument('labels', help='labels to add', nargs='*')
    parser.add_argument('-c', '--context', type=argparse.FileType('r'),
                              help='json file with transDict')
    parser.set_defaults(func=sc_fake)

def add_input_group(parser):
    group_input = parser.add_mutually_exclusive_group(required=True)
    group_input.add_argument('-d', '--directory', type=pathlib.Path,
                             help='directory for input')
    group_input.add_argument('-f', '--file', type=argparse.FileType('r'),
                             help='input file')

PARSERS_TO_ADD = (
    # (add_dibo_parser, sc_dibo, None),
    (add_fake_parser, sc_fake, sc_fake_validation),
    (add_inter_parser, sc_inter, sc_inter_validation),
    (add_merge_parser, sc_merge, sc_merge_validation),
    (add_replace_parser, sc_replace, sc_replace_validation),
    (add_splitall_parser, sc_splitall, None),
    (add_switch_parser, sc_switch, sc_switch_validation),
    (add_trim_parser, sc_trim, sc_trim_validation),
)

def create_global_parser():
    global_parser = argparse.ArgumentParser(prog='sc')
    global_parser.set_defaults(func=lambda _: global_parser.print_help())
    subparsers = global_parser.add_subparsers(title='subcommands',
                                              help='SpeechCluster operations')
    validation_map = {}
    for (adder, func, validator) in PARSERS_TO_ADD:
        adder(subparsers)
        if validator:
            validation_map[func] = validator
    return global_parser, validation_map

def main():
    gp, validation_map = create_global_parser()
    args = gp.parse_args()
    validation_map.get(args.func, lambda _: None)(args)
    args.func(args)

if __name__ == '__main__':
    main()
