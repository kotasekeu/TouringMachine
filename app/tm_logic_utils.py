"""
Turing Machine logic utilities for binary multiplication.
"""

BLANK = '#'
ALPHABET = ['0', '1', BLANK]


def add_copy_logic(transitions, start_state, success_state):
    """Copy first number from T1 to T2."""
    for bit in ['0', '1']:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Copy bit from T1 to T2, advance both heads right
                transitions[(start_state, (bit, b2, b3))] = (start_state, (bit, bit, b3), ('R', 'R', 'S'))

    # Termination: Hit end of number on T1
    for b2 in ALPHABET:
        for b3 in ALPHABET:
            # Move T1 right (to next factor), T2 left (back to LSB)
            transitions[(start_state, (BLANK, b2, b3))] = (success_state, (BLANK, b2, b3), ('R', 'L', 'S'))


def add_multiplication_logic(transitions, select_state, add_setup_state, shift_state, success_state):
    """
    Phase 3: Decide operation based on Tape 1 bit.
    T1 head stays on current bit during operation, moves left AFTER shift.
    """
    for b2 in ALPHABET:
        for b3 in ALPHABET:
            # BIT '1': Add T2 to T3, then shift.
            # T1 stays on current bit during addition.
            transitions[(select_state, ('1', b2, b3))] = (add_setup_state, ('1', b2, b3), ('S', 'S', 'S'))

            # BIT '0': Skip addition, go directly to shift.
            # T1 stays on current bit.
            transitions[(select_state, ('0', b2, b3))] = (shift_state, ('0', b2, b3), ('S', 'S', 'S'))

            # BLANK: Reached separator, current factor complete.
            # Transfer result from T3 to T2.
            transitions[(select_state, (BLANK, b2, b3))] = (success_state, (BLANK, b2, b3), ('S', 'S', 'S'))

def add_binary_addition_logic(transitions, setup_state, success_state):
    """Binary addition: T3 = T3 + T2."""
    # 1. ASYNCHRONOUS SETUP: Each head moves right to its end independently
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Decide movement for each tape separately
                m2 = 'R' if b2 in ['0', '1'] else 'S'
                m3 = 'R' if b3 in ['0', '1'] else 'S'

                if m2 == 'R' or m3 == 'R':
                    # At least one needs to move, continue setup
                    transitions[(setup_state, (b1, b2, b3))] = (setup_state, (b1, b2, b3), ('S', m2, m3))
                else:
                    # Both at BLANK (m2='S', m3='S') -> aligned at end.
                    # Jump to addition and move both left to bits.
                    transitions[(setup_state, (b1, BLANK, BLANK))] = ('q_add_c0', (b1, BLANK, BLANK), ('S', 'L', 'L'))

    c0_map = {
        ('0', '0'): ('0', 'q_add_c0'), ('0', '1'): ('1', 'q_add_c0'),
        ('1', '0'): ('1', 'q_add_c0'), ('1', '1'): ('0', 'q_add_c1'),
        (BLANK, '0'): ('0', 'q_add_c0'), (BLANK, '1'): ('1', 'q_add_c0'),
        ('0', BLANK): ('0', 'q_add_c0'), ('1', BLANK): ('1', 'q_add_c0'),
        (BLANK, BLANK): (BLANK, 'q_add_finish')
    }

    c1_map = {
        ('0', '0'): ('1', 'q_add_c0'), ('0', '1'): ('0', 'q_add_c1'),
        ('1', '0'): ('0', 'q_add_c1'), ('1', '1'): ('1', 'q_add_c1'),
        (BLANK, '0'): ('1', 'q_add_c0'), (BLANK, '1'): ('0', 'q_add_c1'),
        ('0', BLANK): ('1', 'q_add_c0'), ('1', BLANK): ('0', 'q_add_c1'),
        (BLANK, BLANK): ('1', 'q_add_finish')
    }

    # 2. ADDITION: Apply maps to transitions
    for b1 in ALPHABET:
        # Carry 0 state
        for (r2, r3), (w3, nxt) in c0_map.items():
            transitions[('q_add_c0', (b1, r2, r3))] = (nxt, (b1, r2, w3), ('S', 'L', 'L'))
        # Carry 1 state
        for (r2, r3), (w3, nxt) in c1_map.items():
            transitions[('q_add_c1', (b1, r2, r3))] = (nxt, (b1, r2, w3), ('S', 'L', 'L'))

    # 3. FINISH: Move T3 head back to position 0 (or first data position)
    # Move T3 LEFT to leftmost data, then RIGHT back to position 0
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ['0', '1']:
                # Keep moving T3 left while it has data
                transitions[('q_add_finish', (b1, b2, b3))] = ('q_add_finish', (b1, b2, b3), ('S', 'S', 'L'))
            # Hit blank - we're at leftmost, now move right to position 0
            transitions[('q_add_finish', (b1, b2, BLANK))] = ('q_add_return', (b1, b2, BLANK), ('S', 'R', 'R'))

    # Move T2 and T3 right until T3 reaches position 0 (or past all data)
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Move both right
                transitions[('q_add_return', (b1, b2, b3))] = (success_state, (b1, b2, b3), ('S', 'R', 'R'))

