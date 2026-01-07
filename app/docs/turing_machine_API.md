# turing_machine.py API Documentation

**Module**: `turing_machine.py`
**Purpose**: Core infrastructure for Multi-Tape Turing Machine simulation
**Version**: 1.0
**Date**: 2026-01-07

---

## Table of Contents
1. [Overview](#overview)
2. [Module Constants](#module-constants)
3. [Class: Tape](#class-tape)
4. [Class: MultiTapeTuringMachine](#class-multitapeturingmachine)
5. [Class: TuringEncoder](#class-turingencoder)
6. [Class: SimulationLogger](#class-simulationlogger)
7. [Usage Examples](#usage-examples)
8. [Implementation Notes](#implementation-notes)

---

## Overview

This module provides a generic framework for simulating Deterministic Multi-Tape Turing Machines. It is designed to be:
- **Generic**: Works with any alphabet, number of tapes, and transition function
- **Efficient**: Uses dictionary-based sparse storage for tapes
- **Extensible**: Easy to add new transition rules and states
- **Observable**: Built-in logging and visualization tools

### Architecture

```
turing_machine.py (generic TM infrastructure)
     ↑
     | uses
     |
tm_logic_utils.py (multiplication logic blocks)
     ↑
     | composed by
     |
run.py (main entry point)
```

This module contains **only** the generic TM infrastructure. The actual multiplication algorithm is defined in `tm_logic_utils.py` and composed in `run.py`.

---

## Module Constants

### ALPHABET
```python
ALPHABET = ['0', '1', '#']
```
**Type**: `list[str]`
**Description**: Default alphabet for binary multiplication
**Values**:
- `'0'` - Binary digit zero
- `'1'` - Binary digit one
- `'#'` - Blank/separator symbol

### BLANK
```python
BLANK = '#'
```
**Type**: `str`
**Description**: Symbol representing empty tape cells and separators

### NUM_TAPES
```python
NUM_TAPES = 3
```
**Type**: `int`
**Description**: Default number of tapes (T1=input, T2=working, T3=accumulator)

---

## Class: Tape

Represents an infinite bi-directional tape with sparse storage.

### Storage Model

- **Sparse Dictionary**: Only non-blank cells consume memory
- **Infinite Extension**: Supports positive and negative indices
- **Zero-Indexed**: Initial content starts at position 0

### Constructor

```python
Tape(blank_symbol='#', initial_content="")
```

**Parameters**:
- `blank_symbol` (str): Symbol for empty cells (default: `'#'`)
- `initial_content` (str): Data to load at positions [0, len-1] (default: empty)

**Example**:
```python
tape = Tape('#', "101")
# Creates: {0: '1', 1: '0', 2: '1'}, head at 0
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `blank` | str | Blank symbol |
| `data` | defaultdict | Sparse storage: {position → symbol} |
| `head` | int | Current head position (can be negative) |

### Methods

#### read() → str
Read symbol at current head position.

**Returns**: Symbol at `head` position (blank if uninitialized)

**Example**:
```python
tape.head = 5
symbol = tape.read()  # Returns tape.data[5] or blank
```

---

#### write(symbol: str)
Write symbol to current head position.

**Parameters**:
- `symbol` (str): Symbol to write (should be in alphabet)

**Side Effects**: Updates `tape.data[head]`

**Example**:
```python
tape.write('1')  # Sets tape.data[tape.head] = '1'
```

---

#### move(direction: str)
Move tape head one position.

**Parameters**:
- `direction` (str): One of:
  - `'R'` - Move right (+1)
  - `'L'` - Move left (-1)
  - `'S'` - Stay (no movement)

**Side Effects**: Updates `tape.head`

**Example**:
```python
tape.head = 5
tape.move('R')  # head becomes 6
tape.move('L')  # head becomes 5
tape.move('S')  # head stays 5
```

**Note**: Moving left from position 0 goes to negative positions:
```python
tape.head = 0
tape.move('L')  # head becomes -1
```

---

#### get_bounds() → tuple[int, int]
Calculate extent of tape based on data and head position.

**Returns**: `(min_position, max_position)`

**Use Case**: Determining what range to display in visualizations

**Example**:
```python
tape.data = {0: '1', -2: '0', 5: '1'}
tape.head = 3
min_pos, max_pos = tape.get_bounds()  # Returns (-2, 5)
```

---

## Class: MultiTapeTuringMachine

Core execution engine for k-tape Turing Machines.

### Computational Model

```
Step 1: Read symbols from all tapes
Step 2: Look up δ(state, (sym1, sym2, ...))
Step 3: Write new symbols
Step 4: Move all heads
Step 5: Update state
Step 6: Repeat or halt
```

### Constructor

```python
MultiTapeTuringMachine(states, alphabet, start_state, accept_states,
                       blank='#', num_tapes=3)
```

**Parameters**:
- `states` (iterable): Collection of state names (will be sorted)
- `alphabet` (iterable): Collection of symbols (will be sorted)
- `start_state` (str): Initial state name
- `accept_states` (iterable): Accepting/halting states
- `blank` (str): Blank symbol (default: `'#'`)
- `num_tapes` (int): Number of tapes (default: 3)

**Example**:
```python
tm = MultiTapeTuringMachine(
    states=['q0', 'q1', 'qf'],
    alphabet=['0', '1', '#'],
    start_state='q0',
    accept_states=['qf'],
    num_tapes=2
)
```

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `states` | list[str] | Sorted list of state names |
| `alphabet` | list[str] | Sorted list of symbols |
| `start_state` | str | Initial state |
| `accept_states` | set[str] | Accepting states |
| `blank` | str | Blank symbol |
| `num_tapes` | int | Number of tapes |
| `transitions` | dict | Transition function table |
| `current_state` | str | Current state (changes during execution) |
| `tapes` | list[Tape] | List of tape objects |
| `step` | int | Step counter (increments on each transition) |

### Methods

#### add_transition(curr_state, read_symbols, next_state, write_symbols, moves)
Add a transition rule to the machine.

**Parameters**:
- `curr_state` (str): Current state name
- `read_symbols` (tuple): Symbols read from each tape
- `next_state` (str): Next state name
- `write_symbols` (tuple): Symbols to write to each tape
- `moves` (tuple): Head movements ('L', 'R', or 'S' for each tape)

**Transition Format**:
```
δ(curr_state, (read1, read2, ...)) = (next_state, (write1, write2, ...), (move1, move2, ...))
```

**Example**:
```python
# δ(q0, ('1', '#')) = (q1, ('1', '1'), ('R', 'R'))
tm.add_transition('q0', ('1', '#'), 'q1', ('1', '1'), ('R', 'R'))
```

**Storage**: Internally stored as:
```python
transitions[('q0', ('1', '#'))] = ('q1', ('1', '1'), ('R', 'R'))
```

---

#### step_forward() → bool
Execute a single computational step.

**Returns**:
- `True`: Transition executed successfully
- `False`: No valid transition found (halted)

**Execution Sequence**:
1. Read symbols from all tapes at current heads
2. Look up `transitions[(current_state, symbols)]`
3. If not found, return `False` (halt)
4. Write new symbols to tapes
5. Move all heads
6. Update `current_state`
7. Increment `step` counter
8. Return `True`

**Example**:
```python
while tm.step_forward():
    print(f"Step {tm.step}")
print("Halted")
```

**Side Effects**:
- Modifies tape contents
- Moves tape heads
- Changes `current_state`
- Increments `step`

---

## Class: TuringEncoder

Encodes machine definitions into binary or JSON formats.

### Constructor

```python
TuringEncoder(machine: MultiTapeTuringMachine)
```

**Parameters**:
- `machine`: TM instance to encode

**Example**:
```python
encoder = TuringEncoder(tm)
binary_str = encoder.encode_binary()
json_str = encoder.encode()
```

### Methods

#### encode_binary() → str
Encode machine as binary string using unary representation.

**Returns**: Binary-encoded machine (string of '0' and '1')

**Encoding Scheme**:
- States: `q_i → '0' * (i+1)`
- Symbols: `a_j → '0' * (j+1)`
- Moves: `L='0', R='00', S='000'`
- Separator within transition: `'1'`
- Separator between transitions: `'11'`

**Format**:
```
state_in | symbols_in | state_out | symbols_out | moves
```

**Example**:
```python
# For δ(q0, ('1', '#')) = (q0, ('1', '1'), ('R', 'R'))
# If q0=0th state='0', '#'=0th symbol='0', '1'=2nd symbol='000'
# L='0', R='00', S='000'
# Encodes as: "0|1|000|0|1|0|000|000|1|00|00"
```

**Use Case**: Theoretical analysis (e.g., Kolmogorov complexity)

---

#### encode() → str
Encode machine as JSON string.

**Returns**: JSON-formatted machine definition

**JSON Structure**:
```json
{
  "states": ["q0", "q1", ...],
  "alphabet": ["#", "0", "1", ...],
  "start_state": "q0",
  "accept_states": ["qf"],
  "blank": "#",
  "num_tapes": 3,
  "transitions": [
    {
      "current_state": "q0",
      "read_symbols": ["1", "#"],
      "next_state": "q1",
      "write_symbols": ["1", "1"],
      "moves": ["R", "R"]
    },
    ...
  ]
}
```

**Use Cases**:
- Saving configurations to disk
- Debugging transition tables
- Sharing machine definitions
- Visualization tools

---

## Class: SimulationLogger

Static utility class for logging TM execution.

### Methods

#### log_tapes(machine, file)
Log visual representation of all tapes.

**Parameters**:
- `machine` (MultiTapeTuringMachine): Machine to visualize
- `file`: File handle (must support `write()`)

**Output Format**:
```
Step 5 (q_add_c0)
T1 [pos:  2]: ##101#10#110##
                  ^
T2 [pos:  3]: #####10######
                     ^
T3 [pos: -1]: #1########
                ^
----------------------------------------
```

**Features**:
- Dynamic windowing (shows only relevant regions)
- Head position indicators (`^`)
- Position labels (absolute coordinates)
- Automatic padding around data

**Implementation**:
- Scans all tapes to find data extent
- Expands window to include heads ± padding
- Default window: [-2, 6] if no data exists
- Handles negative positions (carry bits)

---

#### log_state(machine, file)
Log current state and transition details.

**Parameters**:
- `machine` (MultiTapeTuringMachine): Machine to log
- `file`: File handle (must support `write()`)

**Output Format**:
```
Step 5 (q_add_c0): Read (1,0,#) -> Write (1,0,1), Move (S,L,L), Next: q_add_c1
```

Or if no transition:
```
Step 10 (q_done): Read (#,1,#) -> HALT (No transition)
```

**Details Logged**:
- Step number
- Current state
- Symbols read from each tape
- Symbols to be written
- Head movements
- Next state or HALT

**Note**: Logs *before* transition executes (shows what *will* happen)

---

## Usage Examples

### Example 1: Simple 2-Tape TM (Copy Machine)

```python
from turing_machine import MultiTapeTuringMachine, Tape

# Define machine
tm = MultiTapeTuringMachine(
    states=['q0', 'q1', 'qf'],
    alphabet=['0', '1', '#'],
    start_state='q0',
    accept_states=['qf'],
    num_tapes=2
)

# Add transitions: Copy T1 to T2
for bit in ['0', '1']:
    tm.add_transition('q0', (bit, '#'), 'q0', (bit, bit), ('R', 'R'))

# Stop when T1 reaches blank
tm.add_transition('q0', ('#', '#'), 'qf', ('#', '#'), ('S', 'S'))

# Load input
tm.tapes[0] = Tape('#', "101")

# Run
while tm.step_forward():
    pass

# Extract result
result = "".join(tm.tapes[1].data[i] for i in sorted(tm.tapes[1].data.keys())
                 if tm.tapes[1].data[i] != '#')
print(f"Result: {result}")  # Output: "101"
```

### Example 2: Using SimulationLogger

```python
from turing_machine import SimulationLogger

with open("log.txt", "w") as f:
    f.write("=== TM EXECUTION LOG ===\n\n")
    SimulationLogger.log_tapes(tm, f)

    while tm.step_forward():
        SimulationLogger.log_state(tm, f)
        if tm.step % 5 == 0:  # Log tape state every 5 steps
            SimulationLogger.log_tapes(tm, f)

    SimulationLogger.log_tapes(tm, f)
    f.write("\nCOMPUTATION COMPLETE\n")
```

### Example 3: Encoding Machine

```python
from turing_machine import TuringEncoder
import json

# Encode as JSON
encoder = TuringEncoder(tm)
json_str = encoder.encode()

# Save to file
with open("machine_def.json", "w") as f:
    f.write(json_str)

# Parse back
machine_def = json.loads(json_str)
print(f"States: {machine_def['states']}")
print(f"Transitions: {len(machine_def['transitions'])}")

# Binary encoding for theoretical analysis
binary_encoding = encoder.encode_binary()
print(f"Binary length: {len(binary_encoding)} chars")
```

### Example 4: Multi-Step Execution with Timeout

```python
max_steps = 1000
timeout_reached = False

for _ in range(max_steps):
    if not tm.step_forward():
        break
else:
    timeout_reached = True

if timeout_reached:
    print(f"ERROR: Exceeded {max_steps} steps (possible infinite loop)")
elif tm.current_state in tm.accept_states:
    print(f"SUCCESS: Halted in accept state after {tm.step} steps")
else:
    print(f"HALTED: Stopped in non-accept state {tm.current_state}")
```

---

## Implementation Notes

### Sparse Tape Storage

Tapes use `defaultdict(lambda: blank)` for efficient memory usage:

```python
# Only stores non-blank cells
tape.data = {0: '1', 2: '1', -1: '1'}
# Positions 1, 3, 4, ..., -2, -3, ... all read as blank
```

**Benefits**:
- O(1) read/write at any position
- No pre-allocation needed
- Infinite extension in both directions
- Memory proportional to data size, not tape extent

### Transition Table Lookup

Transitions use dictionary with tuple keys for O(1) lookup:

```python
key = (current_state, tuple(symbols))
if key in transitions:
    next_state, writes, moves = transitions[key]
```

**Performance**: Constant time regardless of number of states/transitions

### Head Movement Edge Cases

```python
# Moving into negative positions
tape.head = 0
tape.move('L')  # head = -1 (valid, tape extends left)

# Reading uninitialized positions
tape.head = 100
symbol = tape.read()  # Returns blank (no error)

# Writing to any position
tape.head = -50
tape.write('1')  # Valid, creates data[-50] = '1'
```

### State Sorting

States and alphabet are **sorted** in constructor:

```python
tm = MultiTapeTuringMachine(
    states=['qz', 'qa', 'qm'],  # Input order
    ...
)
print(tm.states)  # ['qa', 'qm', 'qz'] - Sorted!
```

**Impact**: Affects binary encoding indices. Ensure consistency across encodings.

### Accept State Checking

Machine doesn't auto-halt in accept states:

```python
# Manual check required
while tm.current_state not in tm.accept_states:
    if not tm.step_forward():
        break
```

Or use transition absence to halt:

```python
# No transitions from 'qf' → auto-halts when qf reached
```

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Tape read/write | O(1) | O(1) |
| Tape move | O(1) | O(1) |
| Transition lookup | O(1) | O(1) |
| Step execution | O(k) | O(k) |
| Tape get_bounds | O(n) | O(1) |
| Log tapes | O(k × w) | O(k × w) |

Where:
- `k` = number of tapes
- `n` = number of non-blank cells
- `w` = display window width

---

## Thread Safety

**Not thread-safe**. Do not share TM instances across threads without external synchronization.

---

## Related Files

- **tm_logic_utils.py**: Multiplication logic blocks (add, shift, transfer)
- **run.py**: Main entry point and state machine composition
- **tests/test_*.py**: Unit and integration tests

---

## Changelog

### Version 1.0 (2026-01-07)
- Initial release
- Comprehensive documentation added
- Removed deprecated functions
- Enhanced comments for all classes and methods

---

## License

Generated for CS Theory Project - Educational Use
