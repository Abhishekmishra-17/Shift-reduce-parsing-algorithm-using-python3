from follow import follow_pos
from state import *
from numpy import nan
from pandas import DataFrame as df, MultiIndex


states = []
parsing_table = df()

def grammar_fromstr(g):
    '''1 split each line
    2 separate LHS from RHS
    3 split HRSs i.e.: X => Y | Z
    4 for each RHS r, make a rule LHS => r
    '''
    grm = g.split('\n')
    rules = []
    for r in grm:
        if r.strip()=='':continue # skip empty lines
        lhs, rhs_ls = r.split('=>')
        for rhs in rhs_ls.split('|'):
            rules.append((lhs.strip(),rhs.strip().split()))
    return rules

def augment(grammar_str):
    '''
    - Rules must be in form LHS => RHS
    - NONTERMINALS must start with (`) and be UPPERCASE. use only [A-Z] and (_) for NONTERMINALS
    - Terminals must be lower case
    - If there are many rhs for one lhs, you should put them all in the same line and separate them with (|) i.e: X => Y | Z | !εpslon
    - Use the form (!εpslon) for writing epslons 
    '''
    grammar= grammar_fromstr(grammar_str)
    rhs = [grammar[0][0]] # The start symbol
    aug=Rule(grammar[0][0]+"'", tuple(rhs))
    s = State()
    s.add_rule(aug)
    Rule.augmented.append(aug)
    for r in grammar:
        Rule.augmented.append(Rule(r[0],r[1]))
    return s, extract_symbols(grammar)

def extract_symbols(rules):
    terminals = []
    non_terminals = []
    for r in rules:
        if r[0] not in non_terminals:
            non_terminals.append(r[0])
        for s in r[1]:
            if not s.startswith('`'):
                if s not in terminals:
                    if s != '!εpslon':
                        terminals.append(s)
            else:
                if s not in non_terminals:
                    non_terminals.append(s)
    terminals.append('$')
    return (non_terminals, terminals)

def goto_operation():
    #s = states[0]
    for s in states:
        transitions = []
        for r in  s.rules:
            rule = r.movedot()
            dotatend = rule == None
            if dotatend:
                continue
            transitions.append((r.handle(), rule))
        
        # If a new transition item is already in the current state, make a cycle
        gotoself(transitions, s)
        
        for t in transitions:

            # Put all items with the same Transition symbol in one state
            items_same_X = [r for r in transitions if r[0] == t[0]]
            make_transition(s, items_same_X) 
    return State.graph

def gotoself(transitions, s):
    # If a new transition is already in the current state, make a cycle
    for t in transitions:
        if t[1] in s.rules:
            s.goto( s._i, t[0])
            transitions.remove(t)

def make_transition(source, items_same_X):
    new_state = newstate(items_same_X)
    ### exists
    # If new Items I alraedy there in a state s, goto s
    # Else, make a new state Si of I 
    exists = False
    for s in states:
        if new_state == s:
            source.goto(s._i, symbol=items_same_X[0][0])
            exists=True
            State._count = State._count-1
            break
    ###
    if not exists:
        new_state.closure()
        states.append(new_state)
        source.goto(new_state._i, symbol=items_same_X[0][0])

def newstate(items_same_X):
    new_state = State()
    for r in items_same_X:
        new_state.add_rule(r[1])
    return new_state

def parsing_table_skelton(non_terminals, terminals):
    levels = (['action']*len(terminals) + ['goto']*len(non_terminals))
    columns = terminals+non_terminals
    index = [s._i for s in states]
    return df(index=index, columns=MultiIndex.from_tuples(list(zip(levels,columns)),names=['table','symbol'])).fillna('_')

def slr_parsing_table(items):
    global parsing_table
    for i in items:
        isterminal = not i[2].startswith('`')
        if isterminal: # Shift

            cell = parsing_table.loc[(i[0]), ('action', i[2])]
            if cell !='_':
                print('conflict: '+ cell + '    s'+str(i[1]))
                continue
            parsing_table.loc[(i[0]), ('action', i[2])] = 's'+str(i[1])
        else: # goto
            parsing_table.loc[(i[0]), ('goto', i[2])] = i[1]
    # reduce
    n = Rule._n # grammar rules start index
    reduce = [(s.rules[0].lhs, s._i, Rule.augmented.index(s.rules[0].copy())) for s in states if s.hasreduce]
    for r in reduce:
        
        if r[0].endswith("'"):
            parsing_table.loc[(r[1]), ('action', '$')] = 'accept'
        else:
            for f in follow_pos(r[0]):
                cell = parsing_table.loc[(r[1]), ('action', f)]
                if cell !='_':
                    print('conflict: '+cell + '    r'+str(r[2]+n))
                parsing_table.loc[(r[1]), ('action', f)] = 'r'+str(r[2]+n)

def moves(s):
    snap=[]
    stack = [('$',State._n)]
    input_ = s.split()+['$']
    action = []

    while True:
        a = parsing_table.loc[(stack[-1][1]), ('action', input_[0])]
        action.append(a)
        snap.append((''.join([s[0]+str(s[1]) for s in stack]), ' '.join(input_)))

        if a == 'accept':
            print ('Driver: accept')
            break
        #Shift
        if a.startswith('s'):
            stack.append((input_[0],int(''.join(a[1:]))))
            input_.remove(input_[0])
        #Reduce
        elif a.startswith('r'):
            r = Rule.augmented[(int(''.join(a[1:])))]
            for _ in range(len(r.rhs)):
                stack.pop()
            goto = parsing_table.loc[(stack[-1][1]), ('goto', r.lhs)]
            stack.append((r.lhs, goto))
            action[-1] = ' '.join([a,'goto:'+str(goto), str(r).replace(' • ', ' ')])
        else:
            print('Driver: Syntax error')
            break
    return df(data=list(zip([s[0] for s in snap],[s[1]for s in snap],action)) ,columns=('Stack','Input','Action'))

'''def draw(graph):
    import networkx
    import matplotlib.pyplot as plt
    print('pygraphviz is required to draw cycles(state goes to itself) if exists')
    
    n = State._n # offset to subtract from state _i in graph[] when indexing states[]
    g = networkx.DiGraph(directed=True)
    g.add_edges_from([(str(states[e[0]-n]), str(states[e[1]-n])) for e in graph])
    pos = networkx.circular_layout(g)
    plt.figure()
    networkx.draw(g,pos,labels={node:node for node in g.nodes()}, node_size=5500,node_color='white',node_shape='s',font_family='Consolas',font_size=9) # select a monospace font
    networkx.draw_networkx_edge_labels(g,pos,edge_labels={(str(states[e[0]-n]), str(states[e[1]-n])):e[2] for e in graph})
    plt.show()
'''
def run(grammar):
    global parsing_table
    start_state, symbols = augment(grammar)
    start_state.closure()
    states.append(start_state)
    items = goto_operation()
    parsing_table =  parsing_table_skelton(symbols[0], symbols[1])
    slr_parsing_table(items)
    return items


def test(grammar, test_string):
    states_graph = run(grammar)
    for s in states:
        print(s, end='\n')

   # draw(states_graph)

    print(parsing_table)

    driver_table = moves(test_string) # lexemes of test_string  must separated with spaces
    print(driver_table)

if __name__ == '__main__':
    print(augment.__doc__)
    g4 = """`E => `E + `T
    `E => `T 
    `T => `T * `F 
    `T => `F 
    `F => ( `E ) 
    `F => id"""

    print(g4, end='\n------grammar------\n\n')
    test(g4, 'id + id * id')
