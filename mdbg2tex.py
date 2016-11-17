# -*- coding: utf-8 -*-
# Little tool to convert Markdown to cool LaTeX documents.
# Written by YoPox, Hadrien and pierrotdu18

# Import
import re
import sys

# Documentation
doc = """
mdbg2tex help
Full version

Usage :
    main.py <input> <options> (normal use of the function, provides a fresh .tex document)
    main.py --help (to get this text exactly)

Options :
    -o : shortcut for --output
    --ouput <output> : output file name (same as input file name by default)

    -d : shortcut for --date
    --date <date> : date of the document (none by default)

    -a : shortcut for --author
    --author <author> : author of the document (none by default)

    -t : shortcut for --title
    --title <title> : title of the document (none by default)

    -c : shortcut for --documentclass
    --documentclass <class> : document class (article by default)

    -p : shortcut for --packages
    --packages <pcks> : list of additionnal packages with syntax
                        {[options1]{package1},[options2]{package2},...}
                        (none by default)

    -T : shortcut for --tableofcontents
    --tableofcontents : if a table of contents is needed ('on' by default)

    -r : shortcut for --robot option
    --robot : put this option if you want to use RobotMono font for your code
    
Go to https://github.com/YoPox/mdConvert/ for more information
"""

# Managing arguments
global ARGV

ARGV = {
    'output': '',
    'input': '',
    'documentclass': 'report',
    'tableofcontents': True,
    'help': False,
    'robot': False
}

def arg_treatment():
    global ARGV

    # Input
    if len(sys.argv) > 1:
        ARGV['input'] = sys.argv[1]

    # List of possible options
    options_with_args = {
        '-o': 'output',
        '--ouput': 'output',
        '-d': 'date',
        '--date': 'date',
        '-a': 'author',
        '--author': 'author',
        '-t': 'title',
        '--title': 'title',
        '-c': 'documentclass',
        '--documentclass': 'documentclass',
        '-p': 'packages',
        '--packages': 'packages'
    }
    bool_options = {
        '-h': 'help',
        '--help': 'help',
        '-T': 'tableofcontents',
        '--tableofcontents': 'tableofcontents',
        '--robot': 'robot',
        '-r': 'robot'
    }

    # Options treatment
    for i in range(2, len(sys.argv)):
        if sys.argv[i] in options_with_args and i + 1 < len(sys.argv):
            ARGV[options_with_args[sys.argv[i]]] = sys.argv[i + 1]
        elif sys.argv[i] in bool_options:
            ARGV[bool_options[sys.argv[i]]] = True

    if ARGV['output'] == '':
        ARGV['output'] = re.sub(
            r"(?P<name>(?:(?!(?:\.[^\.]+$)).)*)(\.[^\.]+$)?", r"\g<name>.tex", ARGV['input'])

# Parsing functions

# Block parsing

def block_code_parse(matchObj): # to parse blocks of code
    # Option syntax : "java" if wanted language is java, and "nb-java" if
    # wanted language is java AND non breaking is wanted
    code = matchObj.group('code')
    __option = matchObj.group('option')
    option = re.sub(r"nb\-(?P<option>.*)", r"\g<option>", __option) # we remove 'nb-' if it's in the option
    non_breaking = __option != option # if those two are different, that's because non breaking is wanted
    out = ''
    if non_breaking:
        # Putting the code in a minipage will prevent from page breaking
        out += "\\begin{minipage}{\\linewidth}\n"
    if option != '':
        if option.lower() == 'ocaml':
            # Because lstlisting doesn't know oCaml (and we love oCaml don't we ?)
            option = 'Caml'
        out += r"\lstset{language=" + option + "}\n"
    out += "\\begin{lstlisting}\n"
    out += code # the code is not modified
    out += "\n\\end{lstlisting}"
    if non_breaking:
        out += "\\begin{minipage}{\\linewidth}\n"
    return out

