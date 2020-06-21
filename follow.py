from state import Rule


_first = {}
_follow = {}
def first_pos(symbol):
    first = set()
    if not symbol.startswith('`'):
        return set([symbol])
    
    for r in [i for i in Rule.augmented if i.lhs == symbol]:
        whole_rhs_has_e = True
        for s in r.rhs:
            has_e=False
            for f in first_pos(s):
                if f == '!εpslon':
                    has_e=True
                else:
                    first.add(f)
            if not has_e:
                whole_rhs_has_e=False
                break
        if whole_rhs_has_e:
            first.add('!εpslon')
    global _first
    _first[symbol]=list(first)
    return list(first)

def follow_pos(symbol, A=None):
    follow = set()
    if symbol.endswith("'"):
        follow.add('$')
    for r in [i for i in Rule.augmented if symbol in i.rhs]:
        occurences = r.rhs.count(symbol) # if symbol appears many time in a rule
        # B --> a A
        if symbol == r.rhs[-1]:
            if symbol != r.lhs and A != r.lhs: # (to prevent this problem X => Y , Y => X , and i want follow(y))
                for f in follow_pos(r.lhs, symbol):
                    follow.add(f)
            continue
        # (B --> a A Beta)
        beta = r.rhs
        for i in range(occurences):
            j=beta.index(symbol)
            beta = r.rhs[j+1:]
            s=beta[0]
            f = first_pos(s)
            for f1 in f:
                if f1 == '!εpslon':
                    if symbol == r.lhs or A == r.lhs: continue # don't repeat yourself
                    for f2 in follow_pos(r.lhs, symbol):
                        follow.add(f2)
                else:
                    follow.add(f1)  
    global _follow
    _follow[symbol]=list(follow)          
    return follow

def test_frstfllw(symbols):
    c=[]
    for s in symbols:
        f = first_pos(s)
        fo = follow_pos(s)
        c.append([s,' '.join(f),' '.join(fo)])
    return c
