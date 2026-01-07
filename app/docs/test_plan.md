# Test Plan for Turing Machine Components

## Testing Methodology

Each test uses a **step matrix** to verify correct behavior:

```
Step | State        | T1[pos]='sym' | T2[pos]='sym' | T3[pos]='sym' | Action → Next State
-----|--------------|---------------|---------------|---------------|---------------------
0    | q_start      | T1[0]='1'     | T2[0]='#'     | T3[0]='#'     | Copy → q_start
1    | q_start      | T1[1]='0'     | T2[1]='#'     | T3[0]='#'     | Copy → q_start
...
```

**Verification**:
- ✅ Each step matches expected state, positions, and symbols
- ✅ Final state is correct
- ✅ Final tape contents are correct

---

## Test 1: Copy Logic (`add_copy_logic`)

**Purpose**: Copy first number from T1 to T2, position heads correctly

**Input**: T1 = `"101#"` (5 in binary)

**Expected Behavior**:
1. Copy '1' from T1[0] to T2[0], move both right
2. Copy '0' from T1[1] to T2[1], move both right
3. Copy '1' from T1[2] to T2[2], move both right
4. Read '#' at T1[3], move T1 right, T2 left → end

**Expected Final State**:
- State: `success_state`
- T1: Head at position 4 (after separator)
- T2: Head at position 2 (at LSB), content = "101"
- T3: Unchanged

**Test Matrix**:
```
Step | State         | T1[pos]='sym' | T2[pos]='sym' | T3[pos]='sym' | Write        | Move       | Next
-----|---------------|---------------|---------------|---------------|--------------|------------|-------------
0    | q_start       | T1[0]='1'     | T2[0]='#'     | T3[0]='#'     | (1,1,#)      | (R,R,S)    | q_start
1    | q_start       | T1[1]='0'     | T2[1]='#'     | T3[0]='#'     | (0,0,#)      | (R,R,S)    | q_start
2    | q_start       | T1[2]='1'     | T2[2]='#'     | T3[0]='#'     | (1,1,#)      | (R,R,S)    | q_start
3    | q_start       | T1[3]='#'     | T2[3]='#'     | T3[0]='#'     | (#,#,#)      | (R,L,S)    | q_success
```

**Final Verification**:
- T1 head: 4
- T2 head: 2
- T2 content: "101"

---

## Test 2: Navigation to LSB (`q_look_for_next` → `q_seek_factor_end`)

**Purpose**: Find next factor on T1 and position at its LSB (rightmost bit)

**Input**:
- T1 = `"###101##"` (padding with blanks, factor at positions 3-5)
- Initial T1 head: 0

**Expected Behavior**:
1. Skip blanks (positions 0,1,2) moving right
2. Find '1' at position 3, switch to `q_seek_factor_end`
3. Move right through '0','1' (positions 4,5)
4. Hit blank at position 6, move left to position 5 (LSB)

**Test Matrix**:
```
Step | State              | T1[pos]='sym' | Write  | Move   | Next
-----|--------------------|--------------  |--------|--------|-------------------
0    | q_look_for_next    | T1[0]='#'     | (#,#,#)| (R,S,S)| q_look_for_next
1    | q_look_for_next    | T1[1]='#'     | (#,#,#)| (R,S,S)| q_look_for_next
2    | q_look_for_next    | T1[2]='#'     | (#,#,#)| (R,S,S)| q_look_for_next
3    | q_look_for_next    | T1[3]='1'     | (1,#,#)| (S,S,S)| q_seek_factor_end
4    | q_seek_factor_end  | T1[3]='1'     | (1,#,#)| (R,S,S)| q_seek_factor_end
5    | q_seek_factor_end  | T1[4]='0'     | (0,#,#)| (R,S,S)| q_seek_factor_end
6    | q_seek_factor_end  | T1[5]='1'     | (1,#,#)| (R,S,S)| q_seek_factor_end
7    | q_seek_factor_end  | T1[6]='#'     | (#,#,#)| (L,S,S)| q_mul_select
```

**Final Verification**:
- State: `q_mul_select`
- T1 head: 5 (at LSB '1')

---

## Test 3: Binary Addition (`add_binary_addition_logic`)

**Purpose**: Add T2 to T3 with carry handling

**Input**:
- T2 = "11" (at positions 0,1)
- T3 = "101" (at positions 0,1,2)
- Expected: T3 = "001" + carry → "1000" (3 + 5 = 8)

**Expected Behavior**:
1. **Setup**: Move T2 and T3 heads to rightmost bits
2. **Add with carry**:
   - 1 + 1 = 0, carry 1
   - 1 + 0 = 0 (with carry), carry 1
   - 0 + 1 = 0 (with carry), carry 1
   - Final carry writes '1'
3. **Finish**: Return heads to left

**Test Matrix** (abbreviated):
```
Step | State         | T2[pos]='sym' | T3[pos]='sym' | Write T3 | Carry | Move       | Next
-----|---------------|---------------|---------------|----------|-------|------------|-------------
0    | q_add_setup   | T2[0]='1'     | T3[0]='1'     | (1,1)    | -     | (S,R,S)    | q_add_setup
1    | q_add_setup   | T2[1]='1'     | T3[1]='0'     | (1,0)    | -     | (S,R,S)    | q_add_setup
2    | q_add_setup   | T2[2]='#'     | T3[2]='1'     | (#,1)    | -     | (S,R,S)    | q_add_setup
3    | q_add_setup   | T2[2]='#'     | T3[3]='#'     | (#,#)    | -     | (S,L,L)    | q_add_c0
4    | q_add_c0      | T2[2]='#'     | T3[2]='1'     | 1        | 0     | (L,L)      | q_add_c0
5    | q_add_c0      | T2[1]='1'     | T3[1]='0'     | 1        | 0     | (L,L)      | q_add_c0
6    | q_add_c0      | T2[0]='1'     | T3[0]='1'     | 0        | 1     | (L,L)      | q_add_c1
7    | q_add_c1      | T2[-1]='#'    | T3[-1]='#'    | 1        | 0     | (L,L)      | q_add_finish
```

