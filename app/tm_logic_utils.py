"""
tm_logic_utils.py
================================================================================
Turing Machine Logic Blocks for Binary N-ary Multiplication

This module provides composable logic blocks that implement the shift-and-add
multiplication algorithm for binary numbers on a 3-tape Turing Machine.

Algorithm Overview:
    Input:  x₁ # x₂ # x₃ # ... # xₙ #  (binary numbers separated by #)
    Output: Product of all numbers in binary

Tape Usage:
    T1 (Input):      Read-only input tape with factors separated by #
    T2 (Working):    Current product/multiplicand (modified during computation)
    T3 (Accumulator): Temporary accumulation during single factor processing

Core Operations:
    1. COPY:         Copy first factor from T1 to T2
    2. MULTIPLY:     Process each remaining factor bit-by-bit
    3. ADD:          Binary addition T3 := T3 + T2
    4. SHIFT:        Left shift T2 (multiply by 2)
    5. TRANSFER:     Move result from T3 to T2 after each factor
    6. NAVIGATE:     Move to next bit/factor on T1

State Machine Composition:
    These functions are composed in run.py to create the complete state machine.
    Each function adds transitions for a specific phase of the algorithm.

Author: Generated for CS Theory Project
Date: 2026-01-07
================================================================================
"""

# ============================================================================
# CONSTANTS
# ============================================================================

BLANK = '#'                      # Blank symbol and separator
ALPHABET = ['0', '1', BLANK]     # Binary alphabet


# ============================================================================
# PHASE 1: COPY LOGIC - Initialize T2 with first factor
# ============================================================================

def add_copy_logic(transitions, start_state, success_state):
    """
    Copy the first factor from T1 to T2 (initialization step).

    Purpose:
        Initialize T2 with the first number from T1 before processing
        subsequent factors. This establishes the base value for multiplication.

    Input State:
        - T1 head at start of first factor (position 0)
        - T2 empty (all blank)
        - T3 empty (all blank)

    Output State:
        - T1 head at start of second factor (after first #)
        - T2 contains copy of first factor, head at LSB (rightmost bit)
        - T3 unchanged (still empty)

    Algorithm:
        1. Read bit from T1
        2. Write same bit to T2
        3. Move both heads right
        4. Repeat until # encountered on T1
        5. Move T1 right past #, T2 left to LSB

    Example:
        Input:  T1 = "101#11#"
        After:  T1 head at '1' (position 4), T2 = "101", T2 head at '1' (position 2)

    Transitions Added:
        - δ(start_state, (bit, *, *)) → (start_state, (bit, bit, *), (R, R, S))  for bit ∈ {0,1}
        - δ(start_state, (#, *, *)) → (success_state, (#, *, *), (R, L, S))

    Args:
        transitions (dict): Transition table to modify
        start_state (str): State to begin copying (typically 'q_start')
        success_state (str): State after copy complete (typically 'q_look_for_next')

    Time Complexity: O(|x₁|) where |x₁| is length of first factor
    """
    # Copy loop: Read bit from T1, write to T2, advance both
    for bit in ['0', '1']:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Read bit from T1 → Write to T2 at same position
                # T1: R (move to next bit)
                # T2: R (move to next position)
                # T3: S (stay, unused during copy)
                transitions[(start_state, (bit, b2, b3))] = (
                    start_state,
                    (bit, bit, b3),  # Write bit to T2, preserve T1 and T3
                    ('R', 'R', 'S')
                )

    # Termination: Hit separator on T1, copy complete
    for b2 in ALPHABET:
        for b3 in ALPHABET:
            # T1: R (move past # to start of next factor)
            # T2: L (move back to LSB for multiplication)
            # T3: S (stay, still unused)
            transitions[(start_state, (BLANK, b2, b3))] = (
                success_state,
                (BLANK, b2, b3),  # Don't modify tape contents
                ('R', 'L', 'S')
            )


