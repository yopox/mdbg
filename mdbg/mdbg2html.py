# This version is based on the former mdbg2tex, so it is obsolete


# -*- coding: utf-8 -*-
# Little tool to convert Markdown to cool HTML documents.
# Written by YoPox, Hadrien and pierrotdu18

# Import
import re
import sys

# Parsing functions


def sep_parse_block_code(matchObj, block_codes, argv):
    # Option syntax : "java" if wanted language is java, and "nb-java" if
    # wanted language is java AND non breaking is wanted
    code = matchObj.group('code')
    __option = matchObj.group('option')
    option = re.sub(r"nb\-(?P<option>.*)", r"\g<option>", __option)
    non_breaking = __option != option
    out = ''
    if non_breaking:
        # putting the code in a minipage will prevent from page breaking
        out += "\\begin{minipage}{\\linewidth}\n"
    if option != '':
        if option.lower() == 'ocaml':
            # because lstlisting doesn't know ocaml
            option = 'Caml'
        out += r"\lstset{language=" + option + "}\n"
    out += "\\begin{lstlisting}\n"
    out += code
    out += "\n\\end{lstlisting}"
    if non_breaking:
        out += "\\begin{minipage}{\\linewidth}\n"
    block_codes.append(out)
    # How is going to use &é(]°(-è*@|{) in his document ?...
    return r"&é(]°(-è*@|{)" + str(len(block_codes)) + r"&é(]°(-è*@|{)"


def sep_parse_inline_code(matchObj, inline_codes, argv):
    code = matchObj.group('code')
    inline_codes.append("\\verb`" + code + '`')
    # Again, no one will use £%£%§²& in a document, well... except you maybe ?
    return r'£%£%§²&' + str(len(inline_codes)) + r'£%£%§²&'


def bolden(matchObj, argv):
    # All this funny and odd regexp is to treat things
    # like "foo **bar _ foo** bar ~~foo _bar~~"
    # Example : https://regex101.com/r/CzZFwo/1
    # On this example (the first regexp which follows) we want to match a
    # beggining of a strikethrough environnement
    # Once every beggining/end of every different environnement than
    # the current one has been found, we have to check if
    # there are as many begginings as ends, for each environnement,
    # otherwise we are in a wierd case like above, that's why
    # length of findall lists are compared
    # This is the same for each style environnement handled by this program,
    # i.e. **, _ and ~~
    bold = matchObj.group('bold')
    left1 = re.findall(
        r"^~~((?!(?:~~))[^ ])|(?:(?!(?:~~))\W)~~(?:(?!(?:~~))[^ ])", bold)
    right1 = re.findall(
        r"(?:(?!(?:~~))[^ ])~~$|(?:(?!(?:~~))[^ ])~~(?:(?!(?:~~))\W)", bold)
    left2 = re.findall(
        r"^_((?!(?:_))[^ ])|(?:(?!(?:_))\W)_(?:(?!(?:_))[^ ])", bold)
    right2 = re.findall(
        r"(?:(?!(?:_))[^ ])_$|(?:(?!(?:_))[^ ])_(?:(?!(?:_))\W)", bold)
    if r"\begin" not in bold and r"\end" not in bold and '&' not in bold \
            and len(left1) == len(right1) and len(left2) == len(right2):
        return r"<span class='bold'>" + bold + "</span>"
    else:
        return bold


def italien(matchObj, argv):  # italicien ? italicize ?
    # c.f. bolden()
    it = matchObj.group('it')
    left1 = re.findall(r"^\*\*((?!(?:\*\*))[^ ])|(?:(?!(?:\*\*))\W)"
                       "\*\*(?:(?!(?:\*\*))[^ ])", it)
    right1 = re.findall(r"(?:(?!(?:\*\*))[^ ])\*\*$|(?:(?!(?:\*\*))[^ ])"
                        "\*\*(?:(?!(?:\*\*))\W)", it)
    left2 = re.findall(
        "^_((?!(?:_))[^ ])|(?:(?!(?:_))\W)_(?:(?!(?:_))[^ ])", it)
    right2 = re.findall(
        "(?:(?!(?:_))[^ ])_$|(?:(?!(?:_))[^ ])_(?:(?!(?:_))\W)", it)
    if r"\begin" not in it and r"\end" not in it and '&' not in it and \
            len(left1) == len(right1) and len(left2) == len(right2):
        return r"<span class='italic'>" + it + "</span>"
    else:
        return it


