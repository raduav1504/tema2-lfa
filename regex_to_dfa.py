import json
import sys
from collections import defaultdict, deque

# ------------------ Regex to Postfix (Shunting-Yard) ------------------

def regex_to_postfix(regex):
    """
    Convert infix regex to postfix notation using Shunting-Yard algorithm.
    Supports operators: |, *, +, ?, concatenation (implicit).
    """
    # Define operator precedence
    prec = {'*': 3, '+': 3, '?': 3, '.': 2, '|': 1}
    output = []
    stack = []
    # Insert explicit concatenation operator '.'
    new_regex = []
    prev = None
    for c in regex:
        if c == ' ':
            continue
        if prev is not None and (prev not in '(|' and c not in '|)*+?'):
            new_regex.append('.')
        new_regex.append(c)
        prev = c
    # Shunting-yard
    for token in new_regex:
        if token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # pop '('
        elif token in prec:
            while stack and stack[-1] != '(' and prec.get(stack[-1], 0) >= prec[token]:
                output.append(stack.pop())
            stack.append(token)
        else:
            output.append(token)
    while stack:
        output.append(stack.pop())
    return ''.join(output)

# ------------------ NFA Construction (Thompson) ------------------

class State:
    def __init__(self):
        self.edges = defaultdict(list)  # symbol -> list of states

class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept


def thompson(postfix):
    stack = []  # stack of NFA

    def char_nfa(c):
        s1, s2 = State(), State()
        s1.edges[c].append(s2)
        return NFA(s1, s2)

    for token in postfix:
        if token == '*':
            nfa1 = stack.pop()
            s = State(); a = State()
            s.edges[''].append(nfa1.start)
            s.edges[''].append(a)
            nfa1.accept.edges[''].append(nfa1.start)
            nfa1.accept.edges[''].append(a)
            stack.append(NFA(s, a))
        elif token == '+':
            nfa1 = stack.pop()
            s = State(); a = State()
            s.edges[''].append(nfa1.start)
            nfa1.accept.edges[''].append(nfa1.start)
            nfa1.accept.edges[''].append(a)
            stack.append(NFA(s, a))
        elif token == '?':
            nfa1 = stack.pop()
            s = State(); a = State()
            s.edges[''].append(nfa1.start)
            s.edges[''].append(a)
            nfa1.accept.edges[''].append(a)
            stack.append(NFA(s, a))
        elif token == '.':  # concatenation
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            nfa1.accept.edges[''].append(nfa2.start)
            stack.append(NFA(nfa1.start, nfa2.accept))
        elif token == '|':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            s = State(); a = State()
            s.edges[''].append(nfa1.start)
            s.edges[''].append(nfa2.start)
            nfa1.accept.edges[''].append(a)
            nfa2.accept.edges[''].append(a)
            stack.append(NFA(s, a))
        else:
            stack.append(char_nfa(token))
    return stack.pop()

# ------------------ NFA to DFA (Subset Construction) ------------------

def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        for nxt in state.edges.get('', []):
            if nxt not in closure:
                closure.add(nxt)
                stack.append(nxt)
    return closure


def move(states, symbol):
    result = set()
    for state in states:
        for nxt in state.edges.get(symbol, []):
            result.add(nxt)
    return result

class DFA:
    def __init__(self):
        self.start = None
        self.transitions = {}  # (state, symbol) -> state
        self.accepts = set()
        self.states = set()

    def add_transition(self, src, symbol, dst):
        self.transitions[(src, symbol)] = dst
        self.states.add(src)
        self.states.add(dst)

    def set_start(self, s):
        self.start = s
        self.states.add(s)

    def add_accept(self, s):
        self.accepts.add(s)
        self.states.add(s)

    def simulate(self, s):
        curr = self.start
        for c in s:
            key = (curr, c)
            if key not in self.transitions:
                return False
            curr = self.transitions[key]
        return curr in self.accepts


def nfa_to_dfa(nfa):
    dfa = DFA()
    start_closure = frozenset(epsilon_closure({nfa.start}))
    state_map = {start_closure: 0}
    dfa.set_start(0)
    if nfa.accept in start_closure:
        dfa.add_accept(0)
    queue = deque([start_closure])
    next_state_id = 1
    alphabet = set()
    # gather alphabet (non-epsilon)
    to_visit = [nfa.start]
    seen = {nfa.start}
    while to_visit:
        st = to_visit.pop()
        for sym, lst in st.edges.items():
            if sym and sym not in alphabet:
                alphabet.add(sym)
            for ns in lst:
                if ns not in seen:
                    seen.add(ns)
                    to_visit.append(ns)
    while queue:
        current = queue.popleft()
        curr_id = state_map[current]
        for sym in alphabet:
            m = epsilon_closure(move(current, sym))
            if not m:
                continue
            m_frozen = frozenset(m)
            if m_frozen not in state_map:
                state_map[m_frozen] = next_state_id
                if nfa.accept in m_frozen:
                    dfa.add_accept(next_state_id)
                queue.append(m_frozen)
                next_state_id += 1
            dfa.add_transition(curr_id, sym, state_map[m_frozen])
    return dfa