# ============================================================================
# PHASE 2: MULTIPLICATION DECISION LOGIC - Select operation based on T1 bit
# ============================================================================

def add_multiplication_logic(transitions, select_state, add_setup_state, shift_state, success_state):
    """
    Decide operation based on current bit of factor on T1 (shift-and-add).

    Purpose:
        Implement the core shift-and-add multiplication algorithm. For each bit
        of the current factor on T1:
        - If bit = 1: Add T2 to T3, then shift T2 left
        - If bit = 0: Just shift T2 left (skip addition)
        - If bit = #: Factor complete, transfer T3 → T2

    Algorithm (Shift-and-Add Multiplication):
        For factor x with bits b_{n-1}...b_1 b_0 (MSB to LSB):
            result = 0
            For i from 0 to n-1:  (process LSB to MSB)
                if b_i == 1:
                    result += T2 * (2^i)
            return result

        Implemented as:
            T3 = 0
            For each bit b_i (from LSB to MSB):
                if b_i == 1: T3 += T2
                T2 = T2 * 2  (shift left)

    Input State:
        - T1 head at a bit of current factor (after navigation)
        - T2 contains current product
        - T3 contains partial sum for this factor

    Output State (depends on T1 bit):
        - Bit = '1': Proceed to addition setup
        - Bit = '0': Proceed to shift directly
        - Bit = '#': Proceed to transfer (factor complete)

    Example:
        Multiplying 6 (T2="110") by 3 (T1="11"):
        Bit 0 (LSB '1'): T3 = 0 + 110 = 110, T2 = 1100
        Bit 1 (MSB '1'): T3 = 110 + 1100 = 10010, T2 = 11000
        Result: T3 = 10010 (18 in binary) ✓

    Transitions Added:
        - δ(select, ('1', *, *)) → (add_setup, ('1', *, *), (S, S, S))
        - δ(select, ('0', *, *)) → (shift, ('0', *, *), (S, S, S))
        - δ(select, ('#', *, *)) → (transfer, ('#', *, *), (S, S, S))

    Args:
        transitions (dict): Transition table to modify
        select_state (str): State for operation selection (typically 'q_mul_select')
        add_setup_state (str): State to begin addition (typically 'q_add_setup')
        shift_state (str): State to shift T2 (typically 'q_shift_t2')
        success_state (str): State after factor complete (typically 'q_transfer')

    Note:
        T1 head stays on current bit during both add and shift operations.
        It moves to the next bit only after shift completes.
    """
    for b2 in ALPHABET:
        for b3 in ALPHABET:
            # Case 1: BIT '1' → Add T2 to T3, then shift
            # T1 head stays on '1' during addition (needed for state tracking)
            transitions[(select_state, ('1', b2, b3))] = (
                add_setup_state,
                ('1', b2, b3),  # Don't modify tapes
                ('S', 'S', 'S')  # All heads stay
            )

            # Case 2: BIT '0' → Skip addition, go directly to shift
            # Shifting by 2 without adding is equivalent to multiplying by 0
            transitions[(select_state, ('0', b2, b3))] = (
                shift_state,
                ('0', b2, b3),  # Don't modify tapes
                ('S', 'S', 'S')  # All heads stay
            )

            # Case 3: BLANK → Reached separator, current factor complete
            # Transfer accumulated result from T3 to T2 for next factor
            transitions[(select_state, (BLANK, b2, b3))] = (
                success_state,
                (BLANK, b2, b3),  # Don't modify tapes
                ('S', 'S', 'S')  # All heads stay
            )

# ============================================================================
# PHASE 3: BINARY ADDITION LOGIC - T3 := T3 + T2
# ============================================================================