def tree_parse(matchObj):
    if "nTREE" in matchObj.group(0):
        return ntree_parse(matchObj)       # to parsed multiple trees
    else:
        return binary_tree_parse(matchObj) # to parse binary trees

def binary_tree_parse(matchObj):
    # Only possible option :
    #   - c : center
    option = matchObj.group('option')
    nodes = [list(x) for x in re.findall(r'([A-Z]) "([^"]*?)"', matchObj.group('tree'))] # nodes contains every couple like 'L 42' (see readme.md for the syntax)
    l = len(nodes)
    out = "\n\\begin{center}" if option == 'c' else ""
    out += "\n\\begin{tikzpicture}[nodes={circle, draw}]\n\\graph[binary tree layout, fresh nodes]{\n"
    # The package used to draw trees is TikZ and that requiers LuaLaTeX to compile (the algorithm aiming at computing distance
    # between elements of the graphs is written in Lua)
    # The traversal is a pre-order traversal
    # If you don't understand that code you should go to math spé in Lycée
    # Henri IV and ask E. T.
    def get_tree():
        def aux(i, depth):
            if nodes[i][0] == 'F':
                f = nodes[i][1]
                return ('"' + (block_parse(f) if f != '()' else '') + '"', i + 1)
            else:
                (g, r1) = aux(i + 1, depth + 1)
                (d, r2) = aux(r1, depth + 1)
                return ('"' + block_parse(nodes[i][1]) + '"' + " -- {" + g + "," + d + "}", r2)
        (ans, r) = aux(0, 1)
        if r != l:
            return ""
        else:
            return re.sub(r"\n ?\n", r"\n", ans) + "};\n"

    out += get_tree() + "\\end{tikzpicture}\n" + ("\\end{center}\n" if option == 'c' else "")
    return out

def ntree_parse(matchObj):
    # Possible options :
    #   - c : center
    # /!\ if you want to use bold or italic etc. in a nTREE you must type it in LaTeX, not in MarkdownBG
    option = matchObj.group('option')
    tree = matchObj.group('tree')
    out = "\n\\begin{center}" if option == 'c' else ""
    out += "\n\\begin{tikzpicture}[nodes={circle, draw}]\n\\graph[binary tree layout, fresh nodes]{\n"
    out += tree + "};\n\\end{tikzpicture}\n" + ("\\end{center}\n" if option == 'c' else "") # the syntax we use is the syntax used by the sub package 'graph' of TikZ
    return out

def graph_parse(matchObj):
    # We use TikZ 'graph drawing' and 'graphs' libraries, see pgfmanual for more information
    option = matchObj.group('option')
    option = option if option != None else ''
    graph = matchObj.group('graph')
    out = "\\begin{tikzpicture}\n[nodes={text height=.7em, text depth=.2em, draw=black!20, thick, fill=white, font=\\footnotesize},>=stealth, rounded corners, semithick]\n\\graph [level distance=1cm, sibling sep=.5em, sibling distance=1cm,"
    out += option + "]\n" + '{' + graph + '};\n\\end{tikzpicture}\n'
    return out

def quote_parse(matchObj):
    quotes = matchObj.group('quote')
    quotes = [x for x in re.split(r"(?:^|\n)> (.*)", quotes) if x!= '' and x!= '\n']
    out = "\n\\medskip\n\\begin{displayquote}\n" # we use 'csquote' package
    for quote in quotes:
        out += block_parse(quote) + r"\\" # we parse recursively the content of the quotation
    return out[0:-2] + "\n\\end{displayquote}\n\\medskip\n" # we remove the extra '\\'

def itemize_parse(matchObj):
    itemize = matchObj.group(0)
    itemize = re.sub(r"(?:^|(?<=\n))(?:    |\t)(?P<item>.*)", r"\g<item>", itemize) # we remove left indentation
    items = re.split(r"(?:^|(?<=\n))- ((?:.|\n(?!- ))*)", itemize) # we split items and remove '-' symbol from each item
    items = [x for x in items if x!= '' and x != '\n'] # we keep only non empty items (who cares about empty items?)
    out = "\\begin{itemize}\n"
    for item in items:
        out += "\t\\item " + re.sub(r"\n(?P<line>.*)", r"\n\t\g<line>", block_parse(item)) + '\n' # we parse the item recursively and indent the LaTeX code
    out += "\\end{itemize}\n"
    return out

