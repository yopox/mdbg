"""Little tool to convert Markdown to cool LaTeX documents.

Written by YoPox, Hadrien and pierrotdu18
"""

# Import
import re
import random
try:
    from pygments.styles import get_all_styles
except ImportError:
    PYGMENTS_AVAILABLE = False
else:
    PYGMENTS_AVAILABLE = True
# Parsing functions

# Block parsing


def block_code_parse(matchObj, argv):
    """To parse blocks of code.

    Option syntax : "java" if wanted language is java, and "nb-java" if
    wanted language is java AND non breaking is wanted
    """
    code = matchObj.group('code')
    __option = matchObj.group('option')
    # we remove 'nb-' if it's in the option
    option = re.sub(r"nb\-(?P<option>.*)", r"\g<option>", __option)
    # if those two are different, that's because non breaking is wanted
    non_breaking = __option != option
    out = ''
    if non_breaking:
        # Putting the code in a minipage will prevent from page breaking
        out += "\\begin{minipage}{\\linewidth}\n"
    if argv['minted'] and PYGMENTS_AVAILABLE:
        minted = argv['minted']
        if minted in ('rand', 'random'):
            minted = random.choice(list(get_all_styles()))
            print(minted)
        if 'fruity' in minted or 'vim' in minted or 'native' in minted or 'monokai' in minted:
            out += "\\begin{tcblisting}{listing only,colback=dark_bg,listing engine=minted,"
            out += "minted style=" + minted + ",minted options={breaklines},"
            out += "minted language=" + option + "}\n"
        else:
            out += "\\begin{tcblisting}{listing only,listing engine=minted,minted style=" + \
                minted + ",minted options={breaklines},minted language=" + option + "}\n"
        out += code  # the code is not modified
        out += "\n\\end{tcblisting}"
    else:
        if option != '':
            if option.lower() == 'ocaml':
                # Because lstlisting doesn't know oCaml (and we love oCaml don't we ?)
                option = 'Caml'
            out += r"\lstset{language=" + option + "}\n"
            out += "\\begin{lstlisting}\n"
            out += code  # the code is not modified
            out += "\n\\end{lstlisting}"

    if non_breaking:
        out += "\n\\end{minipage}\n"
    return out


def tree_parse(matchObj, argv):
    """To parse trees."""
    if "nTREE" in matchObj.group(0):
        return ntree_parse(matchObj, argv)        # to parsed multiple trees
    else:
        return binary_tree_parse(matchObj, argv)  # to parse binary trees


def binary_tree_parse(matchObj, argv):
    """To parse binary trees.

    nodes contains every couple like 'L 42' (see readme.md for the syntax)
    """
    nodes = [list(x) for x in re.findall(
        r'([A-Z]) "([^"]*?)"', matchObj.group('tree'))]
    l = len(nodes)
    out = ''
    out += "\n\\begin{tikzpicture}[nodes={circle, draw}]"
    out += "\n\\graph[binary tree layout, fresh nodes]{\n"
    # The package used to draw trees is TikZ and that requiers LuaLaTeX
    # to compile (the algorithm aiming at computing distance
    # between elements of the graphs is written in Lua)
    # The traversal is a pre-order traversal
    # If you don't understand that code you should go to math spé in Lycée
    # Henri IV and ask E. T.

    def get_tree(argv):
        def aux(i, depth):
            if nodes[i][0] == 'L':
                f = nodes[i][1]
                return ('"' + (block_parse(f, argv) if f != '()' else '') + '"', i + 1)
            else:
                (g, r1) = aux(i + 1, depth + 1)
                (d, r2) = aux(r1, depth + 1)
                return ('"' + block_parse(nodes[i][1], argv) +
                        '"' + " -- {" + g + "," + d + "}", r2)
        (ans, r) = aux(0, 1)
        if r != l:
            return ""
        else:
            return re.sub(r"\n ?\n", r"\n", ans) + "};\n"

    out += get_tree(argv) + "\\end{tikzpicture}\n"
    return out


def ntree_parse(matchObj, argv):
    r"""To parse general trees.

    /!\ if you want to use bold or italic etc. in a nTREE
    you must type it in LaTeX, not in MarkdownBG
    """
    tree = matchObj.group('tree')
    out = ''
    out += "\n\\begin{tikzpicture}[nodes={circle, draw}]"
    out += "\n\\graph[binary tree layout, fresh nodes]{\n"
    # the syntax we use is the syntax used by the sub package 'graph' of TikZ
    out += tree + "};\n\\end{tikzpicture}\n"
    return out


