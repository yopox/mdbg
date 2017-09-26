"""Little tool to convert everything to cool mdbg documents and vice versa.

Little tool to convert everything (or as anything as we can do)
to cool mdbg documents (or other things).
Written by Hadrien, pierrotdu18, and YoPox
"""
# -*- coding: utf-8 -*-

# WARNING :
# No convert functions should be implemented here.
# This module calls convert modules.

from docopt import docopt

# Convert modules
import mdbg.md2mdbg as md2mdbg
import mdbg.mdbg2tex as mdbg2tex
import mdbg.mdbg2html as mdbg2html

from mdbg.settings import logger


__doc__ = """
main.py

usage: main.py [-h] [--output OUTPUT] [-m | -b] [-T | -M | -H]
                      [--title TITLE] [--date DATE] [--author AUTHOR]
                      [--packages PACKAGES] [--documentclass DOCUMENTCLASS]
                      [--roboto] [--tableofcontents] [--minted MINTED]
                      INPUT

This is mdbg : a little tool to convert everything (or as anything as we can
do) to cool mdbg documents (or other things).

positional arguments:
  input                 File in input.

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file. If not specified, mdbg will wrote it in
                        input.formatwhere input is the name of the input file
                        (whithout its extention mdbg recognises it).

Syntax Options:
  Input options begin with a lowercase, output options begin with an
  uppercase. Default : -b -T

  -m                    Indicate that the input syntax is markdown.
  -b                    Indicate that the input syntax is mdbg.
  -T                    Indicate that the output syntax is LaTeX.
  -M                    Indicate that the output syntax is mdbg.
  -H                    Indicate that the output syntax is HTML.

LaTeX options:
  --title TITLE         Title
  --date DATE           Date
  --author AUTHOR       Author(s)
  --packages PACKAGES   list of additionnal packages with the following syntax
                        {[options1]{package1},[options2]{package2},...} (none
                        by default)
  --documentclass DOCUMENTCLASS
                        class of the document [default: article]
  --roboto              Use robotoMono font.
  --tableofcontents     Display the table of contents. [default: True]
  --minted MINTED       Minted style, if minted is the wanted syntax engine.
                        (default=normal) If pygments is not installed, the
                        option will be ignored. To deactivate this behaviour,
                        call --minted F-STYLE

Written by YoPox, pierrotdu18 and Hadrien Renaud-Lebret. For more information,
see https://github.com/YoPox/mdbg .
"""



def output_treatment(args):
    """Function to analyze the output."""
    if not args['--output']:
        ext = 'tex'
        if args['-H']:
            ext = 'html'
        elif args['-M']:
            ext = 'mdbg'
        if args['INPUT'][-2:] == 'md':
            args['--output'] = args['INPUT'][:-2] + ext
        elif args['INPUT'][-4:] == 'mdbg':
            args['--output'] = args['INPUT'][:-4] + ext
        else:
            args['--output'] = args['INPUT'] + "." + ext
    return args


def minted_treatment(args):
    """Function to analyze the minted option.

    If pygments is not installed, the option is deactivated.
    Otherwise, anything goes on normally.
    """
    if not mdbg2tex.PYGMENTS_AVAILABLE:
        args['--minted'] = False
        logger.error('Hum, --minted ignored, you need Pygments installed, see the help or the doc.')
    return args



# MAIN
def main():
    # arg_parser = argparse_use()
    args = docopt(__doc__) # arg_parser.parse_args()

    logger.info("Input : " + args['INPUT'])

    if args['--minted']:
        args = minted_treatment(args)
    logger.info('minted : {}'.format(bool(args['--minted'])))

    args = output_treatment(args)
    logger.info("Output : " + args['--output'])

    argv = {
        'input': args['INPUT'],
        'output': args['--output'],
        'documentclass': args['--documentclass'],
        'tableofcontents': args['--tableofcontents'],
        'date': args['--date'],
        'author': args['--author'],
        'title': args['--title'],
        'roboto': args['--roboto'],
        'packages': args['--packages'],
        'minted': args['--minted'],
        'print_help': args['--help'],
    }

    if args['-m']:
        argv2 = dict(argv)
        argv2['--output'] = '.tmp.mdbg'
        md2mdbg.convert_file(argv2['INPUT'], argv2['--output'])
        argv['INPUT'] = open(argv2['--output'], 'r')
    else:
        if args['-H']:
            mdbg2html.main(argv)
        else:  # default option : -Tex
            mdbg2tex.main(argv)
        # if args.Mdbg: Cas chelou que je traiterai plus tard.

if __name__ == '__main__':
    main()