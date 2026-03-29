#!/usr/bin/env python3
"""regex_engine - Simple regex engine via NFA construction."""
import sys

class State:
    _id = 0
    def __init__(self):
        State._id += 1
        self.id = State._id
        self.transitions = {}  # char -> [State]
        self.epsilon = []
        self.accepting = False

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept
        accept.accepting = True

def char_nfa(c):
    s, a = State(), State()
    s.transitions[c] = [a]
    return NFA(s, a)

def concat_nfa(n1, n2):
    n1.accept.accepting = False
    n1.accept.epsilon.append(n2.start)
    return NFA(n1.start, n2.accept)

def alt_nfa(n1, n2):
    s, a = State(), State()
    s.epsilon = [n1.start, n2.start]
    n1.accept.accepting = False
    n2.accept.accepting = False
    n1.accept.epsilon.append(a)
    n2.accept.epsilon.append(a)
    return NFA(s, a)

def star_nfa(n):
    s, a = State(), State()
    s.epsilon = [n.start, a]
    n.accept.accepting = False
    n.accept.epsilon = [n.start, a]
    return NFA(s, a)

def plus_nfa(n):
    s, a = State(), State()
    s.epsilon = [n.start]
    n.accept.accepting = False
    n.accept.epsilon = [n.start, a]
    return NFA(s, a)

def opt_nfa(n):
    s, a = State(), State()
    s.epsilon = [n.start, a]
    n.accept.accepting = False
    n.accept.epsilon.append(a)
    return NFA(s, a)

def parse_regex(pattern):
    pos = [0]
    
    def parse_alt():
        left = parse_concat()
        while pos[0] < len(pattern) and pattern[pos[0]] == '|':
            pos[0] += 1
            right = parse_concat()
            left = alt_nfa(left, right)
        return left
    
    def parse_concat():
        nodes = []
        while pos[0] < len(pattern) and pattern[pos[0]] not in '|)':
            nodes.append(parse_quantifier())
        if not nodes:
            s, a = State(), State()
            s.epsilon.append(a)
            return NFA(s, a)
        result = nodes[0]
        for n in nodes[1:]:
            result = concat_nfa(result, n)
        return result
    
    def parse_quantifier():
        node = parse_atom()
        if pos[0] < len(pattern):
            if pattern[pos[0]] == '*':
                pos[0] += 1; return star_nfa(node)
            elif pattern[pos[0]] == '+':
                pos[0] += 1; return plus_nfa(node)
            elif pattern[pos[0]] == '?':
                pos[0] += 1; return opt_nfa(node)
        return node
    
    def parse_atom():
        if pos[0] >= len(pattern):
            s, a = State(), State()
            s.epsilon.append(a)
            return NFA(s, a)
        c = pattern[pos[0]]
        if c == '(':
            pos[0] += 1
            node = parse_alt()
            if pos[0] < len(pattern) and pattern[pos[0]] == ')':
                pos[0] += 1
            return node
        elif c == '.':
            pos[0] += 1
            s, a = State(), State()
            s.transitions['.'] = [a]
            return NFA(s, a)
        elif c == '\\' and pos[0]+1 < len(pattern):
            pos[0] += 2
            return char_nfa(pattern[pos[0]-1])
        else:
            pos[0] += 1
            return char_nfa(c)
    
    return parse_alt()

def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        s = stack.pop()
        for e in s.epsilon:
            if e not in closure:
                closure.add(e)
                stack.append(e)
    return closure

def match(pattern, text):
    nfa = parse_regex(pattern)
    current = epsilon_closure({nfa.start})
    
    for c in text:
        next_states = set()
        for state in current:
            if c in state.transitions:
                next_states.update(state.transitions[c])
            if '.' in state.transitions:
                next_states.update(state.transitions['.'])
        current = epsilon_closure(next_states)
    
    return any(s.accepting for s in current)

def search(pattern, text):
    """Find first (longest) match position."""
    for i in range(len(text)):
        last_match = None
        for j in range(i, len(text)+1):
            if match(pattern, text[i:j]):
                last_match = (i, j, text[i:j])
        if last_match:
            return last_match
    return None

def test():
    assert match("abc", "abc")
    assert not match("abc", "abd")
    assert match("a.c", "abc")
    assert match("a.c", "axc")
    assert match("ab*c", "ac")
    assert match("ab*c", "abbc")
    assert match("ab+c", "abc")
    assert match("ab+c", "abbc")
    assert not match("ab+c", "ac")
    assert match("ab?c", "ac")
    assert match("ab?c", "abc")
    assert match("a|b", "a")
    assert match("a|b", "b")
    assert not match("a|b", "c")
    assert match("(ab)+", "abab")
    assert match("(a|b)*", "aabba")
    assert match("(a|b)*", "")
    
    r = search("b+", "aabbbcc")
    assert r == (2, 5, "bbb")
    
    print("All tests passed!")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test()
    elif len(sys.argv) > 2:
        pat, text = sys.argv[1], sys.argv[2]
        print(f"Match: {match(pat, text)}")
        r = search(pat, text)
        if r:
            print(f"Found at {r[0]}:{r[1]}: '{r[2]}'")
    else:
        print("Usage: regex_engine.py <pattern> <text>")