def striken(matchObj, argv):
    # c.f. bolden()
    strike = matchObj.group('strike')
    left1 = re.findall(r"^\*\*((?!(?:\*\*))[^ ])|(?:(?!(?:\*\*))\W)"
                       "\*\*(?:(?!(?:\*\*))[^ ])", strike)
    right1 = re.findall(r"(?:(?!(?:\*\*))[^ ])\*\*$|(?:(?!(?:\*\*))[^ ])"
                        "\*\*(?:(?!(?:\*\*))\W)", strike)
    left2 = re.findall(
        "^~~((?!(?:~~))[^ ])|(?:(?!(?:~~))\W)~~(?:(?!(?:~~))[^ ])", strike)
    right2 = re.findall(
        "(?:(?!(?:~~))[^ ])~~$|(?:(?!(?:~~))[^ ])~~(?:(?!(?:~~))\W)", strike)
    if r"\begin" not in strike and r"\end" not in strike and '&' not in \
            strike and len(left1) == len(right1) and len(left2) == len(right2):
        return r"<span class='strike'>" + strike + "</span>"
    else:
        return strike


def tree_parse(matchObj, argv):
    # Possible options :
    #   - c : center
    option = matchObj.group('option')
    nodes = [list(x) for x in re.findall(
        r'([A-Z]) "([^"]*?)"', matchObj.group('tree'))]
    l = len(nodes)
    out_str = "\n\\begin{center}" if option == 'c' else ""
    out_str += "\n\\begin{tikzpicture}[nodes={circle, draw}]"
    out_str += "\n\\graph[binary tree layout, fresh nodes]{\n"
    # The package used to draw trees is TikZ and that requiers
    # LuaLaTeX to compile (the algorithm aiming at computing distance
    # between elements of the graphs is written in Lua)
    # The traversal is a pre-order traversal
    # If you don't understand that code you should go to math spé in Lycée
    # Henri IV and ask E. T.

    def get_tree(argv):
        def aux(i, depth):
            if nodes[i][0] == 'F':
                f = nodes[i][1]
                return ('"' + (f if f != '()' else '') + '"', i + 1)
            else:
                (g, r1) = aux(i + 1, depth + 1)
                (d, r2) = aux(r1, depth + 1)
                return ('"' + nodes[i][1] + '"' +
                        " -- {" + g + "," + d + "}", r2)
        (ans, r) = aux(0, 1)
        if r != l:
            return ""
        else:
            return re.sub("\n ?\n", "\n", ans) + "};\n"
    out_str += get_tree(argv) + "\\end{tikzpicture}\n" + \
        ("\\end{center}\n" if option == 'c' else "")
    return out_str


def ntree_parse(matchObj, argv):
    # Possible options :
    #   - c : center
    option = matchObj.group('option')
    tree = matchObj.group('tree')
    out_str = "\n\\begin{center}" if option == 'c' else ""
    out_str += "\n\\begin{tikzpicture}[nodes={circle, draw}]"
    out_str += "\n\\graph[binary tree layout, fresh nodes]{\n"
    out_str += tree + "};\n\\end{tikzpicture}\n" + ("\\end{center}\n" if option == 'c' else "")
    return out_str


def quote_parse(matchObj, argv):
    quotes = matchObj.group('quote')
    quotes = re.split("(?:^|\n)> (.*)", quotes)
    try:
        # For quotations with a reference
        reference = matchObj.group('reference')
        out = ''
        for quote in quotes:
            if quote != '':
                out += quote + r" \\ "
        return r"\epigraph{" + out[0:-4] + "}" + "{" + reference + "}"
    except:
        # For quotations without a reference
        out = "\n\\medskip\n\\begin{displayquote}\n"
        for quote in quotes:
            if quote != '':
                out += quote + r" \\ "
        return out[0:-4] + "\n\\end{displayquote}\n\\medskip\n"


def itemize_parse(i, matchObj, argv):
    # i : item depth
    itemize = matchObj.group(0)
    # If level is not 1 we add some space and a '-' to make the algorithm
    # believe that the items are normal markdown
    # items when it parses a smaller level
    # When all levels greater than 1 are parsed, level 1 is parsed normally
    # and that's why everything goes well
    # This functions does the work for only ONE level, of depth i
    out = (("    " * i + "- ") if i != 1 else "") + "\\begin{itemize}\n"
    for item in re.findall(
            r"(?:^(?:[ ]{4})+|\n(?:[ ]{4})+)- ((?:(?!\n[ ]{4,}- )(?:.|\n))*)", itemize):
        out += (r"\item " if item != '' and item[0:min(len(item), 6)] != "\\begin" else "")
        out += item + '\n'
    out += r"\end{itemize}"
    return out


