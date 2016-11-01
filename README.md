# Markdown flavoured by BGs

# Markdown BG presentation
Mardown BG (_.mdbg_) is an improvement of the existing [Mardown](https://fr.wikipedia.org/wiki/Markdown) language.

It provides some more functionnalities and syntaxes which make it possible to generate a fresh, correct and nice _.tex_ document.

# Syntax

## Markdown flavoured

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
Bold : this is **bold** or __bold__
```

In mdbg :

```mdbg
Bold : this is *bold*
```

#### Underscore

```mdbg
Underline : this is _underline_
```

#### Italic

In markdown :

```md
Italic : This is _italic_ or *italic*
```

In mdbg :

```mdbg
Italic : This is %italic%
```

#### Strikethrough

In markdown :

```md
Strikethrough : this is ~~strikethrough~~
```

In mdbg :

```mdbg
Strikethrough : this is ~strikethrough~
```

### Lists

Small changes.

This is a list in mdbg :

```mdbg
Neutral text :
    - first item
    - second item
        - first second item
        - second second item
    - third item
```

and an enumerated list

```mdbg
    1. first item
    2. second item
        1. first second item
        2. second second item
    3. third item
```

The indentations can be whether four spaces or a tabulation but every item has to be idented even the first.

### Links

```mdbg
[text for link](https://www.google.com)

[text for link](https://www.google.com "title for link")
```

### Code

Like in Markdown.

### Tables

Like Markdown, without 2nd line.

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

### Miscellaneous

By default, no indentation will be added when you begin a new line or next to a section definition.

You can add one by putting whether four spaces or a tabulation at the begining of the line.

A line break will add a `\\` or `\newline` in the LaTeX generated file.

Those three changes bring more strictness compared to simple Markdown but it will allow you to decide everything you want about your layout.

# Examples

## Trees

This line : `![TREE R 1 N 2 F 3 F 4 F 5]!`; will be converted to some LaTeX wich will look like this :

![Binary tree](http://www.mirari.fr/ShRU)

This line : `![nTREE A -- {B -- {H -- {N, O}, I, J}, C, D, E -- {K -- P, L -- Q}, F, G -- M}]!`; will be converted to some LaTeX wich will look like this :

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

    -l : shortcut for --lua
    --lua : put this option if you are intending to compile your .tex document with LuaLaTeX or not. It is automatically set to True if there are trees in your document.
```
