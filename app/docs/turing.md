# Turing Machine Theory for Binary Multiplication

This document provides the theoretical foundation and specific operational requirements for implementing binary multiplication on a 3-tape Turing machine.

## Three-Tape Architecture

### Tape Designations
- **T1 (Input/Output Tape)**: Contains initial input and final result
- **T2 (Accumulator)**: Stores intermediate multiplication results
- **T3 (Buffer)**: Temporary storage for addition operations

### Critical Rule: Sequential Operations
**Important**: Operations are **sequential, not parallel**. Each transition executes atomically:
1. Read symbols from all tapes simultaneously
2. Write to all tapes simultaneously
3. Move all heads simultaneously

While the operations on different tapes appear "simultaneous" within a single transition, they are executed in one atomic step. There is no parallelization between steps.

### Example Transition
```
(q0, (1, 0, #)) → (q1, (1, 1, 0), (R, R, S))
```
This means:
- Read: T1=1, T2=0, T3=#
- Write: T1=1, T2=1, T3=0
- Move: T1 head Right, T2 head Right, T3 head Stay
- All in **one atomic step**

### Multi-Tape Reading Rules
When reading to determine end-of-input on T1:
- **Must read T1** to check if current position is blank (end marker)
- **Can read T2 and T3** simultaneously in the same transition
- **Can move T2 or T3** simultaneously in the same transition
- All operations happen in **one transition step**, not in parallel threads

**Example**: Checking for end while copying
```
Transition: (q_copy, (1, #, #)) → (q_copy, (1, 1, #), (R, R, S))
- Reads T1 (found '1', not end yet)
- Reads T2 (currently blank)
- Writes to T2 (copy the '1')
- Moves T1 and T2 right
```

## Required Operations for Binary Multiplication

### Algorithm Overview
To compute `x₁ × x₂ × ... × xₙ`:
1. Copy first number `x₁` from T1 to T2 (initial accumulator)
2. For each subsequent number `xᵢ` on T1:
   - Multiply current T2 value by `xᵢ` → result goes to T3
   - Transfer T3 back to T2
3. Final result remains on T1 (or T2 depending on implementation)

### Phase 1: Copy First Number (x₁)
**Goal**: Copy `x₁` from T1 to T2

**Operations**:
- Read bit from T1, write same bit to T2
- Move both T1 and T2 heads right
- Stop when T1 reads blank (`#`)

**States**: `q_start` → `q_copy` → `q_next_factor`

### Phase 2: Navigate to Next Factor
**Goal**: Position T1 head at the start of next number `xᵢ`

**Operations**:
- Skip blank separators on T1 (move right while reading `#`)
- Stop when encountering first bit (`0` or `1`)
- If only blanks remain, computation is complete

**States**: `q_next_factor` → `q_seek_factor_end`

### Phase 3: Position at LSB (Least Significant Bit)
**Goal**: Move T1 head to the rightmost bit of current factor

**Reason**: Binary multiplication processes bits from LSB to MSB (right to left)

**Operations**:
- Move T1 right through all bits (`0` or `1`)
- Stop at blank after the number
- Move back one position left (now at LSB)

**States**: `q_seek_factor_end` → `q_mul_select`

### Phase 4: Multiplication Loop (Core Algorithm)
**Goal**: Multiply current T2 value by current factor on T1

**Algorithm** (Standard binary multiplication):
```
For each bit b in current factor (from LSB to MSB):
    if b == 1:
        Add T2 to T3
    Shift T2 left (multiply by 2, append 0)
    Move to next bit (left on T1)
```

**Sub-operations**:

#### 4a. Bit Decision
- **If T1 reads '1'**: Go to addition routine
- **If T1 reads '0'**: Skip addition, go directly to shift
- **If T1 reads '#'**: Current factor done, go to transfer

**States**: `q_mul_select` → `q_add_setup` | `q_shift_t2` | `q_transfer`

#### 4b. Binary Addition (T3 = T3 + T2)
**Goal**: Add current T2 value to accumulator T3

**Operations**:
1. **Setup**: Move T2 and T3 heads to their respective LSBs (rightmost bits)
2. **Add with carry**:
   - Read bits from T2 and T3
   - Compute sum with carry
   - Write result to T3
   - Move both heads left
3. **Complete**: When both tapes show blank, addition is done

**Truth Table** (with carry):
```
T2  T3  Carry_in  →  Sum  Carry_out
0   0      0          0       0
0   1      0          1       0
1   0      0          1       0
1   1      0          0       1
0   0      1          1       0
0   1      1          0       1
1   0      1          0       1
1   1      1          1       1
```

