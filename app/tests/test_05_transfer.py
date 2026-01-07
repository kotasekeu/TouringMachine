"""
Test 5: Transfer Logic (add_result_transfer_logic)

CRITICAL TEST: This tests T3 -> T2 transfer and should reveal the T2 clearing bug.

The bug: When transferring T3 -> T2, if T2 has bits at positions beyond T3's range
(e.g., from previous shift operations), those bits remain in T2.

Example:
- T2 = "110" (positions: [0]='1', [1]='1', [2]='0')
- T3 = "1" (position: [0]='1')
- After transfer: T2 should be "1", but might be "110" or "11" if not cleared properly
"""

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils


def test_transfer_simple():
    """Test simple transfer: T3='1' -> T2 (should completely replace T2)"""
    print("\n=== Test 5a: Transfer T3='1' to T2 (T2 empty) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    # Build transfer logic
    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_transfer', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 empty, T3 = "1"
    tm.tapes[0].head = 0
    tm.tapes[1].head = 0  # T2 empty
    tm.tapes[2] = Tape(blank, "1")  # T3[0] = '1'
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T2: (empty)")
    print(f"  T3: '1' at position [0]")
    print(f"  Expected: T2 = '1', T3 cleared")

    # Run
    max_steps = 50
    steps = 0
    print(f"\nStep-by-step execution:")
    while tm.current_state not in ['q_done'] and steps < max_steps:
        t2_pos = tm.tapes[1].head
        t3_pos = tm.tapes[2].head
        t2_sym = tm.tapes[1].read()
        t3_sym = tm.tapes[2].read()
        if steps % 5 == 0 or steps < 10:
            print(f"Step {steps}: State={tm.current_state:20s}, T2[{t2_pos}]='{t2_sym}', T3[{t3_pos}]='{t3_sym}'")

        if not tm.step_forward():
            print(f"HALTED at step {steps}")
            break
        steps += 1

    # Final state
    t2_pos = tm.tapes[1].head
    t3_pos = tm.tapes[2].head
    t2_sym = tm.tapes[1].read()
    t3_sym = tm.tapes[2].read()
    print(f"Step {steps}: State={tm.current_state:20s}, T2[{t2_pos}]='{t2_sym}', T3[{t3_pos}]='{t3_sym}'")

    # Extract tape contents
    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)
    t3_content = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank)

    print(f"\n✅ Final State: {tm.current_state}")
    print(f"✅ Steps taken: {steps}")
    print(f"✅ T2 Content: '{t2_content}'")
    print(f"✅ T3 Content: '{t3_content}' (should be empty)")

    # Verify
    assert t2_content == '1', f"T2 should contain '1', got '{t2_content}'"
    assert t3_content == '', f"T3 should be empty after transfer, got '{t3_content}'"

    print("\n✅ TEST PASSED\n")
    return True


