"""
Test 4: Shift Logic (add_shift_logic)

Tests that T2 multiply by 2 (shift left = append 0) works correctly.
"""

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils


def test_shift_simple():
    """Test simple shift: 1 -> 10 (1*2=2)"""
    print("\n=== Test 4a: Shift 1 -> 10 (1*2=2) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    # Build shift logic
    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_mul_next_bit'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_shift_t2', ['q_mul_next_bit'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T1 = "1#1#" at position 2 (the '1'), T2 = "1" at position 0
    tm.tapes[0] = Tape(blank, "1#1#")
    tm.tapes[0].head = 2  # T1 at the factor '1'
    tm.tapes[1] = Tape(blank, "1")  # T2[0] = '1'
    tm.tapes[1].head = 0  # Start at LSB
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T1: '1#1#' at position [2]='1'")
    print(f"  T2: '1' at position [0]")
    print(f"  Expected: T2 = '10' (shift left = multiply by 2)")
    print(f"  Expected: T1 head moves LEFT to position 1")

    # Run
    max_steps = 50
    steps = 0
    print(f"\nStep-by-step execution:")
    while tm.current_state not in ['q_mul_next_bit'] and steps < max_steps:
        t1_pos = tm.tapes[0].head
        t2_pos = tm.tapes[1].head
        t1_sym = tm.tapes[0].read()
        t2_sym = tm.tapes[1].read()
        print(f"Step {steps}: State={tm.current_state:15s}, T1[{t1_pos}]='{t1_sym}', T2[{t2_pos}]='{t2_sym}'")

        if not tm.step_forward():
            print(f"HALTED at step {steps}")
            break
        steps += 1

    # Final state
    t1_pos = tm.tapes[0].head
    t2_pos = tm.tapes[1].head
    t1_sym = tm.tapes[0].read()
    t2_sym = tm.tapes[1].read()
    print(f"Step {steps}: State={tm.current_state:15s}, T1[{t1_pos}]='{t1_sym}', T2[{t2_pos}]='{t2_sym}'")

    # Extract T2 content
    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T2 Content: '{t2_content}'")
    print(f"✅ T1 Head Position: {tm.tapes[0].head} (expected: 1)")

    # Verify: T2 should be "10" (1 shifted left)
    assert t2_content == '10', f"T2 should contain '10' after shift, got '{t2_content}'"

    # Verify: T1 head should move LEFT from 2 to 1
    assert tm.tapes[0].head == 1, f"T1 head should be at position 1, got {tm.tapes[0].head}"

    print("\n✅ TEST PASSED\n")
    return True


def test_shift_multi_bit():
    """Test shift multi-bit: 11 -> 110 (3*2=6)"""
    print("\n=== Test 4b: Shift 11 -> 110 (3*2=6) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_mul_next_bit'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_shift_t2', ['q_mul_next_bit'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T1 at position 3, T2 = "11" at positions [0]='1', [1]='1'
    tm.tapes[0] = Tape(blank, "101#11#")
    tm.tapes[0].head = 3  # T1 at separator
    tm.tapes[1] = Tape(blank, "11")  # T2 = "11" (3 in binary)
    tm.tapes[1].head = 0
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T1: '101#11#' at position [3]")
    print(f"  T2: '11' (3 in binary)")
    print(f"  Expected: T2 = '110' (6 in binary, 3*2)")

    # Run
    max_steps = 50
    steps = 0
    while tm.current_state not in ['q_mul_next_bit'] and steps < max_steps:
        if steps % 5 == 0:
            print(f"Step {steps}: State={tm.current_state:15s}, T1[{tm.tapes[0].head}]='{tm.tapes[0].read()}', T2[{tm.tapes[1].head}]='{tm.tapes[1].read()}'")

        if not tm.step_forward():
            break
        steps += 1

    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T2 Content: '{t2_content}'")

    # Verify: 11 shifted left = 110
    assert t2_content == '110', f"T2 should contain '110', got '{t2_content}'"

    # Verify decimal value
    value = int(t2_content, 2)
    print(f"✅ T2 Decimal Value: {value} (expected: 6)")
    assert value == 6, f"T2 should represent 6, got {value}"

    print("\n✅ TEST PASSED\n")
    return True


def test_shift_with_zero():
    """Test shift: 101 -> 1010 (5*2=10)"""
    print("\n=== Test 4c: Shift 101 -> 1010 (5*2=10) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_mul_next_bit'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_shift_t2', ['q_mul_next_bit'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 = "101" (5 in binary)
    tm.tapes[0] = Tape(blank, "11#101#")
    tm.tapes[0].head = 5
    tm.tapes[1] = Tape(blank, "101")  # T2 = "101" (5 in binary)
    tm.tapes[1].head = 0
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T2: '101' (5 in binary)")
    print(f"  Expected: T2 = '1010' (10 in binary, 5*2)")

    max_steps = 50
    steps = 0
    while tm.current_state not in ['q_mul_next_bit'] and steps < max_steps:
        if steps % 5 == 0:
            print(f"Step {steps}: State={tm.current_state:15s}, T2[{tm.tapes[1].head}]='{tm.tapes[1].read()}'")

        if not tm.step_forward():
            break
        steps += 1

    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T2 Content: '{t2_content}'")

    # Verify
    assert t2_content == '1010', f"T2 should contain '1010', got '{t2_content}'"

    value = int(t2_content, 2)
    print(f"✅ T2 Decimal Value: {value} (expected: 10)")
    assert value == 10, f"T2 should represent 10, got {value}"

    print("\n✅ TEST PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 4: SHIFT LOGIC (MULTIPLY T2 BY 2)")
    print("="*70)

    try:
        test_shift_simple()
        test_shift_multi_bit()
        test_shift_with_zero()

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