def add_binary_addition_logic(transitions, setup_state, success_state):
    """
    Binary addition with full-adder logic: T3 := T3 + T2.

    Purpose:
        Add the current product (T2) to the accumulator (T3) using binary
        full-adder logic with carry propagation. Result is written to T3.

    Algorithm (Ripple-Carry Addition):
        1. SETUP: Position T2 and T3 heads at rightmost (LSB) bits
        2. ADD: Process bits from right to left with carry
        3. NORMALIZE: Reposition T3 head for next operation

    Implementation Details:
        - Uses two states for carry: q_add_c0 (carry=0), q_add_c1 (carry=1)
        - Full-adder truth table:
            (T2, T3, carry_in) → (sum, carry_out)
        - Carry bits are written to negative tape positions (left of MSB)
        - Asynchronous setup allows T2 and T3 to have different lengths

    Input State:
        - T1 head unchanged (stays on current factor bit)
        - T2 head at LSB (after previous operations)
        - T3 head at LSB or position 0 (if empty)

    Output State:
        - T1 head unchanged
        - T2 head at rightmost position
        - T3 contains T3_old + T2, head repositioned

    Example:
        T2 = "11" (3), T3 = "101" (5)
        Addition: 3 + 5 = 8
        Process (right to left):
            Position 0: 1 + 1 + c0 = 0, c1  → T3[0] = 0
            Position 1: 1 + 0 + c1 = 0, c1  → T3[1] = 0
            Position 2: 0 + 1 + c1 = 0, c1  → T3[2] = 0
            Position -1: 0 + 0 + c1 = 1, c0 → T3[-1] = 1
        Result: T3 = "1000" (8) ✓

    Storage Format:
        MSB-first with carry bits at negative positions:
        T3 = {-1: '1', 0: '0', 1: '0', 2: '0'} represents "1000"

    Phases:
        Phase 1 - SETUP: Asynchronous head positioning
        Phase 2 - ADD: Full-adder with carry states
        Phase 3 - NORMALIZE: Reposition T3 head

    Args:
        transitions (dict): Transition table to modify
        setup_state (str): State to begin setup (typically 'q_add_setup')
        success_state (str): State after addition complete (typically 'q_shift_t2')

    Time Complexity: O(max(|T2|, |T3|))
    Space Complexity: O(1) extra space (in-place on T3)
    """

    # ------------------------------------------------------------------------
    # Phase 1: ASYNCHRONOUS SETUP
    # ------------------------------------------------------------------------
    # Move T2 and T3 heads independently to their rightmost bits (LSB).
    # This handles numbers of different lengths gracefully.

    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Decide movement for T2 and T3 independently
                m2 = 'R' if b2 in ['0', '1'] else 'S'  # Move if bit, stay if blank
                m3 = 'R' if b3 in ['0', '1'] else 'S'

                if m2 == 'R' or m3 == 'R':
                    # At least one tape needs to move, continue setup
                    transitions[(setup_state, (b1, b2, b3))] = (
                        setup_state,
                        (b1, b2, b3),  # Don't modify tapes during setup
                        ('S', m2, m3)  # T1 stays, T2/T3 move independently
                    )
                else:
                    # Both T2 and T3 at BLANK → aligned at rightmost position
                    # Move both left to start addition from LSB
                    transitions[(setup_state, (b1, BLANK, BLANK))] = (
                        'q_add_c0',  # Enter addition with carry=0
                        (b1, BLANK, BLANK),
                        ('S', 'L', 'L')  # Move to rightmost bits
                    )

    # ------------------------------------------------------------------------
    # Phase 2: FULL-ADDER LOGIC with Carry States
    # ------------------------------------------------------------------------
    # Truth tables for binary full-adder mapped to state transitions.
    # Format: (T2_bit, T3_bit) → (T3_write, next_state)

    # Carry = 0 transitions
    c0_map = {
        ('0', '0'): ('0', 'q_add_c0'),  # 0+0+c0 = 0, c0
        ('0', '1'): ('1', 'q_add_c0'),  # 0+1+c0 = 1, c0
        ('1', '0'): ('1', 'q_add_c0'),  # 1+0+c0 = 1, c0
        ('1', '1'): ('0', 'q_add_c1'),  # 1+1+c0 = 0, c1
        (BLANK, '0'): ('0', 'q_add_c0'),  # Implicit 0 from T2
        (BLANK, '1'): ('1', 'q_add_c0'),
        ('0', BLANK): ('0', 'q_add_c0'),  # Implicit 0 from T3
        ('1', BLANK): ('1', 'q_add_c0'),
        (BLANK, BLANK): (BLANK, 'q_add_finish')  # Both exhausted, done
    }

    # Carry = 1 transitions
    c1_map = {
        ('0', '0'): ('1', 'q_add_c0'),  # 0+0+c1 = 1, c0
        ('0', '1'): ('0', 'q_add_c1'),  # 0+1+c1 = 0, c1
        ('1', '0'): ('0', 'q_add_c1'),  # 1+0+c1 = 0, c1
        ('1', '1'): ('1', 'q_add_c1'),  # 1+1+c1 = 1, c1
        (BLANK, '0'): ('1', 'q_add_c0'),  # Propagate carry with implicit 0
        (BLANK, '1'): ('0', 'q_add_c1'),
        ('0', BLANK): ('1', 'q_add_c0'),
        ('1', BLANK): ('0', 'q_add_c1'),
        (BLANK, BLANK): ('1', 'q_add_finish')  # Final carry bit
    }

    # Apply truth tables to all T1 symbols (T1 is not involved in addition)
    for b1 in ALPHABET:
        # Carry 0 state transitions
        for (r2, r3), (w3, nxt) in c0_map.items():
            transitions[('q_add_c0', (b1, r2, r3))] = (
                nxt,
                (b1, r2, w3),  # Write sum to T3, preserve T1 and T2
                ('S', 'L', 'L')  # Move T2 and T3 left for next bit
            )

        # Carry 1 state transitions
        for (r2, r3), (w3, nxt) in c1_map.items():
            transitions[('q_add_c1', (b1, r2, r3))] = (
                nxt,
                (b1, r2, w3),  # Write sum to T3 with carry
                ('S', 'L', 'L')  # Move T2 and T3 left
            )

    # ------------------------------------------------------------------------
    # Phase 3: NORMALIZATION (Bug Fix #5)
    # ------------------------------------------------------------------------
    # After addition, T3 data may be at various negative positions due to
    # carry propagation. Normalize by repositioning T3 head.
    #
    # Problem: Multiple additions on same T3 create fragmented data:
    #   1st add: T3 = {-2: '1', -1: '0'}
    #   2nd add: T3 = {-6: '0', -5: '1', -4: '0', -2: '1', -1: '0'}  ← Fragmented!
    #
    # Solution: After each addition, move T3 head left to leftmost data,
    # then right back toward position 0 for consistent positioning.

    # Step 1: Move T3 left to find leftmost data
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ['0', '1']:
                # Keep moving T3 left while reading bits
                transitions[('q_add_finish', (b1, b2, b3))] = (
                    'q_add_finish',
                    (b1, b2, b3),
                    ('S', 'S', 'L')  # Only T3 moves left
                )

            # Hit blank on T3 → we're at leftmost, now normalize
            transitions[('q_add_finish', (b1, b2, BLANK))] = (
                'q_add_return',
                (b1, b2, BLANK),
                ('S', 'R', 'R')  # Move T2 and T3 right
            )

    # Step 2: Move T2 and T3 right to normalize position
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Move both right toward position 0
                transitions[('q_add_return', (b1, b2, b3))] = (
                    success_state,
                    (b1, b2, b3),
                    ('S', 'R', 'R')  # Reposition for next operation
                )