def enumerate_parse(matchObj):
    enum = matchObj.group(0)
    enum = re.sub(r"(?:^|(?<=\n))(?:    |\t)(?P<item>.*)", r"\g<item>", enum) # we remove left indentation
    items = re.split(r"(?:^|(?<=\n))[0-9]+\. ((?:.|\n(?![0-9]+\. ))*)", enum) # we split items and remove things like '2.' from each item
    items = [x for x in items if x!= '' and x != '\n'] # we keep only non empty items (who cares about empty items?)
    out = "\\begin{enumerate}\n"
    for item in items:
        out += "\t\\item " + re.sub(r"\n(?P<line>.*)", r"\n\t\g<line>", block_parse(item)) + '\n' # we parse the item recursively and indent the LaTeX code
    out += "\\end{enumerate}\n"
    return out

def table_parse(matchObj):
    option = matchObj.group('option')
    table = matchObj.group('table')

    n = len(re.findall(r"(?<=\|)([^\|]*)(?=\|)", re.findall("^.*", table)[0])) # number of rows

    out = '\\begin{center}\n\\begin{tabular}'

    if option != None: # we treat the option
        if len(option) == 1: # if it is only a 'c' for example we center each cell of the table
            out += '{' + ('|' + option) * n + '|}'
        else: # else, we have the data of every row text alignement (if the user knows the syntax)
            options = option.split()
            out += '{'
            for op in options:
                out += '|' + option
            out += '|}'
    else:
        out += '{' + ('|' + 'l') * n + '|}' # if we have no option we chose a left text alignement by default

    out += '\n'

    for line in [line for line in re.findall(r"(?:^|(?<=\n)).*", table) if line != '' and line != '\n']: # for each line of the table
        out += "\\hline\n" # we draw a line
        for element in [x for x in re.findall(r"(?<=\|)([^\|]*)(?=\|)", line) if x != '' and x != '\n']: # for each element in this line
            element = re.sub(r"(?:\s*)(?P<inside>\S.*\S)(?:\s*)", r"\g<inside>", element) # we keep only the element itself (no spaces on its sides)
            out += block_parse(element) + '&' # we parse it as a block (we can't parse it as a line if it is an itemize for example)
        out = out[0:-1] + '\\\\\n'
    out = out[0:-3] + '\\\\\n\\hline\n\\end{tabular}\n\\end{center}\n'

    return out

def title_parse(matchObj):
    titles = {
    'article' : [r"\part", r"\section", r"\subsection", r"\subsubsection", r"\paragraph", r"\subparagraph", r'\subsubparagraph'],
    'report' :  [r"\part", r"\chapter", r"\section", r"\subsection", r"\subsubsection", r"\paragraph", r"\subparagraph", r'\subsubparagraph']
    }
    level = len(matchObj.group('level')) - 1
    star = matchObj.group('star') is not None # if this is a 'stared' section (see readme.md)
    title = matchObj.group('title') # title
    paragraph = matchObj.group('paragraph') # contents of the section
    out = ''
    out += titles[ARGV['documentclass']][level]
    if star:
        out += '*'
    out += '{' + inline_parse(title) + '}' + '\n'
    out += block_parse(paragraph)
    return out

