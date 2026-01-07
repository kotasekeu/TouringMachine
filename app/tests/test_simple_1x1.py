"""
Test for the simplest case: 1 * 1 = 1
This should complete in under 100 steps.
"""

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils


def test_1_times_1():
    """Test multiplication: 1 * 1 = 1 (binary)"""
    blank = '#'
    alphabet = ['0', '1', blank]
    input_str = "1#1#"
    num_tapes = 3
    transitions = {}

    # Build transitions (same as run.py)
    utils.add_copy_logic(transitions, 'q_start', 'q_look_for_next')

    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_look_for_next', (blank, b2, b3))] = ('q_look_for_next', (blank, b2, b3), ('R', 'S', 'S'))
            for bit in ['0', '1']:
                transitions[('q_look_for_next', (bit, b2, b3))] = ('q_seek_factor_end', (bit, b2, b3), ('S', 'S', 'S'))

    for b1 in ['0', '1']:
        for b2 in alphabet:
            for b3 in alphabet:
                transitions[('q_seek_factor_end', (b1, b2, b3))] = ('q_seek_factor_end', (b1, b2, b3), ('R', 'S', 'S'))

    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_seek_factor_end', (blank, b2, b3))] = ('q_mul_select', (blank, b2, b3), ('L', 'S', 'S'))

    utils.add_multiplication_logic(transitions, 'q_mul_select', 'q_add_setup', 'q_shift_t2', 'q_transfer')
    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_shift_t2')
    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                transitions[('q_mul_next_bit', (bit, b2, b3))] = ('q_mul_select', (bit, b2, b3), ('S', 'S', 'S'))
            transitions[('q_mul_next_bit', (blank, b2, b3))] = ('q_transfer', (blank, b2, b3), ('S', 'S', 'S'))

    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_look_for_next')
    transitions[('q_look_for_next', (blank, blank, blank))] = ('q_final', (blank, blank, blank), ('S', 'S', 'S'))

    states = list(set([k[0] for k in transitions.keys()]) | {'q_final'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_start', ['q_final'], blank, num_tapes)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    tm.tapes[0] = Tape(blank, input_str)

    print("\n=== Testing 1 * 1 = 1 ===")
    print(f"Input: {input_str}")
    print("\nStep-by-step trace:")

    max_steps = 100
    step_count = 0

    while tm.current_state != 'q_final' and step_count < max_steps:
        current_symbols = tuple(tape.read() for tape in tm.tapes)

        # Detailed trace
        t1_pos = tm.tapes[0].head
        t2_pos = tm.tapes[1].head
        t3_pos = tm.tapes[2].head

        print(f"Step {step_count:3d}: State={tm.current_state:20s} | "
              f"T1[{t1_pos}]='{current_symbols[0]}' | "
              f"T2[{t2_pos}]='{current_symbols[1]}' | "
              f"T3[{t3_pos}]='{current_symbols[2]}'")

        # Check for infinite loop patterns
        if step_count > 0 and step_count % 10 == 0:
            if tm.current_state in ['q_mul_select', 'q_add_setup', 'q_add_c0']:
                print(f"  ⚠️  WARNING: Potential loop detected at step {step_count}")

        if not tm.step_forward():
            print(f"\n❌ HALTED: No transition for state '{tm.current_state}' with symbols {current_symbols}")
            break

        step_count += 1

    if tm.current_state == 'q_final':
        result = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)
        print(f"\n✅ SUCCESS: Computation completed in {step_count} steps")
        print(f"Result on T2: {result}")

        if result == "1":
            print("✅ CORRECT: 1 * 1 = 1")
            return True
        else:
            print(f"❌ WRONG: Expected '1', got '{result}'")
            return False
    else:
        print(f"\n❌ FAILED: Exceeded {max_steps} steps or halted unexpectedly")
        print(f"Final state: {tm.current_state}")

        # Debug: show tape contents
        print("\nFinal tape contents:")
        for i, tape in enumerate(tm.tapes):
            if tape.data:
                content = "".join(tape.data.get(j, blank) for j in range(-5, 10))
                print(f"  T{i+1}: {content} (head at {tape.head})")

        return False


if __name__ == "__main__":
    success = test_1_times_1()
    exit(0 if success else 1)