# ============================================================================
# PHASE 4: SHIFT LOGIC - Multiply T2 by 2 (Left Shift)
# ============================================================================

def add_shift_logic(transitions, shift_state, next_bit_state):
    """
    Multiply T2 by 2 via left shift (append '0' at LSB).

    Purpose:
        Implement the "shift" part of shift-and-add. After processing a bit
        of the factor, shift T2 left (equivalent to multiplying by 2).

    Algorithm:
        1. Move T2 head right to find blank (end of number)
        2. Write '0' at that position
        3. Move T1 head left to previous bit

    Example:
        Before: T2 = "101" (5)
        After:  T2 = "1010" (10)  ← Left shift = multiply by 2

    Args:
        transitions (dict): Transition table to modify
        shift_state (str): State to begin shift (typically 'q_shift_t2')
        next_bit_state (str): State after shift (typically 'q_mul_next_bit')

    Time Complexity: O(|T2|)
    """
    for b1 in ALPHABET:
        for b3 in ALPHABET:
            # Move T2 head right through existing bits
            for b2 in ['0', '1']:
                transitions[(shift_state, (b1, b2, b3))] = (
                    shift_state,
                    (b1, b2, b3),
                    ('S', 'R', 'S')  # Only T2 moves right
                )

            # Found blank on T2 → append '0' and move T1 left to previous bit
            transitions[(shift_state, (b1, BLANK, b3))] = (
                next_bit_state,
                (b1, '0', b3),  # Write '0' to extend number
                ('L', 'S', 'S')  # T1 moves left to next bit
            )


