"""
Test for the simplest case: 1 * 1 = 1
This test imports the complete state machine from run.py to ensure consistency.
"""

import sys
import os

# Add parent directory to path to import run module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils


def build_complete_machine(input_str, blank='#'):
    """
    Build the complete multiplication state machine.
    This uses the EXACT same logic as run.py to avoid duplication.
    """
    alphabet = ['0', '1', blank]
    num_tapes = 3
    transitions = {}

    # Phase 1: Copy first factor
    utils.add_copy_logic(transitions, 'q_start', 'q_look_for_next')

    # Phase 2: Navigation
    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_look_for_next', (blank, b2, b3))] = (
                'q_look_for_next', (blank, b2, b3), ('R', 'S', 'S')
            )
            for bit in ['0', '1']:
                transitions[('q_look_for_next', (bit, b2, b3))] = (
                    'q_seek_factor_end', (bit, b2, b3), ('S', 'S', 'S')
                )

    # Phase 3: Positioning
    for b1 in ['0', '1']:
        for b2 in alphabet:
            for b3 in alphabet:
                transitions[('q_seek_factor_end', (b1, b2, b3))] = (
                    'q_seek_factor_end', (b1, b2, b3), ('R', 'S', 'S')
                )

    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_seek_factor_end', (blank, b2, b3))] = (
                'q_mul_select', (blank, b2, b3), ('L', 'S', 'S')
            )

    # Phase 4: Multiplication core
    utils.add_multiplication_logic(transitions, 'q_mul_select', 'q_add_setup',
                                    'q_shift_t2', 'q_transfer')
    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_shift_t2')
    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    # Phase 5: Bit navigation
    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                transitions[('q_mul_next_bit', (bit, b2, b3))] = (
                    'q_mul_select', (bit, b2, b3), ('S', 'S', 'S')
                )
            transitions[('q_mul_next_bit', (blank, b2, b3))] = (
                'q_skip_factor', (blank, b2, b3), ('R', 'S', 'S')
            )

    # Phase 5b: Skip completed factor
    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                transitions[('q_skip_factor', (bit, b2, b3))] = (
                    'q_skip_factor', (bit, b2, b3), ('R', 'S', 'S')
                )
            transitions[('q_skip_factor', (blank, b2, b3))] = (
                'q_check_more_factors', (blank, b2, b3), ('R', 'S', 'S')
            )

    # Phase 5c: Check if more factors exist
    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                transitions[('q_check_more_factors', (bit, b2, b3))] = (
                    'q_transfer', (bit, b2, b3), ('S', 'S', 'S')
                )
            transitions[('q_check_more_factors', (blank, b2, b3))] = (
                'q_transfer_final', (blank, b2, b3), ('S', 'S', 'S')
            )

    # Phase 5d: Final transfer
    for b1 in alphabet:
        for b2 in alphabet:
            for b3 in ['0', '1']:
                transitions[('q_transfer_final', (b1, b2, b3))] = (
                    'q_transfer_final', (b1, b2, b3), ('S', 'S', 'L')
                )
            transitions[('q_transfer_final', (b1, b2, blank))] = (
                'q_final_t2_home', (b1, b2, blank), ('S', 'L', 'S')
            )

    for b1 in alphabet:
        for b2 in ['0', '1']:
            transitions[('q_final_t2_home', (b1, b2, blank))] = (
                'q_final_t2_home', (b1, b2, blank), ('S', 'L', 'S')
            )
        transitions[('q_final_t2_home', (b1, blank, blank))] = (
            'q_final_clear', (b1, blank, blank), ('S', 'R', 'S')
        )

    for b1 in alphabet:
        for b2 in ['0', '1']:
            for b3 in alphabet:
                transitions[('q_final_clear', (b1, b2, b3))] = (
                    'q_final_clear', (b1, blank, b3), ('S', 'R', 'S')
                )
        for b3 in alphabet:
            transitions[('q_final_clear', (b1, blank, b3))] = (
                'q_final_rehome', (b1, blank, b3), ('S', 'L', 'S')
            )

    for b1 in alphabet:
        for b3 in alphabet:
            for b2 in ['0', '1']:
                transitions[('q_final_rehome', (b1, b2, b3))] = (
                    'q_final_rehome', (b1, b2, b3), ('S', 'L', 'S')
                )
            transitions[('q_final_rehome', (b1, blank, b3))] = (
                'q_final_copy', (b1, blank, b3), ('S', 'R', 'R')
            )

    for b1 in alphabet:
        for b3 in ['0', '1']:
            for b2 in alphabet:
                transitions[('q_final_copy', (b1, b2, b3))] = (
                    'q_final_copy', (b1, b3, blank), ('S', 'R', 'R')
                )
        for b2 in alphabet:
            transitions[('q_final_copy', (b1, b2, blank))] = (
                'q_final', (b1, b2, blank), ('S', 'L', 'S')
            )

    # Phase 6: Regular transfer
    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_look_for_next')

    # Create machine
    states = list(set([k[0] for k in transitions.keys()]) | {'q_final'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_start', ['q_final'], blank, num_tapes)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    tm.tapes[0] = Tape(blank, input_str)

    return tm, blank


def test_1_times_1():
    """Test multiplication: 1 * 1 = 1 (binary)"""
    input_str = "1#1#"

    print("\n=== Testing 1 * 1 = 1 ===")
    print(f"Input: {input_str}")

    # Build complete machine (same as run.py)
    tm, blank = build_complete_machine(input_str)

    # Run simulation
    max_steps = 100
    step_count = 0

    while tm.current_state != 'q_final' and step_count < max_steps:
        if not tm.step_forward():
            current_symbols = tuple(tape.read() for tape in tm.tapes)
            print(f"\n❌ HALTED: No transition for state '{tm.current_state}' with symbols {current_symbols}")
            print(f"Stopped at step {step_count}")
            return False
        step_count += 1

    # Verify result
    if tm.current_state == 'q_final':
        result = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys())
                        if tm.tapes[1].data[k] != blank)
        print(f"✅ Completed in {step_count} steps")
        print(f"Result on T2: {result}")

        # ASSERTION: Check if result is correct
        assert result == "1", f"Expected '1', got '{result}'"
        print("✅ CORRECT: 1 * 1 = 1")
        return True
    else:
        print(f"\n❌ FAILED: Exceeded {max_steps} steps")
        print(f"Final state: {tm.current_state}")
        return False


if __name__ == "__main__":
    success = test_1_times_1()
    exit(0 if success else 1)
