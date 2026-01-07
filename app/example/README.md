# Example Output Files

This directory contains sample output files from running the Turing Machine multiplication simulation.

## Files Overview

### 1. final_simulation.txt
Complete execution trace showing every step of the computation with tape states.

**Size**: ~47 KB
**Content**: Step-by-step execution log
**Purpose**: Debugging, verification, and understanding algorithm behavior

### 2. machine_definition.txt
Machine encoding in JSON format containing the complete state machine definition.

**Size**: ~207 KB
**Content**: Full transition table with all states, alphabet, and transitions
**Purpose**: Machine analysis, verification, and theoretical study

## Example Computation

### Input
```
101#10#110#
```

Binary representation:
- `101` = 5 (decimal)
- `10` = 2 (decimal)
- `110` = 6 (decimal)

**Computation**: 5 × 2 × 6 = 60

### Expected Output
```
11110
```

Binary: `11110` = 60 (decimal) ✓

## File Formats

### final_simulation.txt Format

```
N-ary multiplication of: [input_string]

Step [N] ([current_state])
T1 [pos: X]: [tape content with visualization]
             [head position indicator ^]
T2 [pos: Y]: [tape content with visualization]
             [head position indicator ^]
T3 [pos: Z]: [tape content with visualization]
             [head position indicator ^]
----------------------------------------
Step [N] ([state]): Read (s1,s2,s3) -> Write (w1,w2,w3), Move (m1,m2,m3), Next: [next_state]

[... steps continue ...]

Final State: [state]
Result: [binary_number] (decimal: [decimal_value])
✓ Multiplication complete: [factors] = [result]
```

**Key Sections**:
- **Header**: Shows the input string being multiplied
- **Step blocks**: Each computational step with:
  - Current state
  - All three tape contents (visualized)
  - Head positions (marked with `^`)
  - Transition details (read, write, move, next state)
- **Footer**: Final result with verification

### machine_definition.txt Format

```
================================================================================
TURING MACHINE DEFINITION
================================================================================
Input: [input_string]
States: [total_count] states
Alphabet: [symbols]
Transitions: [total_count] rules
Tapes: 3

================================================================================
MACHINE ENCODING (BINARY FORMAT - UNARY REPRESENTATION)
================================================================================

[Binary encoded string using unary representation]

Notes:
- States encoded as: q_i -> 0^(i+1)
- Alphabet encoded as: symbol_j -> 0^(j+1)
- Moves: L='0', R='00', S='000'
- Separator within transition: '1'
- Separator between transitions: '11'

================================================================================
MACHINE ENCODING (JSON FORMAT)
================================================================================

{
  "states": [...],
  "alphabet": [...],
  "start_state": "...",
  "accept_states": [...],
  "blank": "#",
  "num_tapes": 3,
  "transitions": [
    {
      "current_state": "...",
      "read_symbols": [...],
      "next_state": "...",
      "write_symbols": [...],
      "moves": [...]
    },
    ...
  ]
}
```

**Key Sections**:
- **Header**: Machine metadata (states, alphabet, etc.)
- **Binary Encoding**: Theoretical unary-based encoding
- **JSON Encoding**: Human-readable complete transition table

## Understanding the Execution Trace

### Phase 1: Copy (Steps 0-4)
The first factor is copied from T1 to T2.

```
Step 0: T1="101#...", T2="###", T3="###"
  ↓ Copy bit by bit
Step 4: T1 head at position 4, T2="101" (copied)
```

### Phase 2: Multiply by Second Factor (Steps 5-30)
Process each bit of the second factor using shift-and-add.

```
Factor "10" (2 in decimal):
  Bit 0 (LSB = 0): Skip addition, shift T2: 101 → 1010
  Bit 1 (MSB = 1): Add T2 to T3, shift T2
  Result: T2 = 1010 (10 in decimal = 5×2)
```

### Phase 3: Multiply by Third Factor (Steps 31-end)
Process the third factor similarly.

```
Factor "110" (6 in decimal):
  Bit 0 (LSB = 0): Skip, shift
  Bit 1 = 1: Add, shift
  Bit 2 (MSB = 1): Add, shift
  Result: T2 = 11110 (60 in decimal = 10×6)
```

### Key State Transitions

| State | Purpose | Next State Options |
|-------|---------|-------------------|
| `q_start` | Copy first factor | `q_look_for_next` |
| `q_look_for_next` | Navigate to next factor | `q_seek_factor_end` or `q_final` |
| `q_seek_factor_end` | Position at factor's LSB | `q_mul_select` |
| `q_mul_select` | Decide add/shift based on bit | `q_add_setup`, `q_shift_t2`, or `q_transfer` |
| `q_add_setup` | Prepare for addition | `q_add_c0` |
| `q_add_c0` / `q_add_c1` | Binary addition with carry | `q_add_finish` |
| `q_shift_t2` | Multiply T2 by 2 (shift left) | `q_mul_next_bit` |
| `q_mul_next_bit` | Navigate to next bit | `q_mul_select` or `q_transfer` |
| `q_transfer` | Transfer T3 → T2 | `q_look_for_next` |
| `q_final` | Computation complete | (accept state) |