# ============================================================================
# PHASE 5: NAVIGATION LOGIC - Move to next bit or factor
# ============================================================================

def add_navigation_logic(transitions, next_bit_state, select_state, transfer_state):
    """
    Navigate to next bit of current factor or to transfer state.

    Purpose:
        After shift completes, decide if there are more bits in the current
        factor to process, or if the factor is complete.

    Behavior:
        - If T1 reads a bit ('0' or '1'): More bits remain, go to select_state
        - If T1 reads blank ('#'): Factor complete, go to transfer_state

    Args:
        transitions (dict): Transition table to modify
        next_bit_state (str): State after shift (typically 'q_mul_next_bit')
        select_state (str): State to select operation (typically 'q_mul_select')
        transfer_state (str): State to transfer result (typically 'q_transfer')

    Time Complexity: O(1) - single decision
    """
    for b1 in ['0', '1']:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Still inside factor → process next bit
                transitions[(next_bit_state, (b1, b2, b3))] = (
                    select_state,
                    (b1, b2, b3),
                    ('S', 'S', 'S')  # All heads stay
                )

    for b2 in ALPHABET:
        for b3 in ALPHABET:
            # Hit separator → factor complete, begin transfer
            # Move T1 right past separator
            transitions[(next_bit_state, (BLANK, b2, b3))] = (
                transfer_state,
                (BLANK, b2, b3),
                ('R', 'S', 'S')  # T1 advances past #
            )


# ============================================================================
# PHASE 6: RESULT TRANSFER LOGIC - Move result from T3 to T2
# ============================================================================

