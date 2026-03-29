#!/usr/bin/env python3
"""regex_engine - NFA regex engine with Thompson's construction."""
import argparse

class State:
    def __init__(self, label=None): self.label=label; self.edges=[]
    def add(self, label, target): self.edges.append((label, target))

def parse(pattern):
    """Convert regex pattern to postfix with explicit concat '.'"""
    output=[]; ops=[]; i=0; prev_atom=False
    while i<len(pattern):
        c=pattern[i]
        if c=='(':
            if prev_atom: ops.append('.')
            ops.append(c); prev_atom=False
        elif c==')':
            while ops and ops[-1]!='(': output.append(ops.pop())
            if ops: ops.pop()
            prev_atom=True
        elif c in '*+?':
            output.append(c); prev_atom=True
        elif c=='|':
            while ops and ops[-1]=='.': output.append(ops.pop())
            ops.append(c); prev_atom=False
        elif c=='\\' and i+1<len(pattern):
            if prev_atom: ops.append('.')
            i+=1; output.append(('lit',pattern[i])); prev_atom=True
        else:
            if prev_atom: ops.append('.')
            output.append(('lit',c)); prev_atom=True
        i+=1
    while ops: output.append(ops.pop())
    return output

def build_nfa(postfix):
    stack=[]
    for token in postfix:
        if isinstance(token, tuple) and token[0]=='lit':
            s,e=State(),State(); s.add(token[1],e); stack.append((s,e))
        elif token=='.':
            b=stack.pop(); a=stack.pop(); a[1].add(None,b[0]); stack.append((a[0],b[1]))
        elif token=='|':
            b=stack.pop(); a=stack.pop(); s,e=State(),State()
            s.add(None,a[0]); s.add(None,b[0]); a[1].add(None,e); b[1].add(None,e)
            stack.append((s,e))
        elif token=='*':
            a=stack.pop(); s,e=State(),State()
            s.add(None,a[0]); s.add(None,e); a[1].add(None,a[0]); a[1].add(None,e)
            stack.append((s,e))
        elif token=='+':
            a=stack.pop(); s,e=State(),State()
            s.add(None,a[0]); a[1].add(None,a[0]); a[1].add(None,e)
            stack.append((s,e))
        elif token=='?':
            a=stack.pop(); s,e=State(),State()
            s.add(None,a[0]); s.add(None,e); a[1].add(None,e)
            stack.append((s,e))
    return stack[0] if stack else (State(),State())

def epsilon_closure(states):
    stack=list(states); result=set(states)
    while stack:
        s=stack.pop()
        for label,target in s.edges:
            if label is None and target not in result: result.add(target); stack.append(target)
    return result

def match(nfa_start, nfa_end, text):
    current=epsilon_closure({nfa_start})
    for c in text:
        next_states=set()
        for s in current:
            for label,target in s.edges:
                if label==c or label=='.': next_states.add(target)
        current=epsilon_closure(next_states)
        if not current: return False
    return nfa_end in current

def main():
    p=argparse.ArgumentParser(description="NFA regex engine")
    p.add_argument("pattern"); p.add_argument("text",nargs="?")
    p.add_argument("--test",action="store_true")
    args=p.parse_args()
    if args.test:
        tests=[("a*b","b",True),("a*b","aab",True),("a*b","aa",False),("(a|b)*c","abac",True),("ab+c","ac",False),("ab+c","abbc",True)]
        for pat,txt,exp in tests:
            pf=parse(pat); nfa=build_nfa(pf); r=match(nfa[0],nfa[1],txt)
            status="✓" if r==exp else "✗"
            print(f"  {status} /{pat}/ vs '{txt}' -> {r}")
        return
    postfix=parse(args.pattern); nfa=build_nfa(postfix)
    if args.text:
        r=match(nfa[0],nfa[1],args.text)
        print(f"/{args.pattern}/ {'matches' if r else 'does not match'} '{args.text}'")
    else:
        print(f"NFA built for /{args.pattern}/ — provide text to match")

if __name__=="__main__":
    main()