def test_transfer_with_residue():
    """
    CRITICAL TEST: T2 has residual data from previous operations.
    This is where the bug should appear!

    Setup:
    - T2 = "110" (positions: [0]='1', [1]='1', [2]='0')
    - T3 = "1" (position: [0]='1')

    Expected: T2 = "1" (T3 data only, old T2 data cleared)
    Bug behavior: T2 = "110" or "11" (old data remains)
    """
    print("\n=== Test 5b: Transfer with T2 Residue (CRITICAL BUG TEST) ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_transfer', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 has residual "110" from previous shift, T3 = "1"
    tm.tapes[0].head = 0
    tm.tapes[1] = Tape(blank, "110")  # T2 has leftover data
    tm.tapes[1].head = 0
    tm.tapes[2] = Tape(blank, "1")  # T3 has result "1"
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T2: '110' (residual data from previous operations)")
    print(f"  T3: '1' (new result to transfer)")
    print(f"  Expected: T2 = '1' (ONLY T3 data, T2 completely cleared)")
    print(f"  Bug: T2 = '110' or '11' (residual data remains)")

    # Run
    max_steps = 50
    steps = 0
    print(f"\nStep-by-step execution:")
    while tm.current_state not in ['q_done'] and steps < max_steps:
        t2_pos = tm.tapes[1].head
        t3_pos = tm.tapes[2].head
        t2_sym = tm.tapes[1].read()
        t3_sym = tm.tapes[2].read()
        if steps < 15:  # Show more detail for this critical test
            t2_positions = sorted([k for k in tm.tapes[1].data.keys() if tm.tapes[1].data[k] != blank])
            t2_data = {k: tm.tapes[1].data[k] for k in t2_positions} if t2_positions else {}
            print(f"Step {steps}: State={tm.current_state:20s}, T2[{t2_pos}]='{t2_sym}', T3[{t3_pos}]='{t3_sym}', T2_data={t2_data}")

        if not tm.step_forward():
            print(f"HALTED at step {steps}")
            break
        steps += 1

    # Final state
    t2_pos = tm.tapes[1].head
    t3_pos = tm.tapes[2].head
    t2_positions = sorted([k for k in tm.tapes[1].data.keys() if tm.tapes[1].data[k] != blank])
    t2_data = {k: tm.tapes[1].data[k] for k in t2_positions} if t2_positions else {}
    print(f"Step {steps}: State={tm.current_state:20s}, T2[{t2_pos}], T3[{t3_pos}], T2_data={t2_data}")

    # Extract tape contents
    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)
    t3_content = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank)

    print(f"\n{'✅' if t2_content == '1' else '❌'} Final State: {tm.current_state}")
    print(f"{'✅' if steps < 50 else '❌'} Steps taken: {steps}")
    print(f"{'✅' if t2_content == '1' else '❌'} T2 Content: '{t2_content}' (expected: '1')")
    print(f"{'✅' if t3_content == '' else '⚠️'} T3 Content: '{t3_content}' (expected: empty)")

    # This is the critical assertion that will likely FAIL due to the bug
    if t2_content != '1':
        print(f"\n🔴 BUG CONFIRMED: T2 contains '{t2_content}' instead of '1'")
        print(f"   Root cause: Transfer does not clear T2 positions beyond T3's range")
        print(f"   T2 positions before transfer: [0]='1', [1]='1', [2]='0'")
        print(f"   T3 data to transfer: [0]='1'")
        print(f"   Transfer only overwrites T2[0], leaving T2[1] and T2[2] unchanged")
        raise AssertionError(f"T2 should contain '1', got '{t2_content}'")

    assert t2_content == '1', f"T2 should contain '1', got '{t2_content}'"
    assert t3_content == '', f"T3 should be empty after transfer, got '{t3_content}'"

    print("\n✅ TEST PASSED (Bug was NOT present or already fixed!)\n")
    return True


def test_transfer_longer_data():
    """Test transfer with longer T3: T3='101' -> T2"""
    print("\n=== Test 5c: Transfer T3='101' to T2 (T2 has '1111') ===")

    blank = '#'
    alphabet = ['0', '1', blank]
    transitions = {}

    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_done')

    states = list(set([k[0] for k in transitions.keys()]) | {'q_done'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_transfer', ['q_done'], blank, 3)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Setup: T2 has "1111" (longer than T3), T3 = "101"
    tm.tapes[0].head = 0
    tm.tapes[1] = Tape(blank, "1111")  # T2 longer than T3
    tm.tapes[1].head = 0
    tm.tapes[2] = Tape(blank, "101")  # T3 = "101"
    tm.tapes[2].head = 0

    print(f"\nInitial State:")
    print(f"  T2: '1111' (4 bits, longer than T3)")
    print(f"  T3: '101' (3 bits)")
    print(f"  Expected: T2 = '101' (T2 completely replaced)")

    # Run
    max_steps = 50
    steps = 0
    while tm.current_state not in ['q_done'] and steps < max_steps:
        if not tm.step_forward():
            break
        steps += 1

    t2_content = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)
    t3_content = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank)

    print(f"\n{'✅' if t2_content == '101' else '❌'} Final State: {tm.current_state}")
    print(f"{'✅' if steps < 50 else '❌'} Steps taken: {steps}")
    print(f"{'✅' if t2_content == '101' else '❌'} T2 Content: '{t2_content}' (expected: '101')")
    print(f"{'✅' if t3_content == '' else '⚠️'} T3 Content: '{t3_content}' (expected: empty)")

    if t2_content != '101':
        print(f"\n🔴 BUG: T2 contains '{t2_content}' instead of '101'")
        print(f"   T2 had 4 bits, T3 had 3 bits - T2[3] likely remains")

    assert t2_content == '101', f"T2 should contain '101', got '{t2_content}'"
    assert t3_content == '', f"T3 should be empty after transfer, got '{t3_content}'"

    print("\n✅ TEST PASSED\n")
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TEST SUITE 5: TRANSFER LOGIC (T3 -> T2)")
    print("CRITICAL: This test should reveal the T2 clearing bug")
    print("="*70)

    try:
        test_transfer_simple()
        test_transfer_with_residue()  # Most likely to fail
        test_transfer_longer_data()   # Also likely to fail

        print("\n" + "="*70)
        print("ALL TESTS PASSED ✅")
        print("Transfer logic correctly clears T2 before copying T3!")
        print("="*70 + "\n")
        exit(0)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        print("="*70)
        print("BUG CONFIRMED: Transfer logic does NOT clear T2 properly")
        print("="*70 + "\n")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        exit(1)