**States**: `q_add_setup` → `q_add_c0` / `q_add_c1` → `q_add_finish` → `q_shift_t2`

#### 4c. Left Shift (T2 *= 2)
**Goal**: Multiply T2 by 2 (shift left = append 0 at LSB)

**Operations**:
- Move T2 head to rightmost position (first blank)
- Write '0' at that position
- This effectively shifts the number left by one bit

**States**: `q_shift_t2` → `q_mul_next_bit`

#### 4d. Next Bit Check
**Goal**: Determine if more bits remain in current factor

**Operations**:
- Move T1 head left to next bit
- If bit found (`0` or `1`): Continue multiplication loop
- If blank (`#`): Current factor complete, transfer result

**States**: `q_mul_next_bit` → `q_mul_select` | `q_transfer`

### Phase 5: Result Transfer (T3 → T2)
**Goal**: Move accumulated result from T3 back to T2, clear T3

**Operations**:
1. **Home T3**: Move T3 head to leftmost position (before first bit)
2. **Home T2**: Move T2 head to leftmost position
3. **Copy & Clear**:
   - Read from T3, write to T2
   - Write blank to T3 (erase)
   - Move both right
4. **Complete**: When T3 shows blank, transfer done

**States**: `q_transfer` → `q_transfer_t2_home` → `q_transfer_copy` → `q_next_factor`

### Phase 6: Finalization
**Goal**: Handle end of input, prepare final output

**Operations**:
- After processing all factors, result is in T2
- Optionally copy T2 back to T1 for final output
- Enter final/accept state

**States**: `q_next_factor` → `q_final`

## State Naming Convention

All states use descriptive names in English:
- `q_start`: Initial state
- `q_copy`: Copying first number
- `q_next_factor` / `q_look_for_next`: Navigating to next factor
- `q_seek_factor_end`: Finding LSB of current factor
- `q_mul_select`: Deciding operation based on current bit
- `q_add_setup`: Preparing for addition
- `q_add_c0` / `q_add_c1`: Addition with carry 0/1
- `q_shift_t2`: Shifting T2 left
- `q_mul_next_bit`: Checking for next bit in factor
- `q_transfer`: Initiating result transfer
- `q_final`: Accept/final state

## Transition Rules Must Cover

For a complete, deterministic machine, transition rules must handle:
1. **All state-symbol combinations**: Every `(state, (s1, s2, s3))` must have a defined transition or lead to halt
2. **All alphabet symbols**: Rules for `0`, `1`, and `#` on each tape
3. **Boundary conditions**:
   - Empty input
   - Single number (n=1)
   - End of tape markers
4. **Error handling**: Undefined transitions should halt gracefully

## Key Implementation Constraints

### 1. Input Format
- Binary numbers separated by `#`
- Example: `101#11#10#` represents [5, 3, 2]
- Input ends with trailing `#`

### 2. Output Format
- Final result in binary on T1 (or T2)
- No leading zeros (optional: can be cleaned up)
- Result ends at first blank

### 3. Blank Symbol Handling
- `#` represents blank/empty cell
- Used as separator and end marker
- Tape extends infinitely in both directions (simulated)

### 4. Head Movement Rules
- **R (Right)**: head position + 1
- **L (Left)**: head position - 1
- **S (Stay)**: head position unchanged
- Movement happens **after** write operation

### 5. Atomic Transition Execution
Each transition is **one indivisible step**:
1. Read current symbols under all heads
2. Look up transition rule
3. Write new symbols to all tapes
4. Move all heads according to directions
5. Update state

**No interleaving** between tapes - all operations of a single transition happen together.

## Complexity Considerations

### Time Complexity
- **Per multiplication**: O(m × n) where m and n are bit lengths
- **Total for k numbers**: O(k × B²) where B is average bit length
- Each addition: O(max(len(T2), len(T3)))
- Each shift: O(len(T2))

### Space Complexity
- **T1**: O(total input length) - input preserved
- **T2**: O(result bit length) - can grow to sum of input lengths
- **T3**: O(result bit length) - temporary, reused

### Step Count
For input `x₁ # x₂ # ... # xₙ #`:
- Copy x₁: ~O(|x₁|) steps
- Per factor: O(|xᵢ| × |accumulator|) steps
- Total: O(n × B × R) where R is result bit length

## Verification Requirements

To confirm correct implementation:
1. **Trace execution** for simple input (e.g., `10#11#` = 2×3 = 6 = `110`)
2. **Check each phase** completes correctly
3. **Verify tape contents** at each major state transition
4. **Confirm final state** is accept state
5. **Validate output** matches expected product