def graph_parse(matchObj, argv):
    """To parse graphs.

    We use TikZ 'graph drawing' and 'graphs' libraries, see pgfmanual for more information
    """
    option = matchObj.group('option')
    option = option if option is not None else ''
    graph = matchObj.group('graph')
    out = "\\begin{tikzpicture}\n[nodes={text height=.7em, text depth=.2em,"
    out += "draw=black!20, thick, fill=white, font=\\footnotesize, minimum "
    out += "width=0.53cm},>=stealth, rounded corners, semithick]\n\\graph [level "
    out += "distance=1cm, sibling sep=.5em, sibling distance=1cm,"
    out += option + "]\n" + '{' + graph + '};\n\\end{tikzpicture}\n'
    return out


def quote_parse(matchObj, argv):
    """To parse quoted text."""
    quotes = matchObj.group('quote')
    quotes = [x for x in re.split(r"(?:^|\n)> (.*)", quotes) if x != '' and x != '\n']
    out = "\n\\medskip\n\\begin{displayquote}\n"  # we use 'csquote' package
    for quote in quotes:
        # we parse recursively the content of the quotation
        out += block_parse(quote, argv) + r"\\"
    # we remove the extra '\\'
    return out[0:-2] + "\n\\end{displayquote}\n\\medskip\n"


def itemize_parse(matchObj, argv):
    """To parse simple lists."""
    itemize = matchObj.group(0)
    # we remove left indentation
    itemize = re.sub(r"(?:^|(?<=\n))(?:    |\t)(?P<item>.*)", r"\g<item>", itemize)
    # we split items and remove '-' symbol from each item
    items = re.split(r"(?:^|(?<=\n))- ((?:.|\n(?!- ))*)", itemize)
    # we keep only non empty items (who cares about empty items?)
    items = [x for x in items if x != '' and x != '\n']
    out = "\\begin{itemize}\n"
    for item in items:
        # we parse the item recursively and indent the LaTeX code
        out += "\t\\item "
        out += re.sub(r"\n(?P<line>.*)", r"\n\t\g<line>", block_parse(item, argv))
        out += '\n'
    out += "\\end{itemize}\n"
    return out


def enumerate_parse(matchObj, argv):
    """To parse numbered lists."""
    enum = matchObj.group(0)
    # we remove left indentation
    enum = re.sub(r"(?:^|(?<=\n))(?:    |\t)(?P<item>.*)", r"\g<item>", enum)
    # we split items and remove things like '2.' from each item
    items = re.split(r"(?:^|(?<=\n))[0-9]+\. ((?:.|\n(?![0-9]+\. ))*)", enum)
    # we keep only non empty items (who cares about empty items?)
    items = [x for x in items if x != '' and x != '\n']
    out = "\\begin{enumerate}\n"
    for item in items:
        # we parse the item recursively and indent the LaTeX code
        out += "\t\\item "
        out += re.sub(r"\n(?P<line>.*)", r"\n\t\g<line>", block_parse(item, argv))
        out += '\n'
    out += "\\end{enumerate}\n"
    return out


def table_parse(matchObj, argv):
    """To parse tables."""
    option = matchObj.group('option')
    table = matchObj.group('table')

    # number of rows
    n = len(re.findall(r"(?<=\|)([^\|]*)(?=\|)", re.findall("^.*", table)[0]))

    out = '\\begin{center}\n\\begin{tabular}'

    if option is not None:  # we treat the option
        if len(option) == 1:
            # if it is only a 'c' for example we center each cell of the table
            out += '{' + ('|' + option) * n + '|}'
        # else, we have the data of every row text alignement (if the user knows the syntax)
        else:
            options = option.split()
            out += '{'
            for op in options:
                out += '|' + option
            out += '|}'
    else:
        # if we have no option we chose a left text alignement by default
        out += '{' + ('|' + 'l') * n + '|}'

    out += '\n'

    # for each line of the table
    for line in re.findall(r"(?:^|(?<=\n)).*", table):
        if line != '' and line != '\n':
            out += "\\hline\n"  # we draw a line
            # for each element in this line
            for element in re.findall(r"(?<=\|)([^\|]*)(?=\|)", line):
                if element != '' and element != '\n':
                    # we keep only the element itself (no spaces on its sides)
                    element = re.sub(r"(?:\s*)(?P<inside>\S.*\S)(?:\s*)", r"\g<inside>", element)
                    # we parse it as a block (we can't parse it as a line
                    # if it is an itemize for example)
                    out += block_parse(element, argv) + '&'
            out = out[0:-1] + '\\\\\n'

    out = out[0:-3] + '\\\\\n\\hline\n\\end{tabular}\n\\end{center}\n'
    return out


