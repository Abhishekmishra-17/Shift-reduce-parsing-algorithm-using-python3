# Symbol: {name} 
# Symbols table : { {name} {type:0=terminal / 1=non-terminal} }
# Rule: {LHS} {RHS: sequence of symbol names} {index of ·} {0=not visited / 1=visited}
# state: {index} {Rules} {leaf}
# Transitions graph: {List: {index of Source State} {index of Distination State} {transition symbol}}

class State:
    _n=0 # start index of states (made to change manually here)
    _count=0+_n
    graph=[]

    def __init__(self):
        self.rules = []
        self._i = State._count
        self.hasreduce=0 # The state has a rule to reduce
        State._count = State._count+1
    
    def add_rule(self, rule):
        '''add new rule to the state'''
        if rule not in self.rules:
            self.rules.append(rule)
            if rule._closure==-1:
                self.hasreduce=1
    
    def goto(self, distination_index, symbol):
        '''
        add a transition -with a symbol, between a state and its successor 
        '''
        
        g = [self._i, distination_index, symbol]
        if g not in State.graph:
            State.graph.append(g)
    
    def closure(self): # closure operation
        for rule in self.rules:
            if rule.visited:
                continue
            for r in rule.visit():
                if r not in self.rules:
                    self.add_rule(r)

    def __eq__(self, s):
        "If self rules in s rules"
        if not isinstance(s, State):
            # don't attempt to compare against unrelated types
            # https://stackoverflow.com/a/1227325
            return NotImplemented
        eq = True
        if self.rules.__len__() > s.rules.__len__():
            return False
        for r in self.rules:
            eq = eq and (r in s.rules)
        return eq

    def __str__(self):
        s = []
        max_len=1
        for r in self.rules:
            line='    ['+str(r)
            s.append(line)
            if len(line) > max_len: max_len=len(line)
        # make all line with the same length
        for i in range(len(s)):
            pad = max_len-len(s[i])
            s[i]=s[i]+' '*pad+']'
        s.insert(0,''.join(['I',str(self._i),':',' '*(max_len-2)]))        
        return '\n'.join(s)

class Rule:
    _n=0 # start index of augmented grammar
    augmented = []
    def __init__(self, lhs, rhs=[], dot_index=0):
        self.lhs = lhs
        if rhs == ['!εpslon']:
            self.rhs=[]
        else:
            self.rhs = rhs
        self._closure = dot_index
        
        if self.dotatend():
            self._closure = -1
        
        self.visited = 0

    def __str__(self):
        rhs = list(self.rhs)
        dot = self._closure
        if dot == -1:
            dot = len(rhs)
        rhs.insert(dot, '•')
        return self.lhs + ' → ' + ' '.join(rhs)

    def __eq__(self, rule):
        if not isinstance(rule, Rule):
            # don't attempt to compare against unrelated types
            # https://stackoverflow.com/a/1227325
            return NotImplemented
        return self.lhs == rule.lhs and self.rhs == rule.rhs and self._closure == rule._closure

    def handle(self):
        return self.rhs[self._closure]

    def visit(self):
        '''
        Mark rule as visited and expand in their state
        '''
        self.visited = 1
        # If dot is not at the end of rule and is a handle(non-terminal)
        if self._closure != -1:
            handle =  self.rhs[self._closure]
            if handle.startswith('`'):
                return [r.copy() for r in Rule.augmented if r.lhs == handle]
        return []
        
    def dotatend(self):
        '''
        checks if we reachs the end if the rule
        '''
        if self._closure == len(self.rhs):
            return True
        return False

    def movedot(self):
        '''
        move the . closure and return a new rule for a new state
        '''
        if self._closure == -1:
            return None
        return Rule(self.lhs, self.rhs, self._closure + 1)
    
    def copy(self):
        '''ignore colsure and visited attributes'''
        return Rule(self.lhs,self.rhs)
