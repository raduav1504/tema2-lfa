# Regex → DFA

## Project Structure

- **regex_to_dfa.py**  
  Main script:  
  - Parses a regular expression  
  - Builds an NFA via Thompson’s construction  
  - Converts NFA → DFA by subset construction  
  - Validates and simulates the DFA against test cases  
- **tests.json**  
  JSON file with ≥20 test suites  
 

---

## Usage

### Prerequisites

- Python 3.x 

### Running

1. Clone or download the repository  
2. Open a terminal and `cd` into the project folder  
3. Execute:
   ```bash
   python regex_to_dfa.py tests.json
4. Observe per-suite output:
   -Suite name
   -Original regex
   -Each test input → expected vs. actual result

### Implementation Decisions
No external libraries for regex or automata—everything is handwritten using only Python’s stdlib.

## Parser:

Shunting‐Yard algorithm to convert infix → postfix

Implicit concatenation is made explicit with operator .

## NFA:

Thompson’s construction

ε-transitions represented by the empty string ''

## DFA:

Subset construction (ε-closure + move)

States numbered in order of discovery

## Simulation & Validation:

DFA simulator walks transitions, checks final state label

Validator enforces exactly one start, valid symbols, no duplicate transitions


## Code organization

All functionality lives in regex_to_dfa.py for simplicity.


