#!/usr/bin/env python3
"""regex_engine - Simple regex engine built from scratch (NFA-based)."""
import sys

class State:
    def __init__(self, is_end=False): self.is_end=is_end; self.transitions={}; self.epsilon=[]

def char_nfa(c):
    s,e=State(),State(True); s.transitions[c]=[e]; return s,e

def concat(a,b):
    a[1].is_end=False; a[1].epsilon.append(b[0]); return a[0],b[1]

def union(a,b):
    s=State(); s.epsilon=[a[0],b[0]]
    e=State(True); a[1].is_end=False; b[1].is_end=False
    a[1].epsilon.append(e); b[1].epsilon.append(e)
    return s,e

def star(a):
    s=State(); e=State(True)
    s.epsilon=[a[0],e]; a[1].is_end=False
    a[1].epsilon=[a[0],e]
    return s,e

def parse(pattern):
    i=[0]
    def expr():
        t=term()
        while i[0]<len(pattern) and pattern[i[0]]=='|':
            i[0]+=1; t=union(t,term())
        return t
    def term():
        f=factor()
        while i[0]<len(pattern) and pattern[i[0]] not in '|)':
            f=concat(f,factor())
        return f
    def factor():
        b=base()
        while i[0]<len(pattern) and pattern[i[0]] in '*+?':
            if pattern[i[0]]=='*': b=star(b)
            elif pattern[i[0]]=='+': b2=star((State(),State(True))); b2[0].epsilon=[b[0]]; b=concat(b,(b2[0],b2[1]))  # simplified
            i[0]+=1
        return b
    def base():
        if i[0]<len(pattern) and pattern[i[0]]=='(':
            i[0]+=1; e=expr(); i[0]+=1; return e
        if i[0]<len(pattern) and pattern[i[0]]=='.':
            i[0]+=1; s,e=State(),State(True)
            for c in range(32,127): s.transitions.setdefault(chr(c),[]).append(e)
            return s,e
        c=pattern[i[0]]; i[0]+=1; return char_nfa(c)
    return expr()

def epsilon_closure(states):
    stack=list(states); result=set(states)
    while stack:
        s=stack.pop()
        for e in s.epsilon:
            if e not in result: result.add(e); stack.append(e)
    return result

def match(nfa_start, text):
    current=epsilon_closure({nfa_start})
    for c in text:
        next_states=set()
        for s in current:
            if c in s.transitions: next_states.update(s.transitions[c])
        current=epsilon_closure(next_states)
        if not current: return False
    return any(s.is_end for s in current)

def main():
    args=sys.argv[1:]
    if len(args)<2 or '-h' in args:
        print("Usage: regex_engine.py PATTERN TEXT [TEXT...]\n  Supports: . * | () concatenation"); return
    pattern=args[0]
    nfa=parse(pattern)
    for text in args[1:]:
        result=match(nfa[0], text)
        print(f"  {'✅' if result else '❌'} /{pattern}/ ~ '{text}'")

if __name__=='__main__': main()