def block_parse(block): # main parsing function
    if re.sub(r'\n', '', block) == '': # if the block isn't very interresting we return it directly
        return block
    out = ''

    # A block can be several blocks itself
    # Blocks can be :
    #   - a paragraph
    #   - block code
    #   - itemize/enumerate
    #   - block quote
    #   - a table
    #   - a latex \[ \]
    #   - a tree or a ntree
    #   - a comment
    #   - something between two of the blocks above
    # 'block' is going to be splitted into sub-blocks that will be treated recursively
    # A block is some kind of node in a tree
    # A leaf is a piece of inline text or an block "elementary brick"

    keys = ['code', 'comment', 'latex', 'title', 'itemize', 'enumerate', 'table', 'quotation', 'tree', 'graph']

    detection_regex = { # these regexps are to detect the blocks and to split them correctly
        'code':        r"(```[^\n]*\n(?:(?!```)(?:.|\n))*\n```)",
        'comment':     r"(<!\-\-(?:(?!\-\->)(?:.|\n))*\-\->)",
        'latex':       r"(\\\[(?:.|\n)*?\\\])",
        'title':       r"((?:^|(?<=\n))#+\*? [^\n]*(?:(?!\n#+ )(?:.|\n))*)",
        'itemize':     r"((?:(?:^|(?<=\n))(?:    |\t)- (?:.|\n(?!\n))*)+)",
        'enumerate':   r"((?:(?:^|(?<=\n))(?:    |\t)[0-9]+\. (?:.|\n(?!\n))*)+)",
        'table':       r"((?:!!.*\n)?(?:\|(?:.*?|)+\n)+)",
        'quotation':   r"((?:^|(?<=\n))(?:> .*\n?)+)",
        'tree' :       r"(!\[(?:[a-z]-)?n?TREE (?:(?!\]!)(?:.|\n))*\]!)",
        'graph':       r"((?:!!.*\n)?!\[GRAPH (?:(?!\]!)(?:.|\n))*\]!)"
    }

    parse_regex = { # those regexps and those which follow are to parse the blocks correctly
        'code':        r"```(?P<option>[^\n]*)\n(?P<code>(?:(?!```)(?:.|\n))*)\n```",
        'comment':     r"<!\-\-(?P<comment>(?:(?!\-\->)(?:.|\n))*)\-\->",
        'latex':       r"(?P<everything>.*)",
        'title':       r"(?:^|(?<=\n))(?P<level>#+)(?P<star>\*)? (?P<title>[^\n]*)(?P<paragraph>(?:(?!\n#+ )(?:.|\n))*)",
        'itemize':     r"(?:.|\n)*",
        'enumerate':   r"(?:.|\n)*",
        'table':       r"(?:!!tab (?P<option>.*?)\n)?(?P<table>(?:\|(?:.*?\|)+\n)+)",
        'quotation':   r"(?:^|(?<=\n))(?P<quote>(?:[>] .*\n?)+)",
        'tree' :       r"!\[(?:(?P<option>[a-z])-)?n?TREE (?P<tree>(?:(?!\]!)(?:.|\n))*)\]!",
        'graph' :      r"(?:!!(?P<option>.*)\n)?!\[GRAPH (?P<graph>(?:(?!\]!)(?:.|\n))*)\]!"
    }

    parse_repl = {
        'code':        block_code_parse,
        'comment':     "% \g<comment>",
        'latex':       "\g<everything>",
        'title':       title_parse,
        'itemize':     itemize_parse,
        'enumerate':   enumerate_parse,
        'table':       table_parse,
        'quotation':   quote_parse,
        'tree' :       tree_parse,
        'graph':       graph_parse
    }

    n = len(block)
    
    # matches is going to contain couples (i, j) where i is a key in keys and j is the position of the first key-element in the block
    # if there is no key-element in the block the position is set to n + 1 where n is the length of the block
    matches = {}
    for key in keys:
        match = re.search(detection_regex[key], block)
        if match == None:
            matches[key] = n + 1
        else:
            matches[key] = match.start()

    # we take the key the element of which is the first in the block
    key = min(keys, key = lambda x: matches[x])

    # if there is code/latex we have to chose it before other blocks (and code before latex)
    if matches['latex'] != n + 1:
        key = 'latex'
    if matches['code'] != n + 1:
        key = 'code'

    # block is going to be splitted into the first key-element and the rest of the string
    if matches[key] != n + 1: # if this element is indeed existing
        sub_blocks = re.split(detection_regex[key],block)
        if sub_blocks != ['', block, '']:
            for sub_block in sub_blocks:
                out += block_parse(sub_block)
            return out
        return re.sub(parse_regex[key], parse_repl[key], block)
    
    # If we arrive to this point, this means block is not a block; it is just an inline part so we just have to
    return inline_parse(block)

