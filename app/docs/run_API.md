# run.py API Documentation

**Module**: `run.py`
<br />**Purpose**: Main entry point for binary n-ary multiplication using Multi-Tape Turing Machine
<br />**Version**: 1.0
<br />**Date**: 2026-01-07

---

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [State Machine Composition](#state-machine-composition)
4. [Configuration Options](#configuration-options)
5. [Execution Flow](#execution-flow)
6. [Output Files](#output-files)
7. [Usage Examples](#usage-examples)
8. [Performance Analysis](#performance-analysis)

---

## Overview

`run.py` is the main entry point that composes a complete Turing Machine for multiplying an arbitrary number of binary integers. It combines pre-tested logic blocks from `tm_logic_utils.py` with custom navigation and control flow to create a full multiplication machine.

### Key Features
- **Composable Architecture**: Assembles tested components into complete machine
- **N-ary Multiplication**: Handles 2+ factors without modification
- **Detailed Logging**: Configurable step-by-step execution trace
- **Machine Encoding**: Exports machine definition in binary and JSON formats
- **Decimal Verification**: Converts result to decimal for validation

### Input Format
```
x₁ # x₂ # x₃ # ... # xₙ #
```
Binary numbers separated by `#` symbols.

**Example**:
```
"101#10#11#"  → 5 × 2 × 3 = 30 (binary: "11110")
```

### Output
- **Primary**: Binary product on Tape 2 (T2)
- **Trace**: Complete execution log in `final_simulation.txt`
- **Definition**: Machine encoding in `machine_definition.txt`

---

## Architecture

### Tape Usage

| Tape | Purpose | Access | Content Format |
|------|---------|--------|----------------|
| **T1** | Input factors | Read-only | `x₁#x₂#x₃#...#xₙ#` |
| **T2** | Current product / Multiplicand | Read-write | Binary number (MSB-first) |
| **T3** | Accumulator | Read-write | Binary number (MSB-first, with carries at negative positions) |

### Algorithm: Shift-and-Add Multiplication

For input `x₁ # x₂ # x₃ # ... # xₙ #`:

```python
result = x₁  # Copy first factor to T2

for factor in [x₂, x₃, ..., xₙ]:
    T3 = 0  # Clear accumulator

    for bit in reversed(factor):  # Process LSB to MSB
        if bit == 1:
            T3 += T2  # Add current product to accumulator
        T2 = T2 * 2   # Shift left (multiply by 2)

    T2 = T3  # Transfer result for next iteration

return T2  # Final product
```

### Example Execution: 5 × 2 × 3

```
Input: "101#10#11#"

Phase 1 - Copy first factor:
  T1: "101#10#11#" (head at pos 4)
  T2: "101" (5 in decimal)
  T3: empty

Phase 2 - Multiply by second factor "10" (2):
  Process bit 0 (LSB '0'):
    Bit=0 → skip addition, shift T2
    T2: "101" → "1010" (10)
  Process bit 1 (MSB '1'):
    Bit=1 → T3 += T2 → T3="1010", shift T2
    T2: "1010" → "10100" (20)
  Transfer: T2 = T3 = "1010" (10 in decimal) ✓

Phase 3 - Multiply by third factor "11" (3):
  Process bit 0 (LSB '1'):
    Bit=1 → T3 += T2="1010" → T3="1010", shift T2
    T2: "1010" → "10100" (20)
  Process bit 1 (MSB '1'):
    Bit=1 → T3 += T2="10100" → T3="11110", shift T2
    T2: "10100" → "101000" (40)
  Transfer: T2 = T3 = "11110" (30 in decimal) ✓

Phase 4 - No more factors:
  Final transfer: T2 = "11110" (30)
  Halt in accept state q_final

Output: "11110" (30 in binary) ✓
```

---

## State Machine Composition

### State Flow Diagram

```
                     ┌──────────────────────────────────────────┐
                     │                                          │
                     ▼                                          │
    q_start ──copy──> q_look_for_next ──navigate──> q_seek_factor_end
                            ▲                              │
                            │                         position
                            │                              │
                            │                              ▼
                            │                        q_mul_select
                            │                        ╱    │    ╲
                            │                   bit=1   bit=0  bit=#
                            │                      │      │      │
                            │                   q_add  q_shift  │
                            │                      │      │      │
                            │                      └──────┴──────┘
                            │                            │
                            │                      q_mul_next_bit
                            │                        ╱        ╲
                            │                  more bits    blank
                            │                      │            │
                            │                      └────────>   │
                            │                               q_skip_factor
                            │                                   │
                            │                            q_check_more_factors
                            │                              ╱          ╲
                            │                        more data      blank
                            │                            │              │
                            └─────────< q_transfer <─────┘              │
                                                                   q_transfer_final
                                                                        │
                                                                     q_final
                                                                     (ACCEPT)
```

### State Phases

#### Phase 1: Initialization
- **States**: `q_start` → `q_look_for_next`
- **Purpose**: Copy first factor from T1 to T2
- **Implementation**: `utils.add_copy_logic()`

#### Phase 2: Navigation
- **States**: `q_look_for_next` → `q_seek_factor_end`
- **Purpose**: Find start of next factor (skip blanks)
- **Implementation**: Custom transitions

#### Phase 3: Positioning
- **States**: `q_seek_factor_end` → `q_mul_select`
- **Purpose**: Move to LSB of factor (for LSB→MSB processing)
- **Implementation**: Custom transitions

#### Phase 4: Multiplication Core
- **States**: `q_mul_select` ↔ `{q_add_setup, q_shift_t2}` ↔ `q_mul_next_bit`
- **Purpose**: Shift-and-add algorithm execution
- **Implementation**:
  - `utils.add_multiplication_logic()` - Decision logic
  - `utils.add_binary_addition_logic()` - Binary addition
  - `utils.add_shift_logic()` - Left shift

#### Phase 5: Control Flow
- **States**: `q_mul_next_bit` → `q_skip_factor` → `q_check_more_factors`
- **Purpose**: Determine if more factors exist
- **Implementation**: Custom transitions

#### Phase 6: Transfer
- **States**: `q_transfer` → ... → `q_look_for_next` (loop)
- **Purpose**: Move result T3→T2 for next factor
- **Implementation**: `utils.add_result_transfer_logic()`

#### Phase 7: Final Transfer
- **States**: `q_transfer_final` → ... → `q_final` (accept)
- **Purpose**: Move final result T3→T2 and terminate
- **Implementation**: Custom transitions (duplicates transfer logic with unique state names)

---

## Configuration Options

### Machine Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `blank` | `'#'` | Blank symbol and factor separator |
| `alphabet` | `['0', '1', '#']` | Binary alphabet |
| `input_str` | `"101#10#110#1#1001#10#"` | Input factors (5×2×6×1×9×2) |
| `output_file` | `"final_simulation.txt"` | Execution trace output file |
| `machine_file` | `"machine_definition.txt"` | Machine encoding output file |
| `num_tapes` | `3` | Number of tapes (T1, T2, T3) |

### Logging Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `log_every_n_steps` | `1` | Log frequency (1=every step, 10=every 10th step) |
| `show_debug_info` | `False` | Show T2/T3 data at key states |
| `max_steps` | `10000` | Safety limit to prevent infinite loops |

### Customizing Input

To multiply different numbers, modify `input_str`:

```python
# Example: 7 × 3 × 4 = 84
input_str = "111#11#100#"  # Binary: 7 # 3 # 4 #

# Example: 15 × 15 = 225
input_str = "1111#1111#"   # Binary: 15 # 15 #

# Example: 2 × 2 × 2 × 2 = 16
input_str = "10#10#10#10#" # Binary: 2 # 2 # 2 # 2 #
```

**Important**: Always end with a trailing `#` separator!

---

## Execution Flow

### 1. Configuration Phase
```python
def main():
    blank = '#'
    alphabet = ['0', '1', blank]
    input_str = "101#10#110#1#1001#10#"
    transitions = {}
```
Initialize machine parameters and empty transition table.

### 2. State Machine Composition Phase
```python
    # Add copy logic
    utils.add_copy_logic(transitions, 'q_start', 'q_look_for_next')

    # Add navigation logic (custom)
    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_look_for_next', (blank, b2, b3))] = ...

    # Add multiplication core
    utils.add_multiplication_logic(...)
    utils.add_binary_addition_logic(...)
    utils.add_shift_logic(...)

    # Add control flow (custom)
    # ... skip_factor, check_more_factors logic

    # Add transfer logic
    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_look_for_next')

    # Add final transfer logic (custom, similar to regular transfer)
    # ... q_transfer_final sequence
```
Build complete state machine by composing logic blocks.

### 3. Machine Instantiation Phase
```python
    states = list(set([k[0] for k in transitions.keys()]) | {'q_final'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_start', ['q_final'], blank, num_tapes)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    tm.tapes[0] = Tape(blank, input_str)
```
Create machine instance and load all transitions. Initialize T1 with input.

### 4. Execution Loop Phase
```python
    with open(output_file, "w", encoding="utf-8") as f:
        SimulationLogger.log_tapes(tm, f)  # Log initial state

        while tm.current_state != 'q_final' and tm.step < max_steps:
            if tm.step % log_every_n_steps == 0:
                print(f"Step {tm.step}: State={tm.current_state}, ...")
                SimulationLogger.log_state(tm, f)

            if not tm.step_forward():
                # Unexpected halt
                f.write(f"\nHALTED: No rule for state {tm.current_state}\n")
                break
```
Execute machine step-by-step with periodic logging.

### 5. Result Extraction Phase
```python
        if tm.current_state == 'q_final':
            res = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys())
                         if tm.tapes[1].data[k] != blank)
            f.write(f"RESULT ON TAPE 2: {res}\n")

            if res:
                decimal_result = int(res, 2)
                f.write(f"RESULT IN DECIMAL: {decimal_result}\n")
```
Extract binary result from T2 and convert to decimal for verification.

### 6. Machine Definition Export Phase
```python
            with open(machine_file, "w", encoding="utf-8") as mf:
                mf.write(f"MACHINE (Binary):\n{TuringEncoder(tm).encode_binary()}\n")
                mf.write(f"\nENCODED MACHINE (JSON):\n{TuringEncoder(tm).encode()}\n")
```
Save machine definition for analysis and reproducibility.

---

## Output Files

### 1. final_simulation.txt

**Contents**: Complete execution trace with tape visualizations

**Format**:
```
N-ary multiplication of: 101#10#110#1#1001#10#

Step 0 (q_start)
T1 [pos:  0]: ##101#10#110#1#1001#10#
              ^
T2 [pos:  0]: ################
              ^
T3 [pos:  0]: ################
              ^
----------------------------------------
Step 0 (q_start): Read (1,#,#) -> Write (1,1,#), Move (R,R,S), Next: q_start
Step 1 (q_start)
...
Step 371 (q_final)
...
COMPUTATION COMPLETE
RESULT ON TAPE 2: 10000111000
RESULT IN DECIMAL: 1080

Machine definition written to machine_definition.txt
Total steps executed: 371
```

**Key Sections**:
- **Header**: Input string
- **Tape Logs**: Periodic snapshots showing:
  - Current step and state
  - All three tapes with head positions (marked by `^`)
  - Dynamic windowing (only relevant tape regions shown)
- **State Logs**: Transition details for each step:
  - Symbols read from each tape
  - Symbols written to each tape
  - Head movements for each tape
  - Next state
- **Result**: Final binary and decimal values

**Tape Visualization Details**:
- Positions displayed as absolute indices
- Dynamic window: Shows data ± padding, hides infinite blanks
- Head indicator: `^` symbol below current position
- Negative positions: Used for carry bits in T3 during addition

### 2. machine_definition.txt

**Contents**: Machine encoding in two formats

**Structure**:
```
================================================================================
MACHINE ENCODING (BINARY UNARY FORMAT)
================================================================================

[Long binary string with unary-encoded states, symbols, and transitions]

================================================================================
MACHINE ENCODING (JSON FORMAT)
================================================================================

{
  "states": ["q_add_c0", "q_add_c1", "q_add_finish", ...],
  "alphabet": ["#", "0", "1"],
  "start_state": "q_start",
  "accept_states": ["q_final"],
  "blank": "#",
  "num_tapes": 3,
  "transitions": [
    {
      "current_state": "q_start",
      "read_symbols": ["1", "#", "#"],
      "next_state": "q_start",
      "write_symbols": ["1", "1", "#"],
      "moves": ["R", "R", "S"]
    },
    ...
  ]
}
```

**Binary Encoding**:
- Unary representation of states and symbols
- Theoretical format for Kolmogorov complexity analysis
- See `turing_machine.py` TuringEncoder class for encoding details

**JSON Encoding**:
- Human-readable machine definition
- Can be used to reconstruct machine
- Useful for debugging and analysis
- All ~20 states and hundreds of transitions explicitly listed

---

## Usage Examples

### Example 1: Basic Multiplication (2 factors)

```python
# Modify run.py line 80:
input_str = "101#11#"  # 5 × 3 = 15

# Run:
python3 run.py

# Expected output in final_simulation.txt:
# RESULT ON TAPE 2: 1111
# RESULT IN DECIMAL: 15
```

**Expected Steps**: ~30-40 steps

**Key States**:
1. Copy "101" to T2
2. Navigate to "11"
3. Position at LSB of "11"
4. Multiply: process bits 1, 1
5. Transfer final result
6. Halt

### Example 2: Three Factors

```python
input_str = "10#11#100#"  # 2 × 3 × 4 = 24

# Expected output:
# RESULT ON TAPE 2: 11000
# RESULT IN DECIMAL: 24
```

**Expected Steps**: ~70-90 steps

### Example 3: Powers of Two

```python
input_str = "10#10#10#10#"  # 2 × 2 × 2 × 2 = 16

# Expected output:
# RESULT ON TAPE 2: 10000
# RESULT IN DECIMAL: 16
```

**Observation**: Each factor "10" (2) only requires one shift operation, making this very efficient.

### Example 4: Large Product

```python
input_str = "1111#1111#"  # 15 × 15 = 225

# Expected output:
# RESULT ON TAPE 2: 11100001
# RESULT IN DECIMAL: 225
```

**Expected Steps**: ~100-120 steps

### Example 5: Identity Multiplication

```python
input_str = "101#1#"  # 5 × 1 = 5

# Expected output:
# RESULT ON TAPE 2: 101
# RESULT IN DECIMAL: 5
```

**Observation**: Multiplying by 1 demonstrates correct behavior when only LSB bit=1.

### Example 6: Using Debug Mode

```python
# Modify run.py lines 87-88:
log_every_n_steps = 10  # Log every 10th step for speed
show_debug_info = True   # Show T2/T3 contents at key states

input_str = "101#10#"  # 5 × 2 = 10

# Output will include debug lines like:
#   Step 20 (q_mul_select): ...
#   DEBUG: T2={0: '1', 1: '0', 2: '1', 3: '0'}, T3={0: '1', 1: '0', 2: '1'}
```

**Use Case**: Understanding intermediate computation states during multiplication.

---

## Performance Analysis

### Time Complexity

For multiplying `n` factors where the largest factor has `m` bits:

| Operation | Complexity per Factor | Total |
|-----------|----------------------|-------|
| Copy first factor | O(m) | O(m) |
| Navigate to factor | O(m) | O(n·m) |
| Position to LSB | O(m) | O(n·m) |
| Multiply (all bits) | O(m²) | O(n·m²) |
| Transfer result | O(result_length) | O(n·2ⁿ·m) |

**Overall**: O(n·m²) for reasonable inputs, O(n·2ⁿ·m) worst-case (exponential result growth)

**Explanation**:
- Each bit of a factor requires:
  - Addition: O(current_product_length) ≈ O(m)
  - Shift: O(current_product_length) ≈ O(m)
  - Total per bit: O(m)
- Processing all m bits: O(m²)
- With n factors: O(n·m²)

**Special Case - Powers of 2**:
When multiplying only by factors like "10" (2), "100" (4), etc.:
- Only one bit=1, so only one addition per factor
- Time complexity improves to O(n·m)

### Space Complexity

| Component | Space |
|-----------|-------|
| T1 (input) | O(n·m) |
| T2 (product) | O(result_length) ≤ O(n·m) |
| T3 (accumulator) | O(result_length) ≤ O(n·m) |
| Transition table | O(states × alphabet³) = O(1) (constant for this problem) |

**Total**: O(n·m) for input, O(2ⁿ·m) for result storage (exponential in n)

### Step Count Benchmarks

Based on actual execution:

| Input | Factors | Product | Steps | Notes |
|-------|---------|---------|-------|-------|
| "1#1#" | 1 × 1 | 1 | ~30 | Minimal case |
| "101#11#" | 5 × 3 | 15 | ~40 | Two factors |
| "101#10#11#" | 5 × 2 × 3 | 30 | ~70 | Three factors |
| "101#10#110#1#1001#10#" | 5×2×6×1×9×2 | 1080 | 371 | Six factors (default) |
| "1111#1111#" | 15 × 15 | 225 | ~120 | Large factors |

**Observations**:
- Step count grows quadratically with factor bit-length
- Step count grows linearly with number of factors
- Addition dominates runtime for factors with many 1-bits
- Shift operations are relatively fast

### Optimization Opportunities

**Not Implemented** (would break TM purity):
1. **Karatsuba Multiplication**: O(n^log₂3) ≈ O(n^1.585) for large numbers
2. **Parallel Tape Operations**: Current model uses sequential tape heads
3. **Skip Zero Factors**: Special handling for "0" multiplication
4. **Memoization**: Cache intermediate products

**Why Not Optimized**:
- Educational/theoretical purity: Standard TM model
- Correctness over performance: Clear, testable implementation
- Composition simplicity: Reusable logic blocks

---

## State Count and Transition Statistics

### State Breakdown

| Phase | States | Purpose |
|-------|--------|---------|
| Copy | 1 | `q_start` |
| Navigation | 2 | `q_look_for_next`, `q_seek_factor_end` |
| Multiplication | 3 | `q_mul_select`, `q_mul_next_bit`, `q_shift_t2` |
| Addition | 4 | `q_add_setup`, `q_add_c0`, `q_add_c1`, `q_add_finish`, `q_add_return` |
| Control Flow | 2 | `q_skip_factor`, `q_check_more_factors` |
| Transfer | 5 | `q_transfer`, `q_transfer_t2_home`, `q_transfer_clear`, `q_transfer_t2_rehome`, `q_transfer_copy` |
| Final Transfer | 5 | `q_transfer_final`, `q_final_t2_home`, `q_final_clear`, `q_final_rehome`, `q_final_copy` |
| Accept | 1 | `q_final` |
| **Total** | **~20** | (exact count depends on composition) |

### Transition Count

Estimated transition count: **~400-500 transitions**

Breakdown:
- Copy: ~27 transitions (3³ = 27 symbol combinations)
- Navigation: ~18 transitions
- Positioning: ~18 transitions
- Multiplication core: ~27 transitions
- Binary addition: ~135 transitions (full-adder truth tables)
- Shift: ~18 transitions
- Control flow: ~36 transitions
- Transfer: ~50 transitions (each transfer phase)
- Final transfer: ~50 transitions

**Why So Many?**
- Multi-tape TM requires transitions for all symbol combinations: |Q| × |Σ|³
- Full-adder requires separate transitions for carry=0 and carry=1
- Each phase must handle all possible T2 and T3 states

---

## Troubleshooting

### Problem: Infinite Loop

**Symptom**: Machine runs for >1000 steps without reaching `q_final`

**Possible Causes**:
1. Missing transition for some state/symbol combination
2. Incorrect skip_factor or check_more_factors logic
3. Input missing trailing `#` separator

**Solution**:
- Check `final_simulation.txt` for last logged state
- Look for repeating state patterns
- Verify input format: `"101#10#11#"` ✓ vs `"101#10#11"` ✗

### Problem: Incorrect Result

**Symptom**: Machine halts but result is wrong

**Possible Causes**:
1. Bug in transfer logic (T2 not fully cleared)
2. Bug in addition logic (carry not propagated)
3. Input format error (extra/missing separators)

**Solution**:
- Enable debug mode: `show_debug_info = True`
- Check T2 and T3 values at key states
- Manually verify expected result: `python3 -c "print(bin(5*2*3))"`

### Problem: Unexpected Halt

**Symptom**: Machine halts with "HALTED: No rule for state X"

**Possible Causes**:
1. Missing transition for specific symbol combination
2. State name mismatch between logic blocks
3. Incomplete state machine composition

**Solution**:
- Check error message for exact state and symbols
- Search `run.py` for that state name
- Verify all utils functions are called with correct state names

### Problem: Empty Result

**Symptom**: `RESULT ON TAPE 2: ` (blank)

**Possible Causes**:
1. Machine never copied first factor to T2
2. Transfer logic cleared T2 but didn't copy T3
3. Halt occurred before final transfer

**Solution**:
- Check if machine reached `q_final` state
- Review copy phase transitions in log
- Verify final transfer logic executed

---

## Related Files

- **[turing_machine.py](turing_machine_API.md)**: Core TM infrastructure
- **[tm_logic_utils.py](tm_logic_utils_API.md)**: Composable logic blocks
- **[final_simulation.txt](../final_simulation.txt)**: Generated execution trace
- **[machine_definition.txt](../machine_definition.txt)**: Generated machine encoding