def enumerate_parse(i, matchObj, argv):
    # Same idea
    enum = matchObj.group(0)
    out = (("    " * i + "1. ") if i != 1 else "") + "\\begin{enumerate}\n"
    for item in re.findall(
            r"(?:^(?:[ ]{4})+|\n(?:[ ]{4})+)[0-9]+\. ((?:(?!\n[ ]{4,}[0-9]+\. )(?:.|\n))*)", enum):
        out += (r"\item " if item != '' and item[0:min(len(item), 6)] != "\\begin" else "")
        out += item + '\n'
    out += r"\end{enumerate}"
    return out


def table_parse(m, argv):
    # m : match trouvé pour un tableau :
    # m.group(0) : tableau en entier
    # m.group(1) : 1ère ligne
    # m.group(5) : ligne de centrage
    # m.group(7) : reste du tableau
    # pour plus de renseignements : n est a adapter
    # for i in range(n): print(i," : ",m.group(i))

    firstLine = [col for col in m.group(1).split("|") if col != ""]
    centerLine = [col for col in m.group(5).split("|") if col != ""]
    nbCol = len(firstLine)
    result = "\\begin{center}\n\\begin{tabular}{|"

    # Traitement du centrage
    def dispoCell(cell):
        liste = [char for char in cell if char != " "]
        if liste[0] == ":" and liste[-1] == ":":
            return 'c'
        if liste[-1] == ":":
            return 'r'
        return 'l'

    for i in range(nbCol):
        if i < len(centerLine):
            result += dispoCell(centerLine[i]) + "|"
        else:
            result += "l|"

    result += "}\n\\hline\n"

    # Première colonne
    result += firstLine[0]
    for cell in firstLine[1:]:
        result += " & " + cell
    result += "\\\\\n "

    # Reste
    for line in m.group(7).split('\n'):
        tablLine = [cell for cell in line.split("|") if cell != ""]
        if tablLine:
            result += "\\hline\n" + tablLine[0]
            for i, cell in enumerate(tablLine[1:]):
                if i < nbCol - 1:
                    result += " & " + cell
            result += "\\\\\n"

    return result + "\\hline \n\\end{tabular}\n\\end{center}\n"


def merge_inline_code(matchObj, inline_codes, argv):
    return inline_codes[int(matchObj.group('i')) - 1]


def merge_block_code(matchObj, block_codes, argv):
    return block_codes[int(matchObj.group('i')) - 1]