# Inline parsing

def inline_parse(line):
    if re.sub(r'\n', '', line) == '':
        return line

    out = ''

    keys = {
    # things which take only one argument
        1: ['code', 'latex', 'quote1', 'quote2', 'footnote', 'superscript', 'subscript', 'bold', 'underline', 'italic', 'strike'],
    # things which take two arguments
        2: ['color', 'link1', 'link2']
    }

    detection_regex = {
        1 : {
                'code':        r"(`[^`\n]*?`)",
                'latex':       r"(\$[^$]*\$)",
                'quote1':      r"((?:^|(?<=\W))\"(?! )(?:(?:(?!(?<=\W)\"|\"(?=\W)).)*?)\"(?=\W|$))",
                'quote2':      r"((?:^|(?<=\W))'(?! )(?:(?:(?!(?<=\W)'|'(?=\W)).)*?)'(?=\W|$))",
                'footnote':    r"(\*\*\*\{[^\n\{\}]*\})",
                'superscript': r"(\^\{[^\n\{\}]*\})",
                'subscript':   r"(_\{[^\n\{\}]*\})",
                'bold':        r"(\*(?! )[^\*]*\*)",
                'underline':   r"(_(?! )[^_]*_)",
                'italic':      r"(%(?! )[^%]*%)",
                'strike':      r"(~(?! )[^~]*~)"
            },
        2:  {
                'color':       r"(\{[^\n\{\}]*\}\[[^\n\{\}]*\])",
                'link1':       r"(\<https?://[^ ]*\>)",
                'link2':       r"(\[.*\]\([^ ]*(?: \".*\")?\))"
            }
    }

    parse_regex = {
        1:  {
                'code':        r"`(?P<inside>[^`\n]*)`",
                'latex':       r"\$(?P<inside>[^\$]*)\$",
                'quote1':      r"(?:^|(?<=\W))\"(?! )(?P<inside>(?:(?!(?<=\W)\"|\"(?=\W)).)*?)\"(?=\W|$)",
                'quote2':      r"(?:^|(?<=\W))'(?! )(?P<inside>(?:(?!(?<=\W)'|'(?=\W)).)*?)'(?=\W|$)",
                'footnote':    r"\*\*\*\{(?P<inside>[^\n\{\}]*)\}",
                'superscript': r"\^\{(?P<inside>[^\n\{\}]*)\}",
                'subscript':   r"_\{(?P<inside>[^\n\{\}]*)\}",
                'bold':        r"\*(?! )(?P<inside>[^\*]*)\*",
                'underline':   r"_(?! )(?P<inside>[^_]*)_",
                'italic':      r"%(?! )(?P<inside>[^%]*)%",
                'strike':      r"~(?! )(?P<inside>[^~]*)~"
            },
        2:  {
                'color':       r"\{(?P<left>[^\n\{\}]*)\}\[(?P<right>[^\n\{\}]*)\]",
                'link1':       r"\<(?P<left>(?P<right>https?://[^ ]*))\>",
                'link2':       r"\[(?P<left>.*)\]\((?P<right>[^ ]*)( \".*\")?\)"
            }
    }

    parse_borders = {
        1:  {
                'code':        (r'\verb`',            '`'),
                'latex':       ('$',                  '$'),
                'quote1':      (r'\say{',             '}'),
                'quote2':      (r'\say{',             '}'),
                'footnote':    (r'\footnote{',        '}'),
                'superscript': (r'\textsuperscript{', '}'),
                'subscript':   (r'\textsubscript{',   '}'),
                'bold':        (r'\textbf{',          '}'),
                'underline':   (r'\ul{',              '}'),
                'italic':      (r'\textit{',          '}'),
                'strike':      (r'\st{',              '}')
            },
        2:  {
                'color':       (r'\color{',   '}{',   '}'),
                'link1':       (r'\href{',    '}{',   '}'),
                'link2':       (r'\href{',    '}{',   '}')
            }
    }

    n = len(line)
    matches = {1: {}, 2: {}}
    for i in (1, 2):
        for key in keys[i]:
            match = re.search(detection_regex[i][key], line)
            if match == None:
                matches[i][key] = n + 1
            else:
                matches[i][key] = match.start()

    key = min([(i, keys[i][j]) for i in (1, 2) for j in range(len(keys[i]))], key = lambda x: matches[x[0]][x[1]])

    # Same as in block_parse
    if matches[1]['latex'] != n + 1:
        key = (1, 'latex')
    if matches[1]['code'] != n + 1:
        key = (1, 'code')
    
    if matches[key[0]][key[1]] != n + 1:
        sub_lines = re.split(detection_regex[key[0]][key[1]], line)
        if sub_lines != ['', line, '']:
            for sub_line in sub_lines:
                out += inline_parse(sub_line)
            return out
        if key[0] == 1:
            inside = re.sub(parse_regex[key[0]][key[1]], r"\g<inside>", line)
            if key[1] in ('code', 'latex'):
                return parse_borders[key[0]][key[1]][0] + inside + parse_borders[key[0]][key[1]][1]
            else:
                return parse_borders[key[0]][key[1]][0] + inline_parse(inside) + parse_borders[key[0]][key[1]][1]
        else:
            left =  re.sub(parse_regex[key[0]][key[1]], r"\g<left>", line)
            right = re.sub(parse_regex[key[0]][key[1]], r"\g<right>", line)
            if key[1] in ('link1', 'link2'):
                return parse_borders[key[0]][key[1]][0] + left + parse_borders[key[0]][key[1]][1] + right + parse_borders[key[0]][key[1]][2]
            else:
                return parse_borders[key[0]][key[1]][0] + left + parse_borders[key[0]][key[1]][1] + inline_parse(right) + parse_borders[key[0]][key[1]][2]
    
    
    # If we arrive here... it is because 'line' is not a cool piece of mdbg, yet, we can do smth to it
    supl_regex = [
        r"^[-\*_]{3,}",                                     # horizontal line
        r"\* \* \*",                                        # removing decoration
        r"(?:^|(?<=\n))!(?!\[)(?P<remainder>.*)",           # no indent
        r"_",                                               # replacing _ by \_
        r"&",                                               # replacing & by \&
        r"#",                                               # replacing # by \#
        r"%",                                               # replacing % by \%
        r"€",                                               # replacing € by \euro{}
        r"—",                                               # replacing — by \\textemdash\
        r'\[(?P<text>.*)\]\((?P<link>[^ ]*)( ".*")?\)', # links
        r"\<(?P<link>https?://[^ ]*)\>",                    # links
        r"[ ]*/(?=\n|$)",                                   # newline
        r"(?<!\\)LaTeX"                                     # LaTeX
    ]
    supl_repl = [
        r"\\hrulefill\n",
        r'',
        r'\\noindent\n\g<remainder>',
        r"\_",
        r"\&",
        r"\#",
        r"\%",
        r"\euro{}",
        r"\\textemdash\ ",
        r"\\href{\g<link>}{\g<text>}",
        r"\\href{\g<link>}{\g<link>}",
        r"\\newline",
        r"\\LaTeX{}"
    ]

    for i in range(len(supl_regex)):
        line = re.sub(supl_regex[i], supl_repl[i], line)

    return line