# ------------------ Configuration Conversion and DFA Validation ------------------

def dfa_to_config(dfa):
    """
    Convert our DFA object into the config dict format used by the validator from Tema 1.
    """
    # Alphabet: all symbols seen in transitions
    alfabet = sorted({sym for (src, sym) in dfa.transitions.keys()})
    # States: list of state names as strings
    stari = [str(s) for s in sorted(dfa.states)]
    # Marcaje (labels): 'S' for start, 'F' for accept
    marcaje = {}
    for s in sorted(dfa.states):
        labels = set()
        if s == dfa.start:
            labels.add('S')
        if s in dfa.accepts:
            labels.add('F')
        marcaje[str(s)] = labels
    # Transitions
    tranzitii = []
    for (src, sym), dst in dfa.transitions.items():
        tranzitii.append((str(src), sym, str(dst)))
    return {'alfabet': alfabet, 'stari': stari, 'marcaje': marcaje, 'tranzitii': tranzitii}

# ------------------ DFA Validator (Tema 1) ------------------

def valideaza_dfa(sectiuni):
    """
    Validates the DFA config dict. Returns (is_valid, [error messages]).
    """
    este_valid = True
    mesaje = []
    if 'alfabet' not in sectiuni or 'stari' not in sectiuni or 'tranzitii' not in sectiuni:
        mesaje.append("Lipşeste o sectiune din config.")
        return False, mesaje
    alfabet = sectiuni['alfabet']
    stari = sectiuni['stari']
    marcaje = sectiuni.get('marcaje', {})
    tranzitii = sectiuni['tranzitii']
    # Exactly one start state
    stari_start = [st for st in stari if 'S' in marcaje.get(st, set())]
    if len(stari_start) != 1:
        este_valid = False
        mesaje.append(f"Prea multe sau niciună stare de start; găsite {len(stari_start)}.")
    # Check transitions
    tabel_tr = {}
    for (sursa, simbol, destinatie) in tranzitii:
        if sursa not in stari:
            este_valid = False
            mesaje.append(f"Starea sursă {sursa} nu este declarată.")
        if destinatie not in stari:
            este_valid = False
            mesaje.append(f"Starea destinație {destinatie} nu este declarată.")
        if simbol not in alfabet:
            este_valid = False
            mesaje.append(f"Simbolul '{simbol}' nu este în alfabet.")
        key = (sursa, simbol)
        if key in tabel_tr:
            este_valid = False
            mesaje.append(f"Tranziția {sursa} --{simbol}--> apare de mai multe ori.")
        tabel_tr[key] = destinatie
    return este_valid, mesaje


def simuleaza_dfa(sectiuni, sir_input):
    """
    Simulează DFA pe input. Returnează True dacă e acceptat.
    """
    alfabet = sectiuni['alfabet']
    stari = sectiuni['stari']
    marcaje = sectiuni.get('marcaje', {})
    tranzitii = sectiuni['tranzitii']
    # Build transition table
    tabel_tr = {(s, sym): d for (s, sym, d) in tranzitii}
    # Find start state
    stare_init = next((s for s in stari if 'S' in marcaje.get(s, set())), None)
    if stare_init is None:
        return False
    curr = stare_init
    # Process input
    for c in sir_input:
        if c not in alfabet:
            return False
        key = (curr, c)
        if key not in tabel_tr:
            return False
        curr = tabel_tr[key]
    # Check accept
    return 'F' in marcaje.get(curr, set())

# ------------------ Main and Test Runner ------------------

def run_tests(testfile):
    with open(testfile, 'r', encoding='utf-8') as f:
        suites = json.load(f)
    for suite in suites:
        name = suite.get('name', '<no-name>')
        regex = suite['regex']
        print(f"Suite {name}: regex = '{regex}'")
        # Build DFA
        postfix = regex_to_postfix(regex)
        nfa = thompson(postfix)
        dfa = nfa_to_dfa(nfa)
        # Convert to config
        config = dfa_to_config(dfa)
        # Validate DFA config
        valid, errors = valideaza_dfa(config)
        if not valid:
            print("  Generated DFA is INVALID:")
            for e in errors:
                print("   ", e)
            continue
        # Run tests
        for t in suite['test_strings']:
            inp = t['input']
            exp = t['expected']
            res = simuleaza_dfa(config, inp)
            status = 'OK' if res == exp else 'FAIL'
            print(f"  Input: '{inp}' Expected: {exp} Got: {res} => {status}")
        print()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <tests.json>")
        sys.exit(1)
    run_tests(sys.argv[1])
