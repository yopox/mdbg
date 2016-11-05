# BG-flavoured markdown

Mardown BG (_.mdbg_) is an improvement of the existing [Mardown](https://fr.wikipedia.org/wiki/Markdown) language.

It provides nice features which make it possible to generate a fresh, correct and nice _.tex_ document.

# Syntax

## Markdown-flavoured

### Headers

Like in markdown.

```mdbg
# H1
## H2
### H3
#### H4
##### H5
###### H6
```

#### Non numbered sections

For non enumerated sections :

```mdbg
#* H1
##* H2
###* H3
####* H4
#####* H5
######* H6
```


### Emphasis

Translations :

#### Bold

In markdown :

```md
**bold** or __bold__
```

In mdbg :

```mdbg
*bold*
```

#### Underline

```mdbg
_underline_
```

#### Italic

In markdown :

```md
_italic_ or *italic*
```

In mdbg :

```mdbg
%italic%
```

#### Strikethrough

In markdown :

```md
~~strikethrough~~
```

In mdbg :

```mdbg
~strikethrough~
```

### Lists

Small changes have been made.

This is a list in mdbg :

```mdbg
Neutral text :
    - first item
    - second item
        - first second item
        - second second item
    - third item
```

and an enumerated list :

```mdbg
    1. first item
    2. second item
        1. first second item
        2. second second item
    3. third item
```

The indentations can be four spaces or a tabulation but each item has to be idented.

### Links

```mdbg
[text for link](https://www.google.com)

[text for link](https://www.google.com "title for link")
```

### Code

Like in Markdown.

### Tables

Like Markdown, without the 2nd line.

In mdbg :

```mdbg
| C11 | C21 | C31 |
| C21 | C22 | C32 |
| C31 | C32 | C33 |
```

Whereas in Markdown :

```md
| C11 | C21 | C31 |
| --- | --- | --- |
| C21 | C22 | C32 |
| C31 | C32 | C33 |
```

You can't chose text alignment for every cell but you can chose it for every row by adding the command `!!tab` followed by the alignments.

For example one possible table would be :

```mdbg
!!tab r c l
| C11 | C21 | C31 |
| C21 | C22 | C32 |
| C31 | C32 | C33 |
```

## New !

### Trees

#### Basic binary tree

Description :
  - Command : `![TREE]!`
  - Root : `R "text"`
  - Node : `N "text"`
  - Leave : `L "text"`

```mdbg
![TREE R "root" N "a node" L "a leave" L "an other leave" N "an other node" L "a leave again !" N "a node again !" L  "OneWord" L "the last leave"]!
```

If you want to draw an non strictly binary tree, you can write `L ()` for a empty leaf

#### Non binary trees

Command : `![nTREE]!`

```mdbg
![nTREE "A" -- {"B" -- {"H" -- {"N", "O"}, "I", "J"}, "C", "D", "E" -- {"K" -- "P", "L" -- "Q"}, "F", "G" -- "M"}]!
```

#### Centering

You can center a tree by adding the option `c` next to the command opener :
Command : `![c-TREE]!` or `![c-nTREE]!`

```mdbg
![c-nTREE "A" -- {"B" -- {"H" -- {"N", "O"}, "I", "J"}, "C", "D", "E" -- {"K" -- "P", "L" -- "Q"}, "F", "G" -- "M"}]!
```

### Graphs

You can draw graphs with a very simple syntax (the same as nTREE syntax).

This is made possible thanks to _TikZ_ fantastic `graphs` and `graphdrawing` packages, with some of their libraries.

Command : `![GRAPH .............!]`

With a possible `!!option` before `![GRAPH...` line.

This `option` will be translated to `\graph[<option>]...` in _LaTeX_.

See pgfmanual for more information about the syntax.

You can also base your graph on the example given in the section **Examples**

### New text features

#### Superscript

You can use text in superscript :

```mdbg
We live in Paris, in the 5^{th}
```

#### Subscript

You can use text in subscript :

```mdbg
This is a normal text_{this one is subscripted}
```

#### Footnotes

This is how to use footnotes :

```mdbg
I never work ***{almost}
```

#### Colored texts

How to use colored texts :

```mdbg
I love {red}[red] and {green}[blue witten in green] !
```

A list of all possible colors is given at the end of this readme.

### Miscellaneous

Add a `!` at the begining of a line to have a `\noindent` before this line in the _LaTeX_ generated file.

Add a `/` at the end of a line to have a line break.

# Examples

## Trees

The command `![TREE R 1 N 2 F 3 F 4 F 5]!` produces the following result in LaTeX :

![Binary tree](http://www.mirari.fr/ShRU)

the command `![nTREE A -- {B -- {H -- {N, O}, I, J}, C, D, E -- {K -- P, L -- Q}, F, G -- M}]!` produces the following result in LaTeX :

![Multiple tree](http://www.mirari.fr/fi6Z)

## Code

Those lines :
```md
```ocaml
let fg i = 2 * i + 1;;
let fd i = 2 * i + 2;;

let rec heapify a n i = match fg i, fd i with
	| g, d when g > n -> ()
	| g, d when d > n -> if a.(i) < a.(g) then swap a i g
	| g, d -> if a.(i) < a.(g) || a.(i) < a.(d) then begin let k = if a.(g) > a.(d) then g else d in swap a i k; heapify a n k end;;

let heap_sort a = let n = ref (vect_length a - 1) in
	for k = !n downto 0 do
		heapify a !n k
	done;
	while !n <> 0 do
		swap a 0 !n;
		decr n;
		heapify a !n 0
	done;;
``` 
```

Will produce this :

![Some code in ocaml](http://www.mirari.fr/ogMn)

## Graphs

```mdbg
!!layered layout
![GRAPH "5th Edition" -> { "6th Edition", "PWB 1.0" };
"6th Edition" -> { "LSX", "1 BSD", "Mini Unix", "Wollongong", "Interdata" };
"Interdata" -> { "Unix/TS 3.0", "PWB 2.0", "7th Edition" };
"7th Edition" -> { "8th Edition", "32V", "V7M", "Ultrix-11", "Xenix", "UniPlus+" };
"V7M" -> "Ultrix-11";
"8th Edition" -> "9th Edition";
"1 BSD" -> "2 BSD" -> "2.8 BSD" -> { "Ultrix-11", "2.9 BSD" };
"32V" -> "3 BSD" -> "4 BSD" -> "4.1 BSD" -> { "4.2 BSD", "2.8 BSD", "8th Edition" };
"4.2 BSD" -> { "4.3 BSD", "Ultrix-32" };
"PWB 1.0" -> { "PWB 1.2" -> "PWB 2.0", "USG 1.0" -> { "CB Unix 1", "USG 2.0" }};
"CB Unix 1" -> "CB Unix 2" -> "CB Unix 3" -> { "Unix/TS++", "PDP-11 Sys V" };
{ "USG 2.0" -> "USG 3.0", "PWB 2.0", "Unix/TS 1.0" } -> "Unix/TS 3.0";
{ "Unix/TS++", "CB Unix 3", "Unix/TS 3.0" } -> "TS 4.0" -> "System V.0" -> "System V.2" -> "System V.3";
]!
```

Will produce this :

![Graph example](http://www.mirari.fr/EbE6)

# Comprehensive list of colors

![Colors](http://www.mirari.fr/VUmg)

# mdbg2tex help
```
mdbg2tex help

Usage :
    mdbg2tex.py <input> <options> (normal use of the function, provides a fresh .tex document)
    mdbg2tex.py --help (to get this text exactly)

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
```

# pgfmanual

[Here](http://ftp.oleane.net/pub/CTAN/graphics/pgf/base/doc/pgfmanual.pdf) is a link of a recent and accurate version of pgf-tikz manual.

It is used for trees and graphs in Markdown BG.