def parse(paragraph, argv):
    # Parsing blocks of code
    # Blocks are "encrypted" in the string and stocked in a list. Everything
    # is merged afterwards.
    block_codes = []
    paragraph = re.sub(
        r"```(?P<option>[^\n]*)\n(?P<code>(?:(?!```)(?:.|\n))*)\n```",
        lambda x: sep_parse_block_code(x, block_codes, argv), paragraph)

    # Parsing inline code
    # Inline codes are "encrypted" in the string and stocked in a list.
    # Everything is merged afterwards.
    inline_codes = []
    paragraph = re.sub("`(?P<code>[^`]*)`",
                       lambda x: sep_parse_inline_code(x, inline_codes, argv), paragraph)

    # Parsing titles
    # Each paragraph's string begins with some '#' so regex matches only the
    # string's very beginning
    paragraph = re.sub(r"^[#]{6} (?P<g>(.*))", r"<h6>\g<g></h6>", paragraph)
    paragraph = re.sub(r"^[#]{5} (?P<g>(.*))", r"<h5>\g<g></h5>", paragraph)
    paragraph = re.sub(r"^[#]{4} (?P<g>(.*))", r"<h4>\g<g></h4>", paragraph)
    paragraph = re.sub(r"^[#]{3} (?P<g>(.*))", r"<h3>\g<g></h3>", paragraph)
    paragraph = re.sub(r"^[#]{2} (?P<g>(.*))", r"<h2>\g<g></h1>", paragraph)
    paragraph = re.sub(r"^[#]{1} (?P<g>(.*))", r"<h1>\g<g></h1>", paragraph)

    # Horizontal lines
    paragraph = re.sub(r"^[-\*_]{3,}", "<div class='hline'></div>", paragraph)

    # Removing decoration
    paragraph = re.sub(r"\* \* \*", '', paragraph)

    # TODO : Puting a \noindent if line begins with '!'
    # paragraph = re.sub(r"(?:^|(?<=\n))!(?!\[)(?P<remainder>.*)",
    #                    r'\\noindent\n\g<remainder>', paragraph)

    # Parsing inline quotes
    # Uses non greedy regexp with lookbehinds/afters because for example :
    # four o'clock in the mornin' MUSN'T be parsed !
    # One should think "hello 'hello" hello' generates and error but it juste
    # gives \say{hello \say{hello} hello} which is perfectly correct an
    # renders "hello 'hello' hello" in LaTeX
    paragraph = re.sub(r"(?<!\w)\"(?=\w)(?P<quote>.*?)(?<=\w)\"(?!\w)",
                       r"<div class='quote'>\g<quote></div>", paragraph)
    paragraph = re.sub(r"(?<!\w)'(?=\w)(?P<quote>.*?)(?<=\w)'(?!\w)",
                       r"<div class='quote'>\g<quote></div>", paragraph)

    # Operations on non-LaTeX text
    # For bold, italic etc. LaTeX must be put aside : paragraph is splitted
    # into LaTeX parts and non-LaTeX parts which are called fragments
    fragments = re.split(r"(\$(?:(?!\$)(?:.|\n))*\$|"
                         "\\\[(?:(?!(?:\\\[|\\\]))(?:.|\n))*\\\])", paragraph)

    # Each style has it own function that checks if there are no subtle syntax
    # problems
    for i in range(len(fragments)):
        if fragments[i] != '' and fragments[i][0] != '$' and \
                fragments[i][0:min(len(fragments[i]), 2)] != "\\[":
            # Bold
            fragments[i] = re.sub(
                r"[*]{2}(?! )(?P<bold>(?:(?![*]{2})(?:.|\n))+)(?<! )[*]{2}",
                lambda x: bolden(x, argv), fragments[i])

            # Italic
            fragments[i] = re.sub(r"_(?! )(?P<it>(?:(?!_)(?:.|\n))+)(?<! )_",
                                  lambda x: italien(x, argv), fragments[i])

            # Strikethrough
            fragments[i] = re.sub(
                r"~~(?! )(?P<strike>(?:(?!~~)(?:.|\n))+)(?<! )~~",
                lambda x: striken(x, argv), fragments[i])

            # Links
            # Links like "[This is google](http://www.google.com)"
            fragments[i] = re.sub(
                r"""\[(?P<text>.*)\]\((?P<link>[^ ]*)( ".*")?\)""",
                "<a href='\g<link>'>\g<text></a>", fragments[i])
            # Links like "<http://www.google.com>"
            fragments[i] = re.sub(r"\<(?P<link>https?://[^ ]*)\>",
                                  "<a href='\g<link>'>\g<link></a>", fragments[i])
            # Links like " http://www.google.com "
            fragments[i] = re.sub(r" (?P<link>https?://[^ ]*) ",
                                  " <a href='\g<link>'>\g<link></a> ", fragments[i])
            # TODO : Replacing _ by \_ (only in non-LaTeX parts obviously !)
            # fragments[i] = re.sub("_", r"\_", fragments[i])

    # Merging fragments
    paragraph = ''
    for fragment in fragments:
        paragraph += fragment

    # New line
    # It's ok <br> is already HTML code :-)

    # Replacing x by \x
    # when x is a specific key word in LaTeX (and x != _)
    # fragments[i] = re.sub("&", r"\&", fragments[i])
    # fragments[i] = re.sub("#", r"\#", fragments[i])

    # TODO : Trees
    # Documentation in function tree_parse()
    # paragraph = re.sub(
    # r"!\[(?:(?P<option>[a-z])-)?TREE (?P<tree>(?:(?!\]!).)*)\]!",
    # tree_parse, paragraph)

    # TODO : nTrees
    # Documentation in function tree_parse()
    # paragraph = re.sub(
    # r"!\[(?:(?P<option>[a-z])-)?nTREE (?P<tree>(?:(?!\]!).)*)\]!",
    # ntree_parse, paragraph)

    # Comments
    # Same as <br>
    # paragraph = re.sub(
    # r"<!\-\-(?P<comment>(?:(?!\-\->).)*)\-\->", "% \g<comment>", paragraph)

    # Quotes
    # Documentation in function quote_parse()
    paragraph = re.sub(r"(?P<quote>(?:^>|(?<=\n)>) (?:.|\n(?=> ))*)" +
                       "\n(?:\((?P<reference>.+)\))?",
                       lambda x: quote_parse(x, argv), paragraph)

    # Itemize
    # Item levels are parsed in the decreasing order
    # More documentation in function itemize_parse()
    for i in range(4, 0, -1):
        pattern = r"(?:^[ ]{" + str(4 * i) + r"}|(?<=\n)[ ]{" + str(4 * i) + \
            r"})- (?:(?!(?:\n\n|\n[ ]{0," + str(4 * i - 2) + r"}- ))(?:.|\n))*"
        paragraph = re.sub(pattern, lambda x: itemize_parse(i, x, argv), paragraph)

    # Enumerate
    # Same : more documentation in function parse_itemize()
    for i in range(4, 0, -1):
        pattern = r"(?:^[ ]{" + str(4 * i) + r"}|(?<=\n)[ ]{" + str(4 * i) + \
            r"})[0-9]+\. (?:(?!(?:\n\n|\n[ ]{0," + str(4 * i - 2) + r"}[0-9]+\. ))(?:.|\n))*"
        paragraph = re.sub(pattern, lambda x: enumerate_parse(i, x, argv), paragraph)

    # Parsing tables
    paragraph = re.sub(r"((\|[^\n|]+)*)(\s)*\|?(\s)*((\| ?:?-+:? ?)+)"
                       "\|[ \t]*\n[ \t]*((((\|([^|\n]*))*)\|?[ \t]*\n?)+)",
                       lambda x: table_parse(x, argv), paragraph)

    # Merging inline code
    paragraph = re.sub(r"£%£%§²&(?P<i>[0-9]+)£%£%§²&",
                       lambda x: merge_inline_code(x, inline_codes, argv), paragraph)

    # Merging blocks of code
    paragraph = re.sub(r"&é\(\]°\(\-è\*@\|\{\)(?P<i>[0-9]+)&é\(\]°\(\-è\*@\|\{\)",
                       lambda x: merge_block_code(x, block_codes, argv), paragraph)

    return paragraph