def add_result_transfer_logic(transitions, start_state, success_state):
    """
    Transfer result from T3 to T2 after completing one factor (Bug Fix #4).

    Purpose:
        After processing all bits of a factor, move the accumulated result
        from T3 to T2 for multiplication with the next factor.

    CRITICAL BUG FIX:
        Original implementation didn't clear T2 before copying T3, causing
        residual data from previous shift operations to remain in T2.

        Example Bug:
            T2 = "110" (residual after shifts)
            T3 = "1" (new result)
            Without clearing: T2 = "11" (positions 0,1 remain!) ✗
            With clearing: T2 = "1" (correct!) ✓

    Algorithm:
        1. Home T3 (move to leftmost blank)
        2. Home T2 (move to leftmost blank)
        3. CLEAR T2 completely (write blanks everywhere)
        4. Return T2 to home position
        5. Copy T3 → T2 and erase T3

    Args:
        transitions (dict): Transition table to modify
        start_state (str): State to begin transfer (typically 'q_transfer')
        success_state (str): State after transfer (typically 'q_look_for_next')

    Time Complexity: O(|T2| + |T3|)
    """

    # Phase 1: Home T3 (move to leftmost blank)
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ['0', '1']:
                # Move T3 left through data
                transitions[(start_state, (b1, b2, b3))] = (
                    start_state,
                    (b1, b2, b3),
                    ('S', 'S', 'L')
                )

            # Hit blank on T3 → at leftmost, now home T2
            transitions[(start_state, (b1, b2, BLANK))] = (
                'q_transfer_t2_home',
                (b1, b2, BLANK),
                ('S', 'L', 'S')
            )

    # Phase 2: Home T2 (move to leftmost blank)
    for b1 in ALPHABET:
        for b2 in ['0', '1']:
            transitions[('q_transfer_t2_home', (b1, b2, BLANK))] = (
                'q_transfer_t2_home',
                (b1, b2, BLANK),
                ('S', 'L', 'S')
            )

        # Both at home → begin clearing T2
        transitions[('q_transfer_t2_home', (b1, BLANK, BLANK))] = (
            'q_transfer_clear',
            (b1, BLANK, BLANK),
            ('S', 'R', 'S')
        )

    # Phase 3: CLEAR T2 (write blanks to all positions)
    for b1 in ALPHABET:
        for b2 in ['0', '1']:
            for b3 in ALPHABET:
                # Overwrite any bit on T2 with blank
                transitions[('q_transfer_clear', (b1, b2, b3))] = (
                    'q_transfer_clear',
                    (b1, BLANK, b3),  # Write blank to T2
                    ('S', 'R', 'S')
                )

        # T2 cleared → return to home position
        for b3 in ALPHABET:
            transitions[('q_transfer_clear', (b1, BLANK, b3))] = (
                'q_transfer_t2_rehome',
                (b1, BLANK, b3),
                ('S', 'L', 'S')
            )

    # Phase 4: Return T2 to home position
    for b1 in ALPHABET:
        for b3 in ALPHABET:
            for b2 in ['0', '1']:
                # Safety check (shouldn't happen after clearing)
                transitions[('q_transfer_t2_rehome', (b1, b2, b3))] = (
                    'q_transfer_t2_rehome',
                    (b1, b2, b3),
                    ('S', 'L', 'S')
                )

            # At home → begin copying
            transitions[('q_transfer_t2_rehome', (b1, BLANK, b3))] = (
                'q_transfer_copy',
                (b1, BLANK, b3),
                ('S', 'R', 'R')  # Position for copy
            )

    # Phase 5: Copy T3 → T2 and erase T3
    for b1 in ALPHABET:
        # Copy bit from T3 to T2, erase T3
        for b3 in ['0', '1']:
            for b2 in ALPHABET:
                transitions[('q_transfer_copy', (b1, b2, b3))] = (
                    'q_transfer_copy',
                    (b1, b3, BLANK),  # Write T3 bit to T2, erase T3
                    ('S', 'R', 'R')
                )

        # T3 exhausted → transfer complete
        for b2 in ALPHABET:
            transitions[('q_transfer_copy', (b1, b2, BLANK))] = (
                success_state,
                (b1, b2, BLANK),
                ('S', 'L', 'S')  # Position T2 at LSB
            )


# ============================================================================
# END OF MODULE
# ============================================================================
#
# These logic blocks are composed in run.py to create the complete state
# machine for n-ary binary multiplication.
#
# Composition order in run.py:
#   1. Copy first factor to T2
#   2. Navigate to next factor
#   3. For each factor:
#      a. Multiply: For each bit, decide add/shift
#      b. Add: T3 := T3 + T2 (if bit=1)
#      c. Shift: T2 := T2 * 2
#      d. Navigate to next bit
#      e. Transfer: T3 → T2 when factor complete
#   4. Final transfer and termination
#
# See run.py for the complete state machine assembly.
# ============================================================================