# -*- coding: utf-8 -*-
# Little tool to convert everything (or as anything as we can do)
# to cool mdbg documents (or other things).
# Written by Hadrien, pierrotdu18, and YoPox

# WARNING :
# No convert functions should be implemented here.
# This module calls convert modules.

# IMPORTS

# Convert modules
import md2mdbg
import mdbg2tex
import mdbg2html

# Others
import argparse
import re


# ARGPARSE DATA

description = """This is mdbg : a little tool to convert everything
    (or as anything as we can do) to cool mdbg documents (or other things).
"""
epilog = """Written by YoPox, pierrotdu18 and Hadrien Renaud-Lebret.
For more information, see https://github.com/YoPox/mdbg .
"""


def argparse_use():
    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('input', type=argparse.FileType('r'),
                        help="File in input.")

    parser.add_argument(
        '--output', '-o', help="""Output file. If not specified, mdbg will wrote it in input.format where input is the name of the input file (without its extention mdbg recognises it).""")

    formatInOut = parser.add_argument_group(
        title="Syntax options", description="""Input options begin with a lowercase, output options begin with an uppercase.""")
    formatIn = formatInOut.add_mutually_exclusive_group(required=True)
    formatOut = formatInOut.add_mutually_exclusive_group(required=True)

    formatIn.add_argument('-md', action="store_true",
                          help="Indicate that the input Syntax is markdown.")
    formatIn.add_argument('-mdbg', action="store_true",
                          help="Indicate that the input Syntax is mdbg.")

    formatOut.add_argument('-Tex', action="store_true",
                           help="Indicate that the output Syntax is LaTeX.")
    formatOut.add_argument('-Mdbg', action="store_true",
                           help="Indicate that the output Syntax is mdbg.")
    formatOut.add_argument('-Html', action="store_true",
                           help="Indicate that the output Syntax is HTML.")

    latexOptions = parser.add_argument_group(title="LaTeX options")
    latexOptions.add_argument('--title', help="Title of the document.")
    latexOptions.add_argument('--date', help="Date.")
    latexOptions.add_argument('--author', help="Author(s) of the document.")
    latexOptions.add_argument(
        '--packages', help="""List of additionnal packages with the following syntax {[options1]{package1},[options2]{package2},...} (none by default).""")
    latexOptions.add_argument('--documentclass', help='Class of the document.',
                              default='article')
    latexOptions.add_argument('--roboto', help="Use of robotoMono font.",
                              action="store_true")
    latexOptions.add_argument('--tableofcontents', action="store_false",
                              help="Display the table of Contents.", default=True)

    return parser


# MAIN


if __name__ == '__main__':
    args = argparse_use().parse_args()
    inp = args.input.name

    print("Input : ", inp)

    if not args.output:
        ext = 'txt'
        if args.Tex:
            ext = 'tex'
        elif args.Html:
            ext = 'html'
        elif args.Mdbg:
            ext = 'mdbg'
        if inp[-2:] == 'md':
            args.output = inp[:-2] + ext
        elif inp[-4:] == 'mdbg':
            args.output = inp[:-4] + ext
        else:
            args.output = inp + "." + ext

    print("Output : ", args.output)

    argv = {
        'input': args.input,
        'output': args.output,
        'documentclass': args.documentclass,
        'tableofcontents': args.tableofcontents,
        'date': args.date,
        'author': args.author,
        'title': args.title,
        'roboto': args.roboto,
        'packages': args.packages,
    }
    # Useful for debugging
    # print(argv)

    if args.md:
        argv2 = dict(argv)
        argv2['output'] = '.tmp.mdbg'
        md2mdbg.main(argv2)
        argv['input'] = open(argv2['output'], 'r')
        args.mdbg = True

    if args.mdbg:
        if args.Html:
            mdbg2html.main(argv)
        elif args.Tex:
            mdbg2tex.main(argv)
        # if args.Mdbg: Cas chelou que je traiterai plus tard.
