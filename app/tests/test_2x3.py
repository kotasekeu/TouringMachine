"""
Test for 2 * 3 = 6
Tests multi-bit factor processing.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_simple_1x1 import build_complete_machine


def test_2_times_3():
    """Test multiplication: 2 * 3 = 6 (binary: 10 * 11 = 110)"""
    input_str = "10#11#"
    expected = "110"

    print("\n=== Testing 2 * 3 = 6 ===")
    print(f"Input: {input_str} (binary: 10 × 11)")
    print(f"Expected: {expected} (decimal: 6)")

    # Build complete machine
    tm, blank = build_complete_machine(input_str)

    # Run simulation
    max_steps = 200
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
        print(f"Result on T2: {result} (decimal: {int(result, 2) if result else 0})")

        # ASSERTION: Check if result is correct
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print(f"✅ CORRECT: 2 * 3 = 6")
        return True
    else:
        print(f"\n❌ FAILED: Exceeded {max_steps} steps")
        print(f"Final state: {tm.current_state}")
        return False


if __name__ == "__main__":
    success = test_2_times_3()
    exit(0 if success else 1)
