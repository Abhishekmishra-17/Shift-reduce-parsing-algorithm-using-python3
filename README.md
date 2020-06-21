# Shift-reduce-parsing-algorithm-using-python3

**Shift Reduce** parser attempts for the construction of parse in a similar manner as done in bottom up parsing i.e. the parse tree is constructed from leaves(bottom) to the root(up). A more general form of shift reduce parser is LR parser.
This parser requires some data structures i.e.

1.A input buffer for storing the input string.

2.A stack for storing and accessing the production rules.

# Basic Operations –

**Shift:** This involves moving of symbols from input buffer onto the stack.

**Reduce:** If the handle appears on top of the stack then, its reduction by using appropriate production rule is done i.e. RHS of production rule is popped out of stack and LHS of production rule is pushed onto the stack.

**Accept:** If only start symbol is present in the stack and the input buffer is empty then, the parsing action is called accept. When accept action is obtained, it is means successful parsing is done.

**Error:** This is the situation in which the parser can neither perform shift action nor reduce action and not even accept action.

# About Program--
***main.py** is main program of this repository,and **state.py** and **follow.py** are modules using in **main.py**.

**follow.py** is program for **follow** function,while **state.py** is used for creating the states between the nodes.