def add_shift_logic(transitions, shift_state, next_bit_state):
    """
    Phase 4b: Multiply T2 by 2 (append 0).
    Critical: T2 head moves to first BLANK, writes '0', and T1 head moves Left.
    """
    for b1 in ALPHABET:
        for b3 in ALPHABET:
            # Move T2 head to the right until blank
            for b2 in ['0', '1']:
                transitions[(shift_state, (b1, b2, b3))] = (shift_state, (b1, b2, b3), ('S', 'R', 'S'))

            # Found blank on T2, write '0' and move T1 head to previous bit
            transitions[(shift_state, (b1, BLANK, b3))] = (next_bit_state, (b1, '0', b3), ('L', 'S', 'S'))


def add_navigation_logic(transitions, next_bit_state, select_state, transfer_state):
    """
    Fixed Navigation: Prevents head from wandering away.
    """
    for b1 in ['0', '1']:
        for b2 in ALPHABET:
            for b3 in ALPHABET:
                # Still inside the factor, go select next bit
                transitions[(next_bit_state, (b1, b2, b3))] = (select_state, (b1, b2, b3), ('S', 'S', 'S'))

    for b2 in ALPHABET:
        for b3 in ALPHABET:
            # Hit the separator (#), current factor is done
            # Move T1 one step Right to be ready for Phase 2 (seeking next factor)
            transitions[(next_bit_state, (BLANK, b2, b3))] = (transfer_state, (BLANK, b2, b3), ('R', 'S', 'S'))


def add_result_transfer_logic(transitions, start_state, success_state):
    """
    Phase 5: Transfer T3 -> T2.
    CRITICAL FIX: Completely clear T2 before copying T3 to prevent residual data bug.

    Steps:
    1. Home T3 (move to leftmost blank)
    2. Home T2 (move to leftmost blank)
    3. CLEAR T2 completely (write blanks to all positions)
    4. Return T2 to home position
    5. Copy T3 -> T2 and erase T3
    """
    # 1. Home T3: Move T3 head to the far left until BLANK
    for b1 in ALPHABET:
        for b2 in ALPHABET:
            for b3 in ['0', '1']:
                transitions[(start_state, (b1, b2, b3))] = (start_state, (b1, b2, b3), ('S', 'S', 'L'))

            # Hit BLANK on T3 -> we are at the beginning. Now move T2 to its BLANK too.
            transitions[(start_state, (b1, b2, BLANK))] = ('q_transfer_t2_home', (b1, b2, BLANK), ('S', 'L', 'S'))

    # 2. Home T2: Move T2 head to the far left until BLANK
    for b1 in ALPHABET:
        for b2 in ['0', '1']:
            transitions[('q_transfer_t2_home', (b1, b2, BLANK))] = ('q_transfer_t2_home', (b1, b2, BLANK),
                                                                    ('S', 'L', 'S'))

        # Both T2 and T3 are now at their respective BLANKs (left of data)
        # Go to CLEAR phase instead of copy
        transitions[('q_transfer_t2_home', (b1, BLANK, BLANK))] = ('q_transfer_clear', (b1, BLANK, BLANK),
                                                                   ('S', 'R', 'S'))

    # 3. CLEAR T2: Move right and write BLANK to every position until we hit BLANK
    for b1 in ALPHABET:
        for b2 in ['0', '1']:
            for b3 in ALPHABET:
                # Overwrite any bit on T2 with BLANK, keep moving right
                transitions[('q_transfer_clear', (b1, b2, b3))] = ('q_transfer_clear', (b1, BLANK, b3),
                                                                   ('S', 'R', 'S'))

        # T2 is now BLANK (fully cleared or we're past the data)
        # Move T2 back to home position (leftmost blank)
        for b3 in ALPHABET:
            transitions[('q_transfer_clear', (b1, BLANK, b3))] = ('q_transfer_t2_rehome', (b1, BLANK, b3),
                                                                 ('S', 'L', 'S'))

    # 4. Return T2 to home position (move left until we hit blank on left side)
    for b1 in ALPHABET:
        for b3 in ALPHABET:
            for b2 in ['0', '1']:
                # Should never happen (we just cleared T2), but safety check
                transitions[('q_transfer_t2_rehome', (b1, b2, b3))] = ('q_transfer_t2_rehome', (b1, b2, b3),
                                                                       ('S', 'L', 'S'))

            # T2 is at leftmost blank, ready for copy. T3 is also at home.
            transitions[('q_transfer_t2_rehome', (b1, BLANK, b3))] = ('q_transfer_copy', (b1, BLANK, b3),
                                                                      ('S', 'R', 'R'))

    # 5. Copy: T3 -> T2 and erase T3
    for b1 in ALPHABET:
        # If T3 has a bit (0 or 1), copy it to T2 and erase T3
        for b3 in ['0', '1']:
            for b2 in ALPHABET:
                transitions[('q_transfer_copy', (b1, b2, b3))] = ('q_transfer_copy', (b1, b3, BLANK),
                                                                  ('S', 'R', 'R'))

        # When T3 is BLANK, transfer is complete
        for b2 in ALPHABET:
            transitions[('q_transfer_copy', (b1, b2, BLANK))] = (success_state, (b1, b2, BLANK), ('S', 'L', 'S'))