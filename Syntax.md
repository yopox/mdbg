# Markdown flavoured by BGs
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

For non enuerated section :
```mdbg
#* H1
##* H2
###* H3
####* H4
#####* H5
######* H6
```


### Emphasis

Transaltions :

#### Bold
In markdown :
```no-highlight
Bold : this is *bold*
```
```mdbg
Bold : this is *bold*
```

#### Underscore

```mdbg
Underline : this is _underline_
```

#### Italic
In markdown :

```no-highlight
Italic : This is __italic__
```
```mdbg
Italic : This is %italic%
```

#### Scratch
In markdown :

```no-highlight
Scratch : this is ~~scratch~~
```
```mdbg
Scratch : this is ~scratch~
```

### Lists

Small changes.

This is a list :

```mdbg
Neutral text :
  first item
  second item
    first second item
    second second item
  third item
```

and an enumerated list
```mdbg
  1. first item
  2. second item
    1. first second item
    2. second second item
  3. third item
```

### Links

```mdbg
[text for link](https://www.google.com)

[text for link](https://www.google.com "title for link")
```

### Code

Like Markdown.

### Tables

Like Markdown, without 2nd line.

```mdbg
| C11 | C21 | C31 |
| C21 | C22 | C32 |
| C31 | C32 | C33 |
```

In Markdown :

```no-highlight
| C11 | C21 | C31 |
| --- | --- | --- |
| C21 | C22 | C32 |
| C31 | C32 | C33 |
```

## New !

### Trees :

#### Basic binary tree

Description :
  - Command : `![TREE]!`
  - Root : `R "text"`
  - Node : `N "text"`
  - Leave : `L "text"`

```mdbg
![TREE R "root" N "a node" L "a leave" L "an other leave" N "an other node" L "a leave again !" N "a node again !" L  "OneWord" L "the last leave"]!
```

##### Non binary trees

Command : `![nTREE]!`

```mdbg
![nTREE "A" -- {"B" -- {"H" -- {"N", "O"}, "I", "J"}, "C", "D", "E" -- {"K" -- "P", "L" -- "Q"}, "F", "G" -- "M"}]!
```

##### Centering

Command : `![c-TREE]!`

```mdbg
![nTREE "A" -- {"B" -- {"H" -- {"N", "O"}, "I", "J"}, "C", "D", "E" -- {"K" -- "P", "L" -- "Q"}, "F", "G" -- "M"}]!
```
