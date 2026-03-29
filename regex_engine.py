#!/usr/bin/env python3
"""Simple regex engine supporting . * + ? | () from scratch."""
import sys

class State:
    def __init__(self): self.transitions = []; self.epsilon = []

def char_match(c):
    s, e = State(), State()
    s.transitions.append((c, e))
    return s, e

def dot_match():
    s, e = State(), State()
    s.transitions.append((".", e))
    return s, e

def concat(a, b):
    a[1].epsilon.append(b[0])
    return a[0], b[1]

def alt(a, b):
    s, e = State(), State()
    s.epsilon.extend([a[0], b[0]])
    a[1].epsilon.append(e); b[1].epsilon.append(e)
    return s, e

def star(a):
    s, e = State(), State()
    s.epsilon.extend([a[0], e])
    a[1].epsilon.extend([a[0], e])
    return s, e

def plus(a):
    s, e = State(), State()
    s.epsilon.append(a[0])
    a[1].epsilon.extend([a[0], e])
    return s, e

def opt(a):
    s, e = State(), State()
    s.epsilon.extend([a[0], e])
    a[1].epsilon.append(e)
    return s, e

def parse_regex(pattern):
    pos = [0]
    def expr():
        t = term()
        while pos[0] < len(pattern) and pattern[pos[0]] == "|":
            pos[0] += 1; t = alt(t, term())
        return t
    def term():
        f = None
        while pos[0] < len(pattern) and pattern[pos[0]] not in "|)":
            a = atom()
            if pos[0] < len(pattern) and pattern[pos[0]] == "*": pos[0] += 1; a = star(a)
            elif pos[0] < len(pattern) and pattern[pos[0]] == "+": pos[0] += 1; a = plus(a)
            elif pos[0] < len(pattern) and pattern[pos[0]] == "?": pos[0] += 1; a = opt(a)
            f = concat(f, a) if f else a
        return f or char_match("")
    def atom():
        if pattern[pos[0]] == "(":
            pos[0] += 1; e = expr()
            if pos[0] < len(pattern) and pattern[pos[0]] == ")": pos[0] += 1
            return e
        elif pattern[pos[0]] == ".":
            pos[0] += 1; return dot_match()
        else:
            c = pattern[pos[0]]; pos[0] += 1; return char_match(c)
    return expr()

def epsilon_closure(states):
    stack = list(states); result = set(states)
    while stack:
        s = stack.pop()
        for e in s.epsilon:
            if e not in result: result.add(e); stack.append(e)
    return result

def match(pattern, text):
    if not pattern: return True
    nfa = parse_regex(pattern)
    current = epsilon_closure({nfa[0]})
    for c in text:
        next_s = set()
        for s in current:
            for tc, dest in s.transitions:
                if tc == c or tc == ".": next_s.add(dest)
        current = epsilon_closure(next_s)
        if not current: return False
    return nfa[1] in current

def main():
    if len(sys.argv) < 3:
        print("Usage: regex_engine.py <pattern> <text>"); return
    p, t = sys.argv[1], sys.argv[2]
    r = match(p, t)
    print(f"/{p}/ {'matches' if r else 'does not match'} \"{t}\"")

if __name__ == "__main__": main()
