"""
Test 3: Binary Addition Logic (add_binary_addition_logic)

Tests that T3 = T3 + T2 works correctly with carry handling.
"""

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils


def test_addition_simple():
    """Test simple addition: 1 + 1 = 10 (binary)"""
    print("\n=== Test 3a: Addition 1 + 1 = 10 ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    # Build addition logic
    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_add_setup', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 = "1", T3 = "1"
    tm.tapes[1] = Tape(blank, "1")  # T2[0] = '1'
    tm.tapes[2] = Tape(blank, "1")  # T3[0] = '1'
    tm.tapes[0].head = 0
    tm.tapes[1].head = 0  # Start at LSB
    tm.tapes[2].head = 0  # Start at LSB

    print(f"\nInitial State:")
    print(f"  T2: '1' at position [0]")
    print(f"  T3: '1' at position [0]")
    print(f"  Expected: T3 = '10' (1+1=2 in binary)")

    # Run
    max_steps = 50
    steps = 0
    while tm.current_state not in ['q_done'] and steps < max_steps:
        if steps % 5 == 0:
            print(f"Step {steps}: State={tm.current_state:15s}, T2[{tm.tapes[1].head}]='{tm.tapes[1].read()}', T3[{tm.tapes[2].head}]='{tm.tapes[2].read()}'")

        if not tm.step_forward():
            print(f"HALTED at step {steps}")
            break
        steps += 1

    # Extract T3 content
    t3_content = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T3 Content: '{t3_content}'")

    # The addition writes carry to negative positions
    # 1 + 1 = 10 (binary), stored as position [-1]='1', position [0]='0'
    # When sorted and concatenated: '10'
    assert t3_content == '10', f"T3 should contain '10' (2 in binary), got '{t3_content}'"

    print("\n✅ TEST PASSED\n")
    return True


def test_addition_with_carry():
    """Test addition with carry: 11 + 1 = 100 (binary)"""
    print("\n=== Test 3b: Addition 11 + 1 = 100 (3+1=4) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_add_setup', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 = "1", T3 = "11"
    tm.tapes[1] = Tape(blank, "1")   # T2[0] = '1'
    tm.tapes[2] = Tape(blank, "11")  # T3[0]='1', T3[1]='1'
    tm.tapes[1].head = 0
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T2: '1'  (1 in binary)")
    print(f"  T3: '11' (3 in binary, LSB-first)")
    print(f"  Expected: T3 = '100' (4 in binary, LSB-first: '001')")

    max_steps = 50
    steps = 0
    while tm.current_state not in ['q_done'] and steps < max_steps:
        if steps % 5 == 0:
            print(f"Step {steps}: State={tm.current_state:15s}, T2[{tm.tapes[1].head}]='{tm.tapes[1].read()}', T3[{tm.tapes[2].head}]='{tm.tapes[2].read()}'")

        if not tm.step_forward():
            break
        steps += 1

    t3_content = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T3 Content: '{t3_content}'")

    # 11 + 1 = 100 (binary 4)
    assert t3_content == '100', f"T3 should contain '100' (4 in binary), got '{t3_content}'"

    print("\n✅ TEST PASSED\n")
    return True


def test_addition_different_lengths():
    """Test addition with different length numbers: 101 + 11 = 1000"""
    print("\n=== Test 3c: Addition 101 + 11 = 1000 (5+3=8) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_add_setup', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 = "11" (3), T3 = "101" (5)
    tm.tapes[1] = Tape(blank, "11")   # T2: positions [0]='1', [1]='1'
    tm.tapes[2] = Tape(blank, "101")  # T3: positions [0]='1', [1]='0', [2]='1'
    tm.tapes[1].head = 0
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T2: '11'  (3 in binary)")
    print(f"  T3: '101' (5 in binary)")
    print(f"  Expected: T3 = '1000' (8 in binary)")

    max_steps = 50
    steps = 0
    while tm.current_state not in ['q_done'] and steps < max_steps:
        if steps % 5 == 0:
            t2_pos = tm.tapes[1].head
            t3_pos = tm.tapes[2].head
            print(f"Step {steps}: State={tm.current_state:15s}, T2[{t2_pos}]='{tm.tapes[1].read()}', T3[{t3_pos}]='{tm.tapes[2].read()}'")

        if not tm.step_forward():
            break
        steps += 1

    t3_content = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T3 Content: '{t3_content}'")

    # 5 + 3 = 8 = 1000 in binary, LSB-first: positions [-1,0,1,2] = ['1','0','0','0'] but negative positions might vary
    # Let's check the value instead
    if len(t3_content) == 0:
        print("❌ T3 is empty!")
        return False

    # Convert MSB-first binary to decimal to verify
    value = int(t3_content, 2) if t3_content else 0
    print(f"✅ T3 Decimal Value: {value} (expected: 8)")

    assert value == 8, f"T3 should represent 8, got {value}"

    print("\n✅ TEST PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 3: BINARY ADDITION LOGIC")
    print("="*70)

    try:
        test_addition_simple()
        test_addition_with_carry()
        test_addition_different_lengths()

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