def title_parse(matchObj, argv):
    """To parse titles."""
    titles = {
        'article': [r"\part", r"\section", r"\subsection", r"\subsubsection", r"\paragraph",
                    r"\subparagraph", r'\subsubparagraph'],
        'report':  [r"\part", r"\chapter", r"\section", r"\subsection", r"\subsubsection",
                    r"\paragraph", r"\subparagraph", r'\subsubparagraph']
    }
    level = len(matchObj.group('level')) - 1
    # if this is a 'stared' section (see readme.md)
    star = matchObj.group('star') is not None
    title = matchObj.group('title')  # title
    paragraph = matchObj.group('paragraph')  # contents of the section
    out = ''
    out += titles[argv['documentclass']][level]
    if star:
        out += '*'
    out += '{' + inline_parse(title, argv) + '}' + '\n'
    out += block_parse(paragraph, argv)
    return out


def block_parse(block, argv):
    """Main parsing function."""
    if re.sub(r'\n', '', block) == '':
        # if the block isn't very interresting we return it directly
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
    # 'block' is going to be split into sub-blocks that will
    # be treated recursively
    # A block is some kind of node in a tree
    # A leaf is a piece of inline text or a block "elementary brick"

    keys = ['code', 'comment', 'latex', 'title', 'itemize', 'enumerate', 'table', 'quotation',
            'tree', 'graph', 'center']

    detection_regex = {
        # These regexps detect the blocks and split them correctly
        'code':      r"(```[^\n]*\n(?:(?!```)(?:.|\n))*\n```)",
        'comment':   r"(<!\-\-(?:(?!\-\->)(?:.|\n))*\-\->)",
        'latex':     r"(\\\[(?:.|\n)*?\\\])",
        'title':     r"((?:^|(?<=\n))#+\*? [^\n]*(?:(?!\n#+ )(?:.|\n))*)",
        'itemize':   r"((?:(?:^|(?<=\n))(?:    |\t)- (?:.|\n(?!\n))*)+)",
        'enumerate': r"((?:(?:^|(?<=\n))(?:    |\t)[0-9]+\. (?:.|\n(?!\n))*)+)",
        'table':     r"((?:!!.*\n)?(?:\|(?:.*?|)+\n)+)",
        'quotation': r"((?:^|(?<=\n))(?:> .*\n?)+)",
        'tree':      r"(!\[n?TREE (?:(?!\]!)(?:.|\n))*\]!)",
        'graph':     r"((?:!!.*\n)?!\[GRAPH (?:(?!\]!)(?:.|\n))*\]!)",
        'center':    r"([(]{3}\n(?:.|\n)*?\n[)]{3})"
    }

    parse_regex = {
        # These regexps and those which follow are to parse the blocks
        # correctly
        'code':      r"```(?P<option>[^\n]*)\n(?P<code>(?:(?!```)(?:.|\n))*)\n```",
        'comment':   r"<!\-\-(?P<comment>(?:(?!\-\->)(?:.|\n))*)\-\->",
        'latex':     r"(?P<everything>.*)",
        'title':     r"(?:^|(?<=\n))(?P<level>#+)(?P<star>\*)?(?P<title>[^\n]*)(?P<paragraph>(?:(?!\n#+ )(?:.|\n))*)",
        'itemize':   r"(?:.|\n)*",
        'enumerate': r"(?:.|\n)*",
        'table':     r"(?:!!tab (?P<option>.*?)\n)?(?P<table>(?:\|(?:.*?\|)+\n)+)",
        'quotation': r"(?:^|(?<=\n))(?P<quote>(?:[>] .*\n?)+)",
        'tree':      r"!\[n?TREE (?P<tree>(?:(?!\]!)(?:.|\n))*)\]!",
        'graph':     r"(?:!!(?P<option>.*)\n)?!\[GRAPH (?P<graph>(?:(?!\]!)(?:.|\n))*)\]!",
        'center':    r"[(]{3}\n(?P<inside>(?:.|\n)*?\n)[)]{3}"
    }

    parse_repl = {
        'code':         lambda x: block_code_parse(x, argv),
        'comment':      r"% \g<comment>",
        'latex':        r"\g<everything>",
        'title':        lambda x: title_parse(x, argv),
        'itemize':      lambda x: itemize_parse(x, argv),
        'enumerate':    lambda x: enumerate_parse(x, argv),
        'table':        lambda x: table_parse(x, argv),
        'quotation':    lambda x: quote_parse(x, argv),
        'tree':         lambda x: tree_parse(x, argv),
        'graph':        lambda x: graph_parse(x, argv),
        'center':       "\\begin{center}\n\g<inside>\n\\end{document}"
    }

    n = len(block)

    # matches is going to contain couples (i, j) where i is a key in keys
    # and j is the position of the first key-element in the block
    # if there is no key-element in the block, the position is set to n + 1
    # where n is the length of the block
    matches = {}
    for key in keys:
        match = re.search(detection_regex[key], block)
        if match is None:
            matches[key] = n + 1
        else:
            matches[key] = match.start()

    # We take the key of the element which is the first in the block
    key = min(keys, key=lambda x: matches[x])

    # If there is code/latex we have to choose it before other blocks (and code
    # before latex)
    if matches['latex'] != n + 1:
        key = 'latex'
    if matches['code'] != n + 1:
        key = 'code'

    # block is going to be split into the first key-element and the rest of
    # the string
    if matches[key] != n + 1:  # if this element exists
        sub_blocks = re.split(detection_regex[key], block)
        if sub_blocks != ['', block, '']:
            for sub_block in sub_blocks:
                out += block_parse(sub_block, argv)
            return out
        return re.sub(parse_regex[key], parse_repl[key], block)

    # If we arrive to this point, it means that block isn't a block ;
    # it is just an inline part so we just have to
    return inline_parse(block, argv)


