# tm_logic_utils.py API Documentation

**Module**: `tm_logic_utils.py`
**Purpose**: Composable logic blocks for binary n-ary multiplication
**Version**: 1.0
**Date**: 2026-01-07

---

## Table of Contents
1. [Overview](#overview)
2. [Algorithm Summary](#algorithm-summary)
3. [Function Reference](#function-reference)
4. [Usage Examples](#usage-examples)
5. [Bug Fixes Implemented](#bug-fixes-implemented)

---

## Overview

This module provides composable logic blocks that implement the **shift-and-add multiplication algorithm** for binary numbers on a 3-tape Turing Machine.

### Input Format
```
x₁ # x₂ # x₃ # ... # xₙ #
```
Binary numbers separated by `#` symbols.

### Output Format
```
Product of all numbers in binary
```

### Tape Usage
| Tape | Purpose | Access |
|------|---------|--------|
| T1   | Input factors | Read-only |
| T2   | Current product/multiplicand | Read-write |
| T3   | Accumulator | Read-write |

---

## Algorithm Summary

### Shift-and-Add Multiplication

For each factor `x` with bits `b_{n-1}...b_1 b_0` (MSB to LSB):

```python
result = 0
T2 = previous_product
T3 = 0

For i from 0 to n-1:  # Process LSB to MSB
    if b_i == 1:
        T3 += T2  # Add current value
    T2 *= 2       # Shift left (multiply by 2)

T2 = T3  # Transfer result for next factor
```

### Example: 5 × 2 × 3

```
Input: "101#10#11#"

Phase 1 - Copy:      T2 = 101 (5)
Phase 2 - Multiply by 10 (2):
  Bit 0: T3 = 101, T2 = 1010
  Bit 1: skip (0), T2 = 10100
  Transfer: T2 = 101 0 (10)
Phase 3 - Multiply by 11 (3):
  Bit 0: T3 = 1010, T2 = 10100
  Bit 1: T3 = 11110, T2 = 101000
  Transfer: T2 = 11110 (30)

Output: "11110" (30 in binary) ✓
```

---

## Function Reference

### 1. add_copy_logic()

**Signature**:
```python
add_copy_logic(transitions, start_state, success_state)
```

**Purpose**: Copy first factor from T1 to T2 (initialization).

**Parameters**:
- `transitions` (dict): Transition table to modify
- `start_state` (str): Initial state (typically `'q_start'`)
- `success_state` (str): Next state (typically `'q_look_for_next'`)

**Behavior**:
- Copies T1 → T2 bit-by-bit
- Stops at first `#` separator
- Positions T1 at next factor, T2 at LSB

**Time Complexity**: O(|x₁|)

**Example**:
```
Input:  T1 = "101#11#"
Output: T1 head at pos 4 ('1'), T2 = "101", T2 head at pos 2 (LSB)
```

---

### 2. add_multiplication_logic()

**Signature**:
```python
add_multiplication_logic(transitions, select_state, add_setup_state,
                         shift_state, success_state)
```

**Purpose**: Decide operation based on current T1 bit (shift-and-add core).

**Parameters**:
- `select_state` (str): Decision state (typically `'q_mul_select'`)
- `add_setup_state` (str): Addition entry (typically `'q_add_setup'`)
- `shift_state` (str): Shift entry (typically `'q_shift_t2'`)
- `success_state` (str): Factor complete (typically `'q_transfer'`)

**Behavior**:
| T1 Bit | Action |
|--------|--------|
| `'1'`  | Add T2 to T3, then shift T2 |
| `'0'`  | Just shift T2 (skip addition) |
| `'#'`  | Factor complete, transfer T3→T2 |

**Time Complexity**: O(1) per bit

---

### 3. add_binary_addition_logic()

**Signature**:
```python
add_binary_addition_logic(transitions, setup_state, success_state)
```

**Purpose**: Binary addition with full-adder logic (T3 := T3 + T2).

**Algorithm**:
1. **Setup**: Position T2 and T3 heads at LSB (asynchronous)
2. **Add**: Ripple-carry addition using states `q_add_c0` and `q_add_c1`
3. **Normalize**: Reposition T3 head (Bug Fix #5)

**Parameters**:
- `setup_state` (str): Setup entry (typically `'q_add_setup'`)
- `success_state` (str): After addition (typically `'q_shift_t2'`)

**Full-Adder Truth Tables**:

| T2 | T3 | Carry In | Sum | Carry Out |
|----|----|---------:|----:|----------:|
| 0  | 0  | 0        | 0   | 0         |
| 0  | 1  | 0        | 1   | 0         |
| 1  | 0  | 0        | 1   | 0         |
| 1  | 1  | 0        | 0   | 1         |
| 0  | 0  | 1        | 1   | 0         |
| 0  | 1  | 1        | 0   | 1         |
| 1  | 0  | 1        | 0   | 1         |
| 1  | 1  | 1        | 1   | 1         |

**Storage Format**:
MSB-first with carry bits at negative positions:
```
T3 = {-1: '1', 0: '0', 1: '0', 2: '0'} → "1000"
```

**Time Complexity**: O(max(|T2|, |T3|))

**Bug Fix #5 - Normalization**:
- Problem: Multiple additions create fragmented data at different negative positions
- Solution: After each addition, move T3 left to leftmost data, then right back

---

### 4. add_shift_logic()

**Signature**:
```python
add_shift_logic(transitions, shift_state, next_bit_state)
```

**Purpose**: Multiply T2 by 2 (left shift by appending '0').

**Parameters**:
- `shift_state` (str): Shift entry (typically `'q_shift_t2'`)
- `next_bit_state` (str): After shift (typically `'q_mul_next_bit'`)

**Behavior**:
1. Move T2 head right to blank
2. Write '0' at that position
3. Move T1 head left to previous bit

**Example**:
```
Before: T2 = "101" (5)
After:  T2 = "1010" (10)  ← Multiplied by 2
```

**Time Complexity**: O(|T2|)

---

### 5. add_navigation_logic()

**Signature**:
```python
add_navigation_logic(transitions, next_bit_state, select_state, transfer_state)
```

**Purpose**: Navigate to next bit or finish factor.

**Parameters**:
- `next_bit_state` (str): After shift (typically `'q_mul_next_bit'`)
- `select_state` (str): Process next bit (typically `'q_mul_select'`)
- `transfer_state` (str): Factor done (typically `'q_transfer'`)

**Behavior**:
| T1 Symbol | Action |
|-----------|--------|
| `'0'` or `'1'` | Continue to `select_state` |
| `'#'` | Go to `transfer_state` |

**Time Complexity**: O(1)

---

### 6. add_result_transfer_logic()

**Signature**:
```python
add_result_transfer_logic(transitions, start_state, success_state)
```

**Purpose**: Transfer result from T3 to T2 after completing one factor (Bug Fix #4).

**Algorithm**:
1. Home T3 (move to leftmost blank)
2. Home T2 (move to leftmost blank)
3. **CLEAR T2 completely** (critical bug fix!)
4. Return T2 to home position
5. Copy T3 → T2 and erase T3

**Parameters**:
- `start_state` (str): Transfer entry (typically `'q_transfer'`)
- `success_state` (str): After transfer (typically `'q_look_for_next'`)

**Bug Fix #4 - T2 Clearing**:
```
Problem:
  T2 = "110" (residual from shifts)
  T3 = "1" (new result)
  Without clearing: T2 = "11" (positions [1,2] remain!) ✗

Solution:
  T2 = "110" → clear all → T2 = "###"
  Copy T3: T2 = "1" ✓
```

**Time Complexity**: O(|T2| + |T3|)

---

## Usage Examples

### Example 1: Building a Simple Multiplier (2 factors)

```python
from tm_logic_utils import *

transitions = {}
blank = '#'
alphabet = ['0', '1', blank]

# Phase 1: Copy first factor
add_copy_logic(transitions, 'q_start', 'q_look_for_next')

# Phase 2: Navigation to second factor
# (Add navigation transitions manually or use run.py composition)

# Phase 3: Multiplication core
add_multiplication_logic(transitions, 'q_mul_select', 'q_add_setup',
                         'q_shift_t2', 'q_transfer')

# Phase 4: Addition
add_binary_addition_logic(transitions, 'q_add_setup', 'q_shift_t2')

# Phase 5: Shift
add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

# Phase 6: Navigation within factor
add_navigation_logic(transitions, 'q_mul_next_bit', 'q_mul_select', 'q_transfer')

# Phase 7: Transfer result
add_result_transfer_logic(transitions, 'q_transfer', 'q_final')

# Now 'transitions' contains all rules for 2-factor multiplication
```

### Example 2: Testing Addition Logic

```python
from turing_machine import MultiTapeTuringMachine, Tape
from tm_logic_utils import add_binary_addition_logic

# Setup
transitions = {}
add_binary_addition_logic(transitions, 'q_add', 'q_done')

tm = MultiTapeTuringMachine(
    states=list(set(s for (s, _) in transitions.keys())),
    alphabet=['0', '1', '#'],
    start_state='q_add',
    accept_states=['q_done'],
    num_tapes=3
)

for (state, syms), (next_state, writes, moves) in transitions.items():
    tm.add_transition(state, syms, next_state, writes, moves)

# Test: 3 + 5 = 8
tm.tapes[1] = Tape('#', "11")   # T2 = 3
tm.tapes[2] = Tape('#', "101")  # T3 = 5

while tm.step_forward():
    pass

# Extract result from T3
result = "".join(tm.tapes[2].data[i] for i in sorted(tm.tapes[2].data.keys())
                 if tm.tapes[2].data[i] != '#')
print(f"Result: {result}")  # Output: "1000" (8 in binary)
```

---

## Bug Fixes Implemented

### Bug #4: T2 Residual Data
**Location**: `add_result_transfer_logic()`

**Problem**:
When transferring T3→T2, old shift-generated data remained in T2 at positions beyond T3's range.

**Example**:
```
T2 = "110" (after shifts at positions [0,1,2])
T3 = "1" (new result at position [0])
Bug: T2 = "110" (positions [1,2] not cleared)
```

**Fix**:
Added complete T2 clearing phase before copying T3:
```python
# Phase 3: CLEAR T2
for all positions:
    T2[pos] = BLANK
# Then copy T3 to clean T2
```

### Bug #5: T3 Fragmentation
**Location**: `add_binary_addition_logic()` - Phase 3 Normalization

**Problem**:
Multiple additions on same T3 created data at progressively negative positions:
```
1st add: T3 = {-2: '1', -1: '0'}
2nd add: T3 = {-6: '0', -5: '1', -4: '0', -2: '1', -1: '0'}  ← Fragmented!
```

**Fix**:
Added normalization after each addition:
```python
# Phase 3: NORMALIZE
# Move T3 left to leftmost data
# Then move right to consistent position
```

---

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Copy | O(\|x₁\|) | O(1) |
| Select | O(1) | O(1) |
| Addition | O(max(\|T2\|, \|T3\|)) | O(1) in-place |
| Shift | O(\|T2\|) | O(1) |
| Navigate | O(1) | O(1) |
| Transfer | O(\|T2\| + \|T3\|) | O(1) |

**Overall for n factors**:
- Time: O(n × m²) where m = max factor length
- Space: O(m × 2ⁿ) for result storage (product grows exponentially)

---

## State Dependencies

Each function adds transitions for specific states. Composition order in `run.py`:

```
q_start
  ↓ (copy)
q_look_for_next
  ↓ (navigate)
q_mul_select
  ↓ (multiply decision)
  ├→ q_add_setup → q_add_c0/q_add_c1 → q_add_finish → q_add_return
  └→ q_shift_t2
      ↓
    q_mul_next_bit
      ↓
    q_transfer → q_transfer_t2_home → q_transfer_clear →
    q_transfer_t2_rehome → q_transfer_copy
      ↓
    q_look_for_next (loop) or q_final (done)
```

---

## Related Files

- **turing_machine.py**: Core TM infrastructure
- **run.py**: Complete state machine assembly
- **tests/test_*.py**: Unit tests for each logic block

---

## Changelog

### Version 1.0 (2026-01-07)
- Comprehensive documentation added
- Bug #4 (T2 residual data) documented
- Bug #5 (T3 fragmentation normalization) documented
- Enhanced inline comments for all phases

---

## License

Generated for CS Theory Project - Educational Use
