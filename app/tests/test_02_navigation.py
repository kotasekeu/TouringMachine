"""
Test 2: Navigation Logic

Tests that the machine can find the next factor on T1 and position at its LSB.
This includes q_look_for_next and q_seek_factor_end states.
"""

from turing_machine import MultiTapeTuringMachine, Tape


def test_find_and_position_at_lsb():
    """Test finding a factor and positioning at its LSB"""
    print("\n=== Test 2a: Find Factor and Position at LSB ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    # Build navigation logic manually (as in run.py)
    for b2 in alphabet:
        for b3 in alphabet:
            # Skip blanks (separators)
            transitions[('q_look_for_next', (blank, b2, b3))] = ('q_look_for_next', (blank, b2, b3), ('R', 'S', 'S'))

            # Found a bit, switch to seeking end
            for bit in ['0', '1']:
                transitions[('q_look_for_next', (bit, b2, b3))] = ('q_seek_factor_end', (bit, b2, b3), ('S', 'S', 'S'))

    # Navigate to end of factor
    for b1 in ['0', '1']:
        for b2 in alphabet:
            for b3 in alphabet:
                transitions[('q_seek_factor_end', (b1, b2, b3))] = ('q_seek_factor_end', (b1, b2, b3), ('R', 'S', 'S'))

    # Hit blank after number -> move back to LSB
    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_seek_factor_end', (blank, b2, b3))] = ('q_done', (blank, b2, b3), ('L', 'S', 'S'))

    # Create machine
    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_look_for_next', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Set input: "##101#" (factor at positions 2-4)
    tm.tapes[0] = Tape(blank, "##101#")
    tm.tapes[0].head = 0  # Start at beginning

    # Expected step matrix
    expected_steps = [
        # Step, State, T1_pos, T1_char
        (0, 'q_look_for_next', 0, '#'),
        (1, 'q_look_for_next', 1, '#'),
        (2, 'q_look_for_next', 2, '1'),
        (3, 'q_seek_factor_end', 2, '1'),
        (4, 'q_seek_factor_end', 3, '0'),
        (5, 'q_seek_factor_end', 4, '1'),
        (6, 'q_seek_factor_end', 5, '#'),
    ]

    print("\nStep | State              | T1[pos]='char' | Status")
    print("-----|--------------------|-----------------|---------")

    for step, exp_state, exp_t1_pos, exp_t1_char in expected_steps:
        act_state = tm.current_state
        act_t1_pos = tm.tapes[0].head
        act_t1_char = tm.tapes[0].read()

        match = (act_state == exp_state and
                 act_t1_pos == exp_t1_pos and
                 act_t1_char == exp_t1_char)

        status = "✅" if match else "❌"

        print(f"{step:4d} | {act_state:18s} | T1[{act_t1_pos}]='{act_t1_char}' {' ' * (8-len(str(act_t1_pos)))} | {status}")

        if not match:
            print(f"     EXPECTED: {exp_state:18s} | T1[{exp_t1_pos}]='{exp_t1_char}'")
            return False

        if not tm.step_forward():
            break

    # Final verification
    final_state = tm.current_state
    final_pos = tm.tapes[0].head
    final_char = tm.tapes[0].read()

    print(f"\n✅ Final State: {final_state}")
    print(f"✅ T1 Head Position: {final_pos} (expected: 4, at LSB)")
    print(f"✅ T1 Current Char: '{final_char}' (expected: '1', the LSB)")

    assert final_state == 'q_done', f"Expected q_done, got {final_state}"
    assert final_pos == 4, f"T1 head should be at 4 (LSB), got {final_pos}"
    assert final_char == '1', f"Should read '1' at LSB, got '{final_char}'"

    print("\n✅ TEST PASSED\n")
    return True


def test_skip_multiple_separators():
    """Test skipping multiple blank separators before finding factor"""
    print("\n=== Test 2b: Skip Multiple Separators ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

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
            transitions[('q_seek_factor_end', (blank, b2, b3))] = ('q_done', (blank, b2, b3), ('L', 'S', 'S'))

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_look_for_next', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Input: "#####11#" (5 blanks, then "11")
    tm.tapes[0] = Tape(blank, "#####11#")
    tm.tapes[0].head = 0

    print("\nExecuting navigation through 5 blanks to find '11'...")

    steps = 0
    max_steps = 20
    while tm.current_state != 'q_done' and steps < max_steps:
        if steps % 5 == 0:
            print(f"Step {steps}: State={tm.current_state:18s}, T1[{tm.tapes[0].head}]='{tm.tapes[0].read()}'")

        if not tm.step_forward():
            break
        steps += 1

    final_state = tm.current_state
    final_pos = tm.tapes[0].head
    final_char = tm.tapes[0].read()

    print(f"\n✅ Final State: {final_state}")
    print(f"✅ T1 Head Position: {final_pos} (expected: 6, at LSB of '11')")
    print(f"✅ T1 Current Char: '{final_char}' (expected: '1')")

    assert final_state == 'q_done', f"Expected q_done, got {final_state}"
    assert final_pos == 6, f"T1 head should be at 6 (LSB of '11'), got {final_pos}"
    assert final_char == '1', f"Should read '1' at LSB, got '{final_char}'"

    print("\n✅ TEST PASSED\n")
    return True


def test_single_bit_factor():
    """Test finding single-bit factor"""
    print("\n=== Test 2c: Single Bit Factor '1' ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

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
            transitions[('q_seek_factor_end', (blank, b2, b3))] = ('q_done', (blank, b2, b3), ('L', 'S', 'S'))

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_look_for_next', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Input: "#1#" (single bit '1' at position 1)
    tm.tapes[0] = Tape(blank, "#1#")
    tm.tapes[0].head = 0

    expected_steps = [
        (0, 'q_look_for_next', 0, '#'),
        (1, 'q_look_for_next', 1, '1'),
        (2, 'q_seek_factor_end', 1, '1'),
        (3, 'q_seek_factor_end', 2, '#'),
    ]

    print("\nStep | State              | T1[pos]='char' | Status")
    print("-----|--------------------|-----------------|---------")

    for step, exp_state, exp_t1_pos, exp_t1_char in expected_steps:
        act_state = tm.current_state
        act_t1_pos = tm.tapes[0].head
        act_t1_char = tm.tapes[0].read()

        match = (act_state == exp_state and
                 act_t1_pos == exp_t1_pos and
                 act_t1_char == exp_t1_char)

        status = "✅" if match else "❌"

        print(f"{step:4d} | {act_state:18s} | T1[{act_t1_pos}]='{act_t1_char}' {' ' * (8-len(str(act_t1_pos)))} | {status}")

        if not match:
            print(f"     EXPECTED: {exp_state:18s} | T1[{exp_t1_pos}]='{exp_t1_char}'")
            return False

        if not tm.step_forward():
            break

    final_state = tm.current_state
    final_pos = tm.tapes[0].head
    final_char = tm.tapes[0].read()

    print(f"\n✅ Final State: {final_state}")
    print(f"✅ T1 Head Position: {final_pos} (expected: 1, at the single bit)")
    print(f"✅ T1 Current Char: '{final_char}' (expected: '1')")

    assert final_state == 'q_done', f"Expected q_done, got {final_state}"
    assert final_pos == 1, f"T1 head should be at 1, got {final_pos}"
    assert final_char == '1', f"Should read '1', got '{final_char}'"

    print("\n✅ TEST PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 2: NAVIGATION LOGIC")
    print("="*70)

    try:
        test_find_and_position_at_lsb()
        test_skip_multiple_separators()
        test_single_bit_factor()

        print("\n" + "="*70)
        print("ALL TESTS PASSED ✅")
        print("="*70 + "\n")
        exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        exit(1)
