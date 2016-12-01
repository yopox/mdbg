"""Little tool to convert everything to cool mdbg documents and vice versa.

Little tool to convert everything (or as anything as we can do)
to cool mdbg documents (or other things).
Written by Hadrien, pierrotdu18, and YoPox
"""
# -*- coding: utf-8 -*-

# WARNING :
# No convert functions should be implemented here.
# This module calls convert modules.

# IMPORTS


# Others
import argparse

# Convert modules
import md2mdbg
import mdbg2tex
import mdbg2html


# ARGPARSE DATA

description = """This is mdbg : a little tool to convert everything
    (or as anything as we can do) to cool mdbg documents (or other things).
"""
epilog = """Written by YoPox, pierrotdu18 and Hadrien Renaud-Lebret.
For more information, see https://github.com/YoPox/mdbg .
"""


def argparse_use():
    """Function that configure the argument parser used later in the programm execution."""
    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('input', type=argparse.FileType('r'),
                        help="File in input.")

    parser.add_argument(
        '--output', '-o', help="Output file. If not specified, mdbg will wrot it in input.format"
        "where input is the name of the input file (whithout its extention mdbg recognises it).")

    formatInOut = parser.add_argument_group(
        title="Syntax Options",
        description="Input options begin with a lowercase, output options begin with an uppercase. "
        "Default : -mdbg -Tex")

    formatIn = formatInOut.add_mutually_exclusive_group()
    formatOut = formatInOut.add_mutually_exclusive_group()

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
    latexOptions.add_argument('--title', help="Title of the document")
    latexOptions.add_argument('--date', help="Date")
    latexOptions.add_argument('--author', help="Author(s) of the document")
    latexOptions.add_argument(
        '--packages', help="list of additionnal packages with the following syntax "
        "{[options1]{package1},[options2]{package2},...} (none by default)")
    latexOptions.add_argument('--documentclass', help='class of the document',
                              default='article')
    latexOptions.add_argument('--roboto', help="Use robotoMono font.",
                              action="store_true")
    latexOptions.add_argument('--tableofcontents', action="store_false",
                              help="Display the table of Contents. (default=True)", default=True)
    latexOptions.add_argument(
        '--minted', default=False,
        help="Minted style, if minted is the wanted syntax engine. (default=normal) "
        "If pygments are not installed, the option will be ignored. To deactivate this behaviour, "
        "call --minted F-STYLE"
    )

    return parser


def output_treatment(args):
    """Function to analyse the output."""
    if not args.output:
        ext = 'tex'
        if args.Html:
            ext = 'html'
        elif args.Mdbg:
            ext = 'mdbg'
        if args.input.name[-2:] == 'md':
            args.output = args.input.name[:-2] + ext
        elif args.input.name[-4:] == 'mdbg':
            args.output = args.input.name[:-4] + ext
        else:
            args.output = args.input.name + "." + ext
    return args


def minted_treatment(args):
    """Function to analyse the minted option.

    If pygments are not installed, the option is diactivated.
    Otherwise, anything goes on normally.
    """
    if not mdbg2tex.PYGMENTS_AVAILABLE:
        args.minted = False
        print('Hum, --minted ignored, you need Pygments installed, see the help or the doc.')
    return args


# MAIN
if __name__ == '__main__':
    arg_parser = argparse_use()
    args = arg_parser.parse_args()

    print("Input : ", args.input.name)

    args = output_treatment(args)
    print("Output : ", args.output)

    if args.minted:
        args = minted_treatment(args)
    # print('minted : ', args.minted)

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
        'minted': args.minted,
        'print_help': arg_parser.print_help,
        'print_usage': arg_parser.print_usage,
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
        else:  # default option : -Tex
            mdbg2tex.main(argv)
        # if args.Mdbg: Cas chelou que je traiterai plus tard.
