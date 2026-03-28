#!/usr/bin/env python3
"""regex_engine - Regex via Thompson NFA."""
import argparse, sys

class State:
    def __init__(self, label=None):
        self.label = label; self.out = []; self.out2 = []

def compile_regex(pattern):
    """Compile regex pattern to NFA using Thompson construction."""
    frags = []
    i = 0
    def new_state(label=None):
        return State(label)
    while i < len(pattern):
        c = pattern[i]
        if c == "(": frags.append(("LPAREN",)); i += 1; continue
        elif c == ")":
            # concat all since last LPAREN
            stack = []
            while frags and frags[-1] != ("LPAREN",):
                stack.append(frags.pop())
            if frags: frags.pop()  # remove LPAREN
            if stack:
                stack.reverse()
                result = stack[0]
                for s in stack[1:]:
                    result = ("CONCAT", result, s)
                frags.append(result)
            i += 1; continue
        elif c == "|":
            frags.append(("ALT_OP",)); i += 1; continue
        elif c == "*":
            if frags: frags[-1] = ("STAR", frags[-1])
            i += 1; continue
        elif c == "+":
            if frags: frags[-1] = ("PLUS", frags[-1])
            i += 1; continue
        elif c == "?":
            if frags: frags[-1] = ("OPT", frags[-1])
            i += 1; continue
        elif c == ".":
            frags.append(("DOT",)); i += 1; continue
        elif c == "\\" and i+1 < len(pattern):
            frags.append(("CHAR", pattern[i+1])); i += 2; continue
        else:
            frags.append(("CHAR", c)); i += 1; continue
    return frags

def match_nfa(fragments, text):
    """Simple recursive NFA matching."""
    def match_frag(frag, text, pos):
        if frag is None: yield pos; return
        kind = frag[0]
        if kind == "CHAR":
            if pos < len(text) and text[pos] == frag[1]:
                yield pos + 1
        elif kind == "DOT":
            if pos < len(text):
                yield pos + 1
        elif kind == "CONCAT":
            for p in match_frag(frag[1], text, pos):
                yield from match_frag(frag[2], text, p)
        elif kind == "STAR":
            yield pos
            for p in match_frag(frag[1], text, pos):
                if p > pos:
                    yield from match_frag(frag, text, p)
        elif kind == "PLUS":
            for p in match_frag(frag[1], text, pos):
                yield p
                if p > pos:
                    yield from match_frag(("STAR", frag[1]), text, p)
        elif kind == "OPT":
            yield pos
            yield from match_frag(frag[1], text, pos)
    # Build single fragment from list
    combined = None
    for f in fragments:
        if f == ("ALT_OP",): continue
        if combined is None: combined = f
        else: combined = ("CONCAT", combined, f)
    if combined is None: return True, 0, 0
    for start in range(len(text)):
        for end in match_frag(combined, text, start):
            return True, start, end
    return False, -1, -1

def main():
    p = argparse.ArgumentParser(description="Regex engine (Thompson NFA)")
    p.add_argument("pattern")
    p.add_argument("text")
    a = p.parse_args()
    frags = compile_regex(a.pattern)
    found, start, end = match_nfa(frags, a.text)
    if found:
        print(f"Match: \"{a.text[start:end]}\" at [{start}:{end}]")
    else:
        print("No match")

if __name__ == "__main__": main()