# Inline parsing


def inline_parse(line, argv):
    """To parse inline elements."""
    if re.sub(r'\n', '', line) == '':
        return line

    out = ''
    keys = {
        # Things which take only one argument
        1: ['code', 'latex', 'quote1', 'quote2', 'footnote', 'superscript', 'subscript', 'bold',
            'underline', 'italic', 'strike'],
        # Things which take two arguments
        2: ['color', 'link1', 'link2']
    }

    detection_regex = {
        1: {
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
            'color':    r"\{(?P<left>[^\n\{\}]*)\}\[(?P<right>[^\n\{\}]*)\]",
            'link1':    r"\<(?P<left>(?P<right>https?://[^ ]*))\>",
            'link2':    r"\[(?P<left>.*)\]\((?P<right>[^ ]*)( \".*\")?\)"
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
            if match is None:
                matches[i][key] = n + 1
            else:
                matches[i][key] = match.start()

    key = min([(i, keys[i][j]) for i in (1, 2) for j in range(len(keys[i]))],
              key=lambda x: matches[x[0]][x[1]])

    # Same as in block_parse
    if matches[1]['latex'] != n + 1:
        key = (1, 'latex')
    if matches[1]['code'] != n + 1:
        key = (1, 'code')

    if matches[key[0]][key[1]] != n + 1:
        sub_lines = re.split(detection_regex[key[0]][key[1]], line)
        if sub_lines != ['', line, '']:
            for sub_line in sub_lines:
                out += inline_parse(sub_line, argv)
            return out
        if key[0] == 1:
            inside = re.sub(parse_regex[key[0]][key[1]], r"\g<inside>", line)
            if key[1] in ('code', 'latex'):
                return parse_borders[key[0]][key[1]][0] + inside + parse_borders[key[0]][key[1]][1]
            else:
                return parse_borders[key[0]][key[1]][0] + inline_parse(inside, argv) + \
                    parse_borders[key[0]][key[1]][1]
        else:
            left = re.sub(parse_regex[key[0]][key[1]], r"\g<left>", line)
            right = re.sub(parse_regex[key[0]][key[1]], r"\g<right>", line)
            if key[1] in ('link1', 'link2'):
                return parse_borders[key[0]][key[1]][0] + left + parse_borders[key[0]][key[1]][1] +\
                    right + parse_borders[key[0]][key[1]][2]
            else:
                return parse_borders[key[0]][key[1]][0] + left + parse_borders[key[0]][key[1]][1] +\
                    inline_parse(right, argv) + parse_borders[key[0]][key[1]][2]

    # If we arrive here... it is because 'line' is not a cool piece of mdbg,
    # yet, we can do something to it
    supl_regex = [
        r"^[-\*_]{3,}",                           # horizontal line
        r"\* \* \*",                              # removing decoration
        r"(?:^|(?<=\n))!(?!\[)(?P<remainder>.*)",  # no indent
        r"_",                                     # replacing _ by \_
        r"&",                                     # replacing & by \&
        r"#",                                     # replacing # by \#
        r"%",                                     # replacing % by \%
        r"€",                                     # replacing € by \euro{}
        r"—",                                     # replacing — by \\textemdash\
        r'\[(?P<text>.*)\]\((?P<link>[^ ]*)( ".*")?\)',     # links
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


def main(argv):
    """Main function."""
    # Preparing output file
    output = open(argv['output'], 'w')
    output.seek(0)

    # Reading input file
    inputFile = argv['input']
    contents = inputFile.read()

    # Writing to output file
    # Document class
    output.write("\\documentclass{" + argv['documentclass'] + "}\n")

    # Packages
    # Some packages are loaded by default, the user can ask to load more
    # packages by putting them in the -p or --packages option
    additionnal_packages = []
    if argv['packages']:
        temp = argv['packages']
        if temp[0] != '{' or temp[-1] != '}':
            # If the user doesn't know how argument -p works...
            argv['print_help']()
            return -1
        else:
            temp = temp[1:-1]
            additionnal_packages = temp.split(', ')
    packages = ["{fontspec}",
                "[frenchb]{babel}",
                "[usenames,dvipsnames,svgnames,table]{xcolor}",
                "[a4paper]{geometry}",
                "{tcolorbox}",
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
        if 'tcolorbox' in package and argv['minted']:
            output.write(r"\usepackage" + package + '\n')
            output.write("\\tcbuselibrary{minted}\n")
            output.write("\\definecolor{dark_bg}{RGB}{38, 50, 56}\n")
            continue
        output.write(r"\usepackage" + package + '\n')
        if 'tikz' in package:
            # TikZ libraries for trees
            output.write("\\usetikzlibrary{graphs, graphdrawing, arrows.meta}\n"
                         "\\usegdlibrary{trees, force, layered}\n")
        elif 'geometry' in package:
            # Changing the margins
            output.write("\\geometry{top=2cm, bottom=2cm, left=3cm, right=3cm}\n")

    # RobotoMono font
    if argv['roboto']:
        output.write("\\usepackage{roboto}\n")

    # Syntax highliting
    if '`' in contents:
        # If the document is likely to contain a piece of code
        if argv['minted']:
            output.write("\\usemintedstyle{" + argv['minted'] + "}\n")
        else:
            output.write(
                r"\lstset{basicstyle=\ttfamily,keywordstyle=\color{RedViolet},"
                " stringstyle=\color{Green}, commentstyle=\color{Gray}, "
                "identifierstyle=\color{NavyBlue}, numberstyle=\color{Gray},"
                " numbers=left, breaklines=true,breakatwhitespace=true,"
                " breakautoindent=true,breakindent=5pt,"
                "showstringspaces=false, tabsize=4}\n")

    # Presentation
    if argv['title']:
        output.write(r"\title{" + argv['title'] + "}\n")
    if argv['author']:
        output.write(r"\author{" + argv['author'] + "}\n")
    if argv['date']:
        output.write(r"\date{" + argv['date'] + "}\n")

    output.write("\\begin{document}\n")
    output.write("\\nocite{*}\n")

    if argv['title']:
        output.write("\\maketitle\n")

    if argv['tableofcontents']:
        output.write("\n\\tableofcontents\n")
    output.write("\n")

    # Creation of the main string
    main_string = block_parse(contents, argv)

    # Formatting line breaks
    main_string = re.sub(r"\\medskip", r"\n\\medskip\n", main_string)
    main_string = re.sub(r"[\n]{2,}", r"\n\n", main_string)
    main_string = re.sub(r"\n[\t]+\n", r"\n\n", main_string)
    main_string = re.sub(r"\\medskip[\n]{1,}\\medskip", r"\n\\medskip\n", main_string)

    # Writing the main string in the output file
    output.write(main_string)

    # Goodbye
    output.write("\n\\end{document}")

    inputFile.close()
    output.close()

    print("LaTeX output file written in :", argv['output'])