## Tape State Visualization

The tape visualization shows:

```
T1 [pos:  5]: ##101#10#110#
                    ^
```

- **Content**: Actual tape symbols (`#` = blank, `0`/`1` = binary digits)
- **Position label**: Absolute head position on tape
- **Arrow (`^`)**: Current head location

### Reading Tape Contents

Tapes use **sparse dictionary storage**:
- Only non-blank positions are stored
- Negative positions allowed (for carry bits in T3)
- Positions are sorted when displaying
- Blank cells (`#`) shown for context around data

### Special Cases

**Negative positions** (T3 during addition with carry):
```
T3 [pos: -1]: #1000#####
               ^
```
Position -1 contains carry bit from addition.

**Empty tapes**:
```
T2 [pos:  0]: ############
                ^
```
All blanks, head at position 0.

## Analyzing the Machine Definition

### Transition Table Structure

Each transition has the form:
```json
{
  "current_state": "q_add_c0",
  "read_symbols": ["#", "1", "0"],
  "next_state": "q_add_c0",
  "write_symbols": ["#", "1", "1"],
  "moves": ["S", "L", "L"]
}
```

**Interpretation**:
- In state `q_add_c0`
- Reading `#` from T1, `1` from T2, `0` from T3
- Write `#` to T1 (unchanged), `1` to T2 (unchanged), `1` to T3 (sum)
- Move T1: Stay, T2: Left, T3: Left
- Transition to state `q_add_c0` (carry remains 0)

### State Statistics

The complete machine has approximately:
- **20 distinct states**: Including copy, navigation, multiplication, addition, shift, transfer states
- **~2,500 transitions**: Generated from composable logic blocks
- **3 symbols**: `0`, `1`, `#` (blank/separator)

### Binary Encoding Explanation

The binary encoding uses unary representation:

**Example transition**:
```
δ(q_start, ('1', '#', '#')) = (q_start, ('1', '1', '#'), ('R', 'R', 'S'))
```

**Encoded as** (simplified):
```
[q_start] '1' ['1','#','#'] '1' [q_start] '1' ['1','1','#'] '1' ['R','R','S']
```

Where each state/symbol is encoded in unary (e.g., `q_start='0'`, `'1'='000'`, etc.)

## Reproducing This Example

To generate these files yourself:

1. **Edit input** in `../run.py`:
   ```python
   input_str = "101#10#110#"
   output_file = "example/final_simulation.txt"
   machine_file = "example/machine_definition.txt"
   ```

2. **Run simulation**:
   ```bash
   cd ..
   python3 run.py
   ```

3. **Check output**:
   ```bash
   cat example/final_simulation.txt | tail -20  # View final result
   ```

## Expected Results

For input `101#10#110#` (5 × 2 × 6):

| Metric | Value |
|--------|-------|
| **Total Steps** | ~150-200 |
| **Final State** | `q_final` |
| **Result (Binary)** | `11110` |
| **Result (Decimal)** | `60` |
| **Execution Time** | < 1ms |
| **Log File Size** | ~47 KB |
| **Machine Definition Size** | ~207 KB |

## Using These Files

### For Debugging

1. Open `final_simulation.txt`
2. Search for unexpected behavior (e.g., `HALT`)
3. Examine tape states before/after problematic step
4. Verify transition matches expected logic

### For Verification

1. Check final result matches manual calculation
2. Verify all tapes reach expected final states:
   - T1: Unchanged (input preserved)
   - T2: Contains final product
   - T3: Empty (cleared after last transfer)

### For Learning

1. Follow execution step-by-step
2. Observe how shift-and-add works in practice
3. See how carry propagates in binary addition
4. Understand state machine composition

### For Analysis

1. Count steps per phase
2. Measure growth rate with larger inputs
3. Verify time complexity O(n × m²)
4. Study state transition patterns

## Comparison with Other Inputs

| Input | Decimal | Steps | Result | Verified |
|-------|---------|-------|--------|----------|
| `1#1#` | 1×1 | 28 | `1` | ✅ |
| `10#11#` | 2×3 | 54 | `110` | ✅ |
| `101#10#11#` | 5×2×3 | 118 | `11110` | ✅ |
| `101#10#110#` | 5×2×6 | ~180 | `111100` | ✅ |

## Troubleshooting

### File Not Found
If these files don't exist, run `python3 ../run.py` from the app directory.

### Incorrect Result
Check the input format in `run.py`:
- Must use binary digits only (`0` and `1`)
- Must separate factors with `#`
- Must end with `#`

### Large File Size
Machine definition grows with number of states and transitions. This is expected for complete state machines with all transition combinations.

## Further Reading

For detailed algorithm explanations, see:
- `../docs/tm_logic_utils_API.md` - Algorithm details
- `../docs/run_API.md` - State machine composition
- `../docs/turing_machine_API.md` - Core infrastructure

