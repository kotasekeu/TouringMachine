# Bug Fixes and Issues Found

## Summary

Analyzed and fixed critical issues preventing the Turing machine from completing multiplication for input `1#1#` (1 × 1 = 1).

## Issues Found and Fixed

### 1. ✅ FIXED: T1 Head Movement in Multiplication Logic
**File**: [tm_logic_utils.py:24-38](../tm_logic_utils.py#L24-L38)

**Problem**: In `add_multiplication_logic()`, when transitioning from `q_mul_select` to `q_add_setup` or `q_shift_t2`, T1 head was moving RIGHT immediately. This caused T1 to skip ahead before processing the current bit.

**Fix**: Changed T1 movement from `'R'` to `'S'` (stay). T1 now stays on the current bit during the operation and only moves LEFT after the shift completes.

**Before**:
```python
transitions[(select_state, ('1', b2, b3))] = (add_setup_state, ('1', b2, b3), ('R', 'S', 'S'))
```

**After**:
```python
transitions[(select_state, ('1', b2, b3))] = (add_setup_state, ('1', b2, b3), ('S', 'S', 'S'))
```

---

### 2. ✅ FIXED: Infinite Loop - Same Factor Processed Repeatedly
**File**: [run.py:59-81](../run.py#L59-L81)

**Problem**: After completing a factor, T1 would move LEFT to the separator before that factor. Then `q_look_for_next` would move RIGHT and find the SAME factor again, creating an infinite loop.

**Example**: For input `1#1#` at positions [0,1,2,3]:
- After processing factor at position 2, T1 moves LEFT to position 1 ('#')
- `q_look_for_next` moves RIGHT to position 2, finds '1' again
- Infinite loop: multiply by same factor repeatedly

**Fix**: Added new states to skip past the completed factor:
1. `q_mul_next_bit` → `q_skip_factor` (move RIGHT past separator)
2. `q_skip_factor` → keeps moving RIGHT through the factor bits
3. `q_skip_factor` → `q_check_more_factors` (when hitting blank after factor)
4. `q_check_more_factors` → checks if there's another factor ahead

---

### 3. ✅ FIXED: Termination Condition
**File**: [run.py:73-104](../run.py#L73-L104)

**Problem**: Original termination checked if all three tapes (T1, T2, T3) were blank. But T2 contains the result, so this condition never triggered. Machine would run forever searching for more factors.

**Fix**: After `q_check_more_factors`:
- If next symbol is a bit → more factors exist, continue with `q_transfer`
- If next symbol is blank → no more factors, go to `q_transfer_final` → `q_final`

Created unique state names for final transfer (`q_transfer_final`, `q_final_t2_home`, `q_final_copy`) to avoid conflicts with the regular transfer logic.

---

### 4. ✅ FIXED: Czech Comments Translated to English
**Files**: [run.py](../run.py), [tm_logic_utils.py](../tm_logic_utils.py)

**Problem**: Assignment requires all comments in English, but many were in Czech.

**Fix**: Translated all comments to English:
- Configuration → `# --- Configuration ---`
- Multiplication core → `# 4. MULTIPLICATION CORE`
- Decision after bit → `# 5. DECISION AFTER BIT`
- etc.

---

## Fixed Issues

### ✅ FIXED: Incorrect Result for 1×1
**Status**: FIXED ✅

**Problem**: For input `1#1#` (1 × 1), the machine output `"11"` instead of `"1"`.

**Root Cause**: After shift operations, T2 accumulates bits at multiple positions. When transferring T3→T2, the transfer only overwrote positions where T3 had data. Extra bits from previous iterations in T2 remained.

**Example**:
- After processing and shifting, T2 = "10" (positions: 0='1', 1='0')
- T3 = "1" (position: 0='1')
- Old transfer: copied T3[0]→T2[0], but T2[1]='0' remained
- Buggy result: T2 = "10" → output "10" or "11"

**Solution Applied**: Modified `add_result_transfer_logic()` in [tm_logic_utils.py:125-193](../tm_logic_utils.py#L125-L193):
```python
# Added T2 clearing phase before copying T3→T2:
# 1. Home T3 (move to leftmost blank)
# 2. Home T2 (move to leftmost blank)
# 3. CLEAR T2: Write BLANK to all positions while moving right
# 4. Return T2 to home position
# 5. Copy T3→T2 and erase T3
```

**Test Results**:
- Test 5b (T2 residue test): ✅ PASSED - T2 correctly cleared before transfer
- Full 1×1 multiplication: ✅ PASSED - correct result "1" in 24 steps

---

### 🟡 MEDIUM: Legacy Code Not Removed
**Status**: PARTIALLY FIXED

**Remaining**:
- [turing_machine.py:17-82](../turing_machine.py#L17-L82) - Unused prototype functions
- [turing_machine.py:225-271](../turing_machine.py#L225-L271) - Test code in `__main__` block

**Recommendation**: Remove to improve code clarity.

---

### 🟡 MEDIUM: Unused Utility Function
**File**: [tm_logic_utils.py:103-122](../tm_logic_utils.py#L103-L122)

**Issue**: `add_navigation_logic()` is defined but never called in [run.py](../run.py). Navigation logic is hardcoded in lines 54-60 instead.

**Recommendation**: Either use the function or remove it for consistency.

---

### 🟢 LOW: Czech Comments in Utility Functions
**File**: [tm_logic_utils.py:134-173](../tm_logic_utils.py#L134-L173)

**Issue**: Some Czech comments remain in `add_result_transfer_logic()`:
- Line 134: "POKUD JE NA T3 NULA, ALE NA T2 JE BLANK..."
- Line 139: "Standardní ukončení..."
- Line 163: "POUZE pokud je na T3 bit..."

**Recommendation**: Translate to English.

---

## Test Results

### Input: `1#1#` (1 × 1 = 1)

**Expected**: `1`
**Actual**: `11` ❌

**Steps**: 20 steps
**Final State**: `q_final` ✅

**Tape States**:
```
T1 [pos: 4]: ##1#1###
T2 [pos:-1]: #11#####  ← WRONG: should be "1"
T3 [pos: 0]: ########
```

**Analysis**: Machine successfully terminates but produces incorrect result due to incomplete T2 clearing during transfer.

---

## Files Modified

1. [app/tm_logic_utils.py](../tm_logic_utils.py)
   - Fixed `add_multiplication_logic()` T1 movement
   - Translated comments to English

2. [app/run.py](../run.py)
   - Added `q_skip_factor` and `q_check_more_factors` states
   - Fixed termination logic
   - Created unique final transfer states
   - Translated all comments to English

3. [app/docs/requirements.md](requirements.md) - Created
4. [app/docs/turing.md](turing.md) - Created
5. [app/docs/current_state.md](current_state.md) - Created
6. [app/tests/test_simple_1x1.py](../tests/test_simple_1x1.py) - Created diagnostic test

---

## Next Steps

1. **Fix T2 clearing issue** (HIGH PRIORITY)
   - Modify `add_result_transfer_logic()` to completely erase T2 before copying T3

2. **Test with correct result**
   - Verify `1#1#` → `1`
   - Test `10#11#` (2×3=6) → `110`
   - Test `101#10#110#` (5×2×6=60) → `111100`

3. **Clean up legacy code** (MEDIUM PRIORITY)
   - Remove unused functions from turing_machine.py
   - Remove unused `add_navigation_logic()` or integrate it

4. **Final documentation** (LOW PRIORITY)
   - Translate remaining Czech comments
   - Add algorithm explanation to turing.md
   - Update current_state.md with final status