# Main


def main(argv):

    # In case of no arguments given
    if argv['input'] == '':
        print(doc)
        return -1

    # Preparing output file
    output = open(argv['output'], 'w')
    output.seek(0)

    # Reading the input file
    contents = argv['input'].read()

    # Writing in the output file
    # Document class
    output.write("""<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n""")

    # TODO : Presentation
    if argv['title']:
        output.write(r"<title>" + argv['title'] + "</title>\n")
    # if 'author' in argv:
    #     output.write(r"\author{" + argv['author'] + "}\n")
    # if 'date' in argv:
    #     output.write(r"\date{" + argv['date'] + "}\n")

    # TODO : output.write("\setmonofont{[RobotoMono-Regular.ttf]}\n")

    output.write("""</head>\n<body>\n""")

    # TODO : Table of contents
    # if argv['tableofcontents']:
    #     output.write("\n\\tableofcontents\n")
    # output.write("\n")

    # Creation of the main string
    main_string = ""

    # Creation of paragraphs
    # The text is splitted into different paragraphs,
    # which makes the parsing easier
    # A paragraph begins with some #s and a title
    paragraphs = re.split(r"(#+ [^\n]*(?:(?!\n#+ )(?:.|\n))*)", contents)

    # Parsing each paragraph and adding it to the main string
    for paragraph in paragraphs:
        main_string += parse(paragraph, argv)

    # Formating line breaks
    # main_string = re.sub(r"\\medskip", r"\n\\medskip\n", main_string)
    # main_string = re.sub(r"[\n]{2,}", r"\n\n", main_string)
    # main_string = re.sub(r"\\medskip[\n]{1,}\\medskip", r"\n\\medskip\n", main_string)

    # Writing the main string in the output file
    output.write(main_string)

    # Goodbye
    output.write("""</body>\n</html>""")

    inputFile.close()
    output.close()

    print("HTML output file written in :", argv['output'])