**Final Verification**:
- T3 content: "1000" (reading from left: positions -1,0,1,2 = '1','0','0','0')

---

## Test 4: Shift Logic (`add_shift_logic`)

**Purpose**: Multiply T2 by 2 (shift left = append 0 at LSB)

**Input**:
- T2 = "11" (at positions 0,1)
- T1 at position 5

**Expected Behavior**:
1. Move T2 head right from position 0 → 1 → 2 (blank)
2. Write '0' at position 2
3. Move T1 left from position 5 → 4

**Test Matrix**:
```
Step | State         | T1[pos]='sym' | T2[pos]='sym' | Write    | Move       | Next
-----|---------------|---------------|---------------|----------|------------|-------------
0    | q_shift_t2    | T1[5]='1'     | T2[0]='1'     | (1,1,#)  | (S,R,S)    | q_shift_t2
1    | q_shift_t2    | T1[5]='1'     | T2[1]='1'     | (1,1,#)  | (S,R,S)    | q_shift_t2
2    | q_shift_t2    | T1[5]='1'     | T2[2]='#'     | (1,0,#)  | (L,S,S)    | q_mul_next_bit
```

**Final Verification**:
- T1 head: 4
- T2 head: 2
- T2 content: "110" (LSB-first storage: positions 0,1,2 = '1','1','0')

---

## Test 5: Result Transfer (`add_result_transfer_logic`)

**Purpose**: Transfer T3 → T2, clear T3

**Input**:
- T2 = "110" (old data at positions 0,1,2)
- T3 = "1000" (result at positions -1,0,1,2)

**Expected Behavior**:
1. **Home T3**: Move T3 left to position -2 (before first bit)
2. **Home T2**: Move T2 left to position -1 (before first bit)
3. **Copy & Clear**:
   - Copy T3[-1]='1' → T2[-1], erase T3[-1]='#'
   - Copy T3[0]='0' → T2[0], erase T3[0]='#'
   - etc.

**Test Matrix** (key steps):
```
Step | State              | T2[pos]='sym' | T3[pos]='sym' | Write      | Move       | Next
-----|--------------------|--------------  |---------------|------------|------------|------------------
0    | q_transfer         | T2[0]='1'     | T3[-1]='1'    | (1,1)      | (S,S,L)    | q_transfer
1    | q_transfer         | T2[0]='1'     | T3[-2]='#'    | (1,#)      | (S,L,S)    | q_transfer_t2_home
2    | q_transfer_t2_home | T2[-1]='#'    | T3[-2]='#'    | (#,#)      | (S,R,R)    | q_transfer_copy
3    | q_transfer_copy    | T2[-1]='#'    | T3[-1]='1'    | (1,#)      | (R,R)      | q_transfer_copy
4    | q_transfer_copy    | T2[0]='1'     | T3[0]='0'     | (0,#)      | (R,R)      | q_transfer_copy
...
```

**Final Verification**:
- T2 content: "1000" (completely replaced old "110")
- T3 content: "####" (all cleared)

---

## Test 6: Full Multiplication 1×1

**Purpose**: End-to-end test for simplest case

**Input**: `"1#1#"`

**Expected Flow**:
1. Copy first '1' to T2
2. Find second '1', position at LSB
3. Bit is '1' → add T2 to T3 → T3="1"
4. Shift T2 → T2="10"
5. No more bits in factor → skip past it
6. No more factors → final transfer T3→T2
7. Terminate with result "1" on T2

**Expected Result**: T2 = "1"

---

## Test 7: Full Multiplication 2×3

**Purpose**: Test multi-bit multiplication

**Input**: `"10#11#"` (2 × 3 = 6 = "110" in binary)

**Expected Flow**:
1. Copy "10" to T2
2. Process "11":
   - Bit[1]='1': Add T2="10" to T3 → T3="10", Shift → T2="010"
   - Bit[0]='1': Add T2="010" to T3 → T3="110", Shift → T2="0010"
3. Transfer T3="110" to T2
4. Terminate

**Expected Result**: T2 = "110" (6 in binary)

---

## Test Implementation Structure

Each test file follows this pattern:

```python
def test_component_name():
    """Test description"""

    # Setup
    transitions = {}
    add_component_logic(transitions, start_state, end_state)

    # Initialize machine
    tm = create_test_machine(transitions)

    # Set initial tape state
    tm.tapes[0] = Tape(BLANK, "input")

    # Define expected step matrix
    expected_steps = [
        {"step": 0, "state": "q_start", "t1_pos": 0, "t1_char": '1', ...},
        {"step": 1, "state": "q_start", "t1_pos": 1, "t1_char": '0', ...},
        ...
    ]

    # Execute and verify each step
    for expected in expected_steps:
        actual = get_current_state(tm)
        assert_step_matches(actual, expected)
        tm.step_forward()

    # Verify final state
    assert_final_state(tm, expected_final)
```

---

## Test Execution Order

1. ✅ **Test 1**: Copy logic (foundation)
2. ✅ **Test 2**: Navigation (find factors)
3. ✅ **Test 3**: Addition (core arithmetic)
4. ✅ **Test 4**: Shift (multiply by 2)
5. ✅ **Test 5**: Transfer (move results)
6. ✅ **Test 6**: Full 1×1 (integration)
7. ✅ **Test 7**: Full 2×3 (complex case)

Each test builds on previous ones, ensuring components work individually before testing integration.