# Main

def main():
    global ARGV, doc

    # Preparing arguments and files
    # If some help is asked ?
    if ARGV['help']:
        print(doc)
        return 0

    # Treating arguments
    arg_treatment()
    inFile = ARGV['input']
    outFile = ARGV['output']

    # In case of no arguments given
    if inFile == '':
        print(doc)
        return -1

    # Preparing output file
    output = open(outFile, 'w')
    output.seek(0)

    # Reading the input file
    inputFile = open(inFile, 'r')
    contents = inputFile.read()

    # Writing in the output file
    # Document class
    output.write("\\documentclass{" + ARGV['documentclass'] + "}\n")

    # Packages
    # Some packages are loaded by default, the user can ask to load more packages
    # by putting them in the -p or --packages option
    
    additionnal_packages = []
    if 'packages' in ARGV:
        temp = ARGV['packages']
        if temp[0] != '{' or temp[-1] != '}':
            # If the user doesn't know the syntax of argument -p...
            print(doc)
            return -1
        else:
            temp = temp[1:-1]
            additionnal_packages = temp.split(', ')

    packages = ["{fontspec}",
                "[frenchb]{babel}",
                "[usenames,dvipsnames,svgnames,table]{xcolor}",
                "[a4paper]{geometry}",
                "{amsmath}",
                "{amssymb}",
                "{listings}",
                "{enumerate}",
                "{xltxtra}",
                "{soul}",
                "{csquotes}",
                "{dirtytalk}",
                "{hyperref}",
                "[official]{eurosym}",
                "{tikz}"] + additionnal_packages

    for package in packages:
        output.write(r"\usepackage" + package + '\n')
        if 'tikz' in package:
            # TikZ libraries for trees
            output.write(
                "\\usetikzlibrary{graphs, graphdrawing, arrows.meta}\n\\usegdlibrary{trees, force, layered}\n")
        elif 'geometry' in package:
            # Changing the margins
            output.write(
                "\\geometry{top=2cm, bottom=2cm, left=3cm, right=3cm}\n")

    # RobotMono font
    if ARGV['robot']:
        output.write("\setmonofont{[RobotoMono-Regular.ttf]}\n")

    # Syntax highliting
    if '`' in contents:
        # If the document is likely to contain a piece of code
        output.write(r"\lstset{basicstyle=\ttfamily,keywordstyle=\color{RedViolet},stringstyle=\color{Green},commentstyle=\color{Gray},identifierstyle=\color{NavyBlue},numberstyle=\color{Gray},numbers=left,breaklines=true,breakatwhitespace=true,breakautoindent=true,breakindent=5pt,showstringspaces=false, tabsize=4}" + '\n')

    # Presentation
    if 'title' in ARGV:
        output.write(r"\title{" + ARGV['title'] + "}\n")
    if 'author' in ARGV:
        output.write(r"\author{" + ARGV['author'] + "}\n")
    if 'date' in ARGV:
        output.write(r"\date{" + ARGV['date'] + "}\n")

    output.write("\\begin{document}\n")
    output.write("\\nocite{*}\n")

    if 'title' in ARGV:
        output.write("\\maketitle\n")

    if ARGV['tableofcontents']:
        output.write("\n\\tableofcontents\n")
    output.write("\n")

    # Creation of the main string
    main_string = block_parse(contents)

    # Formating line breaks
    main_string = re.sub(r"\\medskip", r"\n\\medskip\n", main_string)
    main_string = re.sub(r"[\n]{2,}", r"\n\n", main_string)
    main_string = re.sub(r"\n[\t]+\n", r"\n\n", main_string)
    main_string = re.sub(
        r"\\medskip[\n]{1,}\\medskip", r"\n\\medskip\n", main_string)

    # Writing the main string in the output file
    output.write(main_string)

    # Goodbye
    output.write("\n\\end{document}")

    inputFile.close()
    output.close()

    print("LaTeX output file written in :", outFile)


# Execution
if __name__ == '__main__':
    main()
else:
    print(doc)
