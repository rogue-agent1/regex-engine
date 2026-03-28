#!/usr/bin/env python3
"""Pure Python regex engine (Thompson NFA)."""
class State:
    def __init__(self,char=None,out1=None,out2=None):
        self.char=char;self.out1=out1;self.out2=out2
class NFA:
    def __init__(self,start,accept): self.start=start;self.accept=accept
def char_nfa(c):
    accept=State(); start=State(c,accept); return NFA(start,accept)
def concat(a,b):
    a.accept.out1=b.start; a.accept.char=None; return NFA(a.start,b.accept)
def union(a,b):
    accept=State(); start=State(None,a.start,b.start)
    a.accept.out1=accept; b.accept.out1=accept
    return NFA(start,accept)
def star(a):
    accept=State(); start=State(None,a.start,accept)
    a.accept.out1=a.start; a.accept.out2=accept
    return NFA(start,accept)
def plus(a):
    accept=State(); start=State(None,a.start)
    a.accept.out1=a.start; a.accept.out2=accept
    return NFA(start,accept)
def question(a):
    accept=State(); start=State(None,a.start,accept)
    a.accept.out1=accept
    return NFA(start,accept)
def parse_regex(pattern):
    stack=[]; i=0
    while i<len(pattern):
        c=pattern[i]
        if c=="(": stack.append("(")
        elif c==")":
            group=[]
            while stack and stack[-1]!="(": group.append(stack.pop())
            if stack: stack.pop()
            if group:
                r=group[-1]
                for g in reversed(group[:-1]): r=concat(r,g)
                stack.append(r)
        elif c=="|":
            stack.append("|")
        elif c=="*":
            if stack and not isinstance(stack[-1],str): stack.append(star(stack.pop()))
        elif c=="+":
            if stack and not isinstance(stack[-1],str): stack.append(plus(stack.pop()))
        elif c=="?":
            if stack and not isinstance(stack[-1],str): stack.append(question(stack.pop()))
        elif c==".": stack.append(char_nfa("."))
        else: stack.append(char_nfa(c))
        i+=1
    while "|" in stack:
        idx=stack.index("|")
        left=stack[idx-1]; right=stack[idx+1]
        stack[idx-1:idx+2]=[union(left,right)]
    if stack:
        r=stack[0]
        for s in stack[1:]:
            if not isinstance(s,str): r=concat(r,s)
        return r
    return char_nfa("")
def add_state(s,states,visited):
    if s is None or id(s) in visited: return
    visited.add(id(s))
    if s.char is None:
        add_state(s.out1,states,visited); add_state(s.out2,states,visited)
    else: states.add(s)
def match(pattern,text):
    nfa=parse_regex(pattern)
    current=set(); add_state(nfa.start,current,set())
    for ch in text:
        next_s=set()
        for s in current:
            if s.char==ch or s.char==".":
                ns=set(); add_state(s.out1,ns,set()); next_s|=ns
        current=next_s
    return nfa.accept in current
if __name__=="__main__":
    tests=[("abc","abc",True),("a.c","axc",True),("ab*c","ac",True),("ab*c","abbc",True),("a|b","a",True),("a|b","c",False)]
    ok=True
    for p,t,exp in tests:
        r=match(p,t)
        if r!=exp: print(f"FAIL: /{p}/ vs '{t}': got {r}"); ok=False
    if ok: print("All regex engine tests passed")
