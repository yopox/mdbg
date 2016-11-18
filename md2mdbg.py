# -*- coding: utf-8 -*-
# Little tool to convert Mardown to Mardown BG
# Written by YoPox, Hadrien and pierrotdu18

# Import
import re
import sys

# Managing arguments
global ARGV

ARGV = {'output': '', 'input': ''}

def arg_treatment():
    global ARGV
    
    # input
    if len(sys.argv) > 1:
        ARGV['input']  = sys.argv[1]

    # output
    if len(sys.argv) > 2:
        ARGV['output'] = sys.argv[2]

    if ARGV['output'] == '':
        ARGV['output'] = re.sub(r"^(?P<name>(?:(?!\.md$).)+)(?:\.md$)?", r"\g<name>.mdbg", ARGV['input'])

# Parsing functions

def itemize_parse(matchObj):
    # Catching the itemize block from the match object
    itemize = matchObj.group(0)

    # Adding left indentation
    itemize = re.sub(r"(?P<line>.*)", r"\t\g<line>", itemize)

    # Parsing each item
    itemize = re.sub(r"(?<=- )(?P<item>(?:(?!^(?:[ ]{4})+|\t+).)*)(?=\n|$)", inline_parse, itemize)

    return itemize

def enumerate_parse(matchObj):
    # Catching the enumerate block from the match object
    enum = matchObj.group(0)

    # Adding left indentation
    enum = re.sub(r"(?P<line>.*)", r"\t\g<line>", enum)

    # Parsing each item
    enum = re.sub(r"(?<=[0-9]\. )(?P<item>(?:(?!^(?:[ ]{4})+|\t+).)*)(?=\n|$)", inline_parse, enum)

    return enum

def table_parse(matchObj):
    # Catching matchObj infos
    __table = matchObj.group(0)
    table = ''
    # Suppressing line of '----'
    for line in [line for line in re.findall(r"(?:^|(?<=\n)).*", __table) if line != '']:
        if re.sub(r"[-:\n \|]", '', line) != '':
            table += line + '\n'

    # Parsing each item
    table = re.sub(r'(?<=\|)(?P<item>[^\|]*)(?=\|)', inline_parse, table)

    return table

def block_parse(block):
    if re.sub(r'\n', '', block) == '':
        return block
    
    out = ''
    
    # A block can be several blocks itself
    # Blocks can be :
    #   - block code
    #   - itemize/enumerate
    #   - a table
    #   - a latex \[ \]
    #   - a comment
    #   - something between two of the blocks above
    # 'block' is going to be splitted into sub-blocks that will be treated recursively
    # A block is some kind of node in a tree
    # A leaf is a piece of inline text or an block "elementary brick"

    keys = ['code', 'comment', 'latex', 'itemize', 'enumerate', 'table']

    detection_regex = {
        'code':        r"(```[^\n]*\n(?:(?!```)(?:.|\n))*\n```)",
        'comment':     r"(<!\-\-(?:(?!\-\->)(?:.|\n))*\-\->)",
        'latex':       r"(\\\[(?:.|\n)*?\\\])",
        'itemize':     r"((?:(?:^|(?<=\n))- (?:.|\n(?!\n))*)+)",
        'enumerate':   r"((?:(?:^|(?<=\n))[0-9]+\. (?:.|\n(?!\n))*)+)",
        'table':       r"((?:(?:^|(?<=\n))\|(?:[^\|]*\|)+(?:(?:\n(?=\|))|$)?)+)",
    }
    
    parse_repl = {
        'code':        lambda x: x.group(0),
        'comment':     lambda x: x.group(0),
        'latex':       lambda x: x.group(0),
        'itemize':     itemize_parse,
        'enumerate':   enumerate_parse,
        'table':       table_parse,
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
        return re.sub(r"((?:.|\n)*)", parse_repl[key], block)

    # If we arrive to this point, this means block is not a block; it is just an inline part so we just have to
    return inline_parse(block)

# Inline parsing

def inline_parse(line):
    if type(line) is not str:
        line = line.groupdict()['item']

    if re.sub(r'\n', '', line) == '':
        return line

    out = ''

    keys = ['code', 'latex', 'bold', 'italic', 'strike']

    detection_regex = {
        'code':      r"(`[^`\n]*`)",
        'latex':     r"(\$[^\$]*\$)",
        'bold':      r"(\*\*(?! )(?:(?:(?!\*\*)(?:.|\n))*)\*\*)",
        'italic':    r"(_(?! )[^_]*_)",
        'strike':    r"(~~(?! )(?:(?:(?!~~)(?:.|\n))*)~~)"
    }
    parse_regex = {
        'code':      r"`(?P<inside>[^`\n]*)`",
        'latex':     r"\$(?P<inside>[^\$]*)\$",
        'bold':      r"\*\*(?! )(?P<inside>(?:(?:(?!\*\*)(?:.|\n))*))\*\*",
        'italic':    r"_(?! )(?P<inside>[^_]*)_",
        'strike':    r"~~(?! )(?P<inside>(?:(?:(?!~~)(?:.|\n))*))~~"
    }
    parse_borders = {
        'code':      '`',
        'latex':     '$',
        'bold':      '*',
        'italic':    '%',
        'strike':    '~',
    }

    n = len(line)
    matches = {}
    for key in keys:
        match = re.search(detection_regex[key], line)
        if match == None:
            matches[key] = n + 1
        else:
            matches[key] = match.start()

    key = min(keys, key = lambda x: matches[x])

    # Same as in block_parse
    if matches['latex'] != n + 1:
        key = 'latex'
    if matches['code'] != n + 1:
        key = 'code'

    if matches[key] != n + 1:
        sub_lines = re.split(detection_regex[key], line)
        if sub_lines != ['', line, '']:
            for sub_line in sub_lines:
                out += inline_parse(sub_line)
            return out
        inside = re.sub(parse_regex[key], r"\g<inside>", line)
        if key in ('code', 'latex'):
            return parse_borders[key] + inside + parse_borders[key]
        else:
            return parse_borders[key] + inline_parse(inside) + parse_borders[key]

    # If we arrive here... it is because 'line' is not a cool piece of mdbg, yet, we can do smth to it
    line = re.sub(r"[ ]*<br>(?=\n|$)", r"/", line)
    return line

# Main

def main():
    arg_treatment()

    inFile = ARGV['input']
    outFile = ARGV['output']

    # In case of no arguments given
    if inFile == '':
        return -1

    # Preparing output file
    output = open(outFile, 'w')
    output.seek(0)

    # Reading the input file
    inputFile = open(inFile, 'r')

    # Writing in the output file
    output.write(block_parse(inputFile.read()))
    inputFile.close()
    output.close()
    print("mdbg output file written in :", outFile)
    return 0


# Execution
if __name__ == '__main__':
    main()
