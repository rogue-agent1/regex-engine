#!/usr/bin/env python3
"""Simple regex engine (Thompson NFA construction)."""
import sys
class State:
    def __init__(self,c=None): self.c,self.out,self.out1=c,[],[]
class NFA:
    def __init__(self,start,end): self.start,self.end=start,end
def char_nfa(c):
    s,e=State(c),State(); s.out=[e]; return NFA(s,e)
def concat(a,b):
    a.end.out=[b.start]; return NFA(a.start,b.end)
def alt(a,b):
    s,e=State(),State()
    s.out=[a.start]; s.out1=[b.start]
    a.end.out=[e]; b.end.out=[e]
    return NFA(s,e)
def star(a):
    s,e=State(),State()
    s.out=[a.start,e]; a.end.out=[a.start,e]
    return NFA(s,e)
def compile_re(pattern):
    stack=[]
    for c in pattern:
        if c=='*': stack.append(star(stack.pop()))
        elif c=='|': b,a=stack.pop(),stack.pop(); stack.append(alt(a,b))
        elif c=='.':
            if len(stack)>=2: b,a=stack.pop(),stack.pop(); stack.append(concat(a,b))
        else: stack.append(char_nfa(c))
    while len(stack)>1: b,a=stack.pop(),stack.pop(); stack.append(concat(a,b))
    return stack[0] if stack else None
def match(nfa,text):
    current={nfa.start}
    def expand(states):
        result,work=set(),list(states)
        while work:
            s=work.pop()
            if s in result: continue
            result.add(s)
            if s.c is None:
                work+=s.out+s.out1
        return result
    current=expand(current)
    for c in text:
        nxt=set()
        for s in current:
            if s.c==c or s.c=='.': nxt.update(s.out)
        current=expand(nxt)
    return nfa.end in current
if len(sys.argv)<3: sys.exit("Usage: regex_engine <pattern> <text>")
nfa=compile_re(sys.argv[1])
print(f"Match: {match(nfa, sys.argv[2])}")
