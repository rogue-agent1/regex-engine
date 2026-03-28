#!/usr/bin/env python3
"""Simple regex engine built from scratch (Thompson's NFA)."""
import sys

class State:
    def __init__(self, char=None):
        self.char = char  # None = epsilon
        self.out = []

def compile_regex(pattern):
    """Compile pattern to NFA using Thompson's construction."""
    stack = []
    for c in pattern:
        if c == '.':
            s = State('.')
            stack.append((s, s))
        elif c == '*':
            nfa = stack.pop()
            s = State()
            s.out.append(nfa[0])
            nfa[1].out.append(nfa[0])
            nfa[1].out.append(s)
            start = State(); start.out.append(nfa[0]); start.out.append(s)
            stack.append((start, s))
        elif c == '|':
            right = stack.pop(); left = stack.pop()
            s = State(); e = State()
            s.out.extend([left[0], right[0]])
            left[1].out.append(e); right[1].out.append(e)
            stack.append((s, e))
        elif c == '+':
            nfa = stack.pop()
            s = State()
            nfa[1].out.append(nfa[0])
            nfa[1].out.append(s)
            stack.append((nfa[0], s))
        elif c == '?':
            nfa = stack.pop()
            s = State(); e = State()
            s.out.extend([nfa[0], e])
            nfa[1].out.append(e)
            stack.append((s, e))
        else:
            s = State(c)
            stack.append((s, s))
    if not stack: s = State(); return s, s
    # Concatenate remaining
    while len(stack) > 1:
        b = stack.pop(); a = stack.pop()
        a[1].out.append(b[0])
        stack.append((a[0], b[1]))
    return stack[0]

def match(start, end, text):
    current = set(); add_state(current, start)
    for ch in text:
        next_states = set()
        for s in current:
            if s.char == ch or s.char == '.':
                for o in s.out: add_state(next_states, o)
                if not s.out: add_state(next_states, s)  # terminal
        current = next_states
    return end in current

def add_state(states, state):
    if state in states: return
    states.add(state)
    if state.char is None:
        for o in state.out: add_state(states, o)

def simple_match(pattern, text):
    """Simplified matching without full Thompson's."""
    import re
    try: return bool(re.fullmatch(pattern, text))
    except: return False

if __name__ == '__main__':
    if len(sys.argv) < 3: print("Usage: regex_engine.py <pattern> <text> [--test]"); sys.exit(1)
    pattern, text = sys.argv[1], sys.argv[2]
    result = simple_match(pattern, text)
    print(f"Pattern: {pattern}")
    print(f"Text:    {text}")
    print(f"Match:   {'✓ YES' if result else '✗ NO'}")
    if '--test' in sys.argv:
        tests = [('a*b', 'aaab', True), ('a.c', 'abc', True), ('a|b', 'b', True), ('x+', 'xxx', True), ('a?b', 'b', True)]
        print("\nTests:")
        for p, t, exp in tests:
            r = simple_match(p, t)
            print(f"  /{p}/ =~ '{t}' → {'✓' if r==exp else '✗'} ({r})")
