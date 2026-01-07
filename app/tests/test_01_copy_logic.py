"""
Test 1: Copy Logic (add_copy_logic)

Tests that the first number is correctly copied from T1 to T2,
and heads are positioned correctly for subsequent operations.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils


def test_copy_single_bit():
    """Test copying a single bit '1'"""
    print("\n=== Test 1a: Copy Single Bit '1' ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    # Build only copy logic
    utils.add_copy_logic(transitions, 'q_start', 'q_done')

    # Create machine
    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_start', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Set input
    tm.tapes[0] = Tape(blank, "1#")

    # Expected step matrix
    expected_steps = [
        # Step, State, T1_pos, T1_char, T2_pos, T2_char, T3_pos, T3_char
        (0, 'q_start', 0, '1', 0, '#', 0, '#'),
        (1, 'q_start', 1, '#', 1, '#', 0, '#'),
    ]

    print("\nStep | State      | T1[pos]='char' | T2[pos]='char' | T3[pos]='char' | Status")
    print("-----|------------|----------------|----------------|----------------|--------")

    for step, exp_state, exp_t1_pos, exp_t1_char, exp_t2_pos, exp_t2_char, exp_t3_pos, exp_t3_char in expected_steps:
        # Get actual state
        act_state = tm.current_state
        act_t1_pos = tm.tapes[0].head
        act_t1_char = tm.tapes[0].read()
        act_t2_pos = tm.tapes[1].head
        act_t2_char = tm.tapes[1].read()
        act_t3_pos = tm.tapes[2].head
        act_t3_char = tm.tapes[2].read()

        # Check match
        match = (act_state == exp_state and
                 act_t1_pos == exp_t1_pos and act_t1_char == exp_t1_char and
                 act_t2_pos == exp_t2_pos and act_t2_char == exp_t2_char and
                 act_t3_pos == exp_t3_pos and act_t3_char == exp_t3_char)

        status = "✅" if match else "❌"

        print(f"{step:4d} | {act_state:10s} | T1[{act_t1_pos}]='{act_t1_char}' {' ' * (8-len(str(act_t1_pos)))} | "
              f"T2[{act_t2_pos}]='{act_t2_char}' {' ' * (8-len(str(act_t2_pos)))} | "
              f"T3[{act_t3_pos}]='{act_t3_char}' {' ' * (8-len(str(act_t3_pos)))} | {status}")

        if not match:
            print(f"     EXPECTED: {exp_state:10s} | T1[{exp_t1_pos}]='{exp_t1_char}' | "
                  f"T2[{exp_t2_pos}]='{exp_t2_char}' | T3[{exp_t3_pos}]='{exp_t3_char}'")
            return False

        # Step forward
        if not tm.step_forward():
            break

    # Final state verification
    final_state = tm.current_state
    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)

    print(f"\n✅ Final State: {final_state}")
    print(f"✅ T1 Head Position: {tm.tapes[0].head} (expected: 2, after separator)")
    print(f"✅ T2 Head Position: {tm.tapes[1].head} (expected: 0, at LSB)")
    print(f"✅ T2 Content: '{t2_content}' (expected: '1')")

    assert final_state == 'q_done', f"Expected q_done, got {final_state}"
    assert tm.tapes[0].head == 2, f"T1 head should be at 2, got {tm.tapes[0].head}"
    assert tm.tapes[1].head == 0, f"T2 head should be at 0, got {tm.tapes[1].head}"
    assert t2_content == '1', f"T2 should contain '1', got '{t2_content}'"

    print("\n✅ TEST PASSED\n")
    return True


def test_copy_multi_bit():
    """Test copying multi-bit number '101' (5 in binary)"""
    print("\n=== Test 1b: Copy Multi-Bit '101' ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_copy_logic(transitions, 'q_start', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_start', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    tm.tapes[0] = Tape(blank, "101#")

    # Expected step matrix
    expected_steps = [
        (0, 'q_start', 0, '1', 0, '#', 0, '#'),
        (1, 'q_start', 1, '0', 1, '#', 0, '#'),
        (2, 'q_start', 2, '1', 2, '#', 0, '#'),
        (3, 'q_start', 3, '#', 3, '#', 0, '#'),
    ]

    print("\nStep | State      | T1[pos]='char' | T2[pos]='char' | T3[pos]='char' | Status")
    print("-----|------------|----------------|----------------|----------------|--------")

    for step, exp_state, exp_t1_pos, exp_t1_char, exp_t2_pos, exp_t2_char, exp_t3_pos, exp_t3_char in expected_steps:
        act_state = tm.current_state
        act_t1_pos = tm.tapes[0].head
        act_t1_char = tm.tapes[0].read()
        act_t2_pos = tm.tapes[1].head
        act_t2_char = tm.tapes[1].read()
        act_t3_pos = tm.tapes[2].head
        act_t3_char = tm.tapes[2].read()

        match = (act_state == exp_state and
                 act_t1_pos == exp_t1_pos and act_t1_char == exp_t1_char and
                 act_t2_pos == exp_t2_pos and act_t2_char == exp_t2_char and
                 act_t3_pos == exp_t3_pos and act_t3_char == exp_t3_char)

        status = "✅" if match else "❌"

        print(f"{step:4d} | {act_state:10s} | T1[{act_t1_pos}]='{act_t1_char}' {' ' * (8-len(str(act_t1_pos)))} | "
              f"T2[{act_t2_pos}]='{act_t2_char}' {' ' * (8-len(str(act_t2_pos)))} | "
              f"T3[{act_t3_pos}]='{act_t3_char}' {' ' * (8-len(str(act_t3_pos)))} | {status}")

        if not match:
            print(f"     EXPECTED: {exp_state:10s} | T1[{exp_t1_pos}]='{exp_t1_char}' | "
                  f"T2[{exp_t2_pos}]='{exp_t2_char}' | T3[{exp_t3_pos}]='{exp_t3_char}'")
            return False

        if not tm.step_forward():
            break

    # Final verification
    final_state = tm.current_state
    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)

    print(f"\n✅ Final State: {final_state}")
    print(f"✅ T1 Head Position: {tm.tapes[0].head} (expected: 4)")
    print(f"✅ T2 Head Position: {tm.tapes[1].head} (expected: 2, at LSB)")
    print(f"✅ T2 Content: '{t2_content}' (expected: '101')")

    assert final_state == 'q_done', f"Expected q_done, got {final_state}"
    assert tm.tapes[0].head == 4, f"T1 head should be at 4, got {tm.tapes[0].head}"
    assert tm.tapes[1].head == 2, f"T2 head should be at 2 (LSB), got {tm.tapes[1].head}"
    assert t2_content == '101', f"T2 should contain '101', got '{t2_content}'"

    print("\n✅ TEST PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 1: COPY LOGIC")
    print("="*70)

    try:
        test_copy_single_bit()
        test_copy_multi_bit()

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
