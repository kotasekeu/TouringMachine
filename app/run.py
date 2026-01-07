"""
run.py
================================================================================
Main Entry Point for Binary N-ary Multiplication using Multi-Tape Turing Machine

This script composes the complete state machine for multiplying an arbitrary
number of binary numbers using the shift-and-add algorithm. It combines logic
blocks from tm_logic_utils.py into a complete multiplication machine.

Algorithm Flow:
    1. COPY: Copy first factor x₁ from T1 to T2
    2. LOOP for each remaining factor xᵢ:
       a. NAVIGATE: Find start of next factor on T1
       b. POSITION: Move to LSB of factor
       c. MULTIPLY: For each bit (LSB to MSB):
          - If bit=1: Add T2 to T3, then shift T2 left
          - If bit=0: Just shift T2 left
       d. TRANSFER: Move result T3 → T2
    3. TERMINATE: Final transfer and halt

Input Format:
    x₁ # x₂ # x₃ # ... # xₙ #
    Binary numbers separated by '#' symbols
    Example: "101#10#11#" represents 5 × 2 × 3

Output:
    Binary product written to T2
    Example: "11110" represents 30 in binary

State Machine Architecture:
    The machine uses ~20 states organized into logical phases:
    - Copy phase: q_start → q_look_for_next
    - Navigation phase: q_look_for_next → q_seek_factor_end → q_mul_select
    - Multiplication phase: q_mul_select ↔ q_add_setup/q_shift_t2 ↔ q_mul_next_bit
    - Skip/check phase: q_skip_factor → q_check_more_factors
    - Transfer phase: q_transfer → q_look_for_next (loop) or q_transfer_final → q_final (done)

Output Files:
    - final_simulation.txt: Complete execution trace with tape visualizations
    - machine_definition.txt: Machine encoding in binary and JSON formats

Author: Generated for CS Theory Project
Date: 2026-01-07
================================================================================
"""

import os
from turing_machine import MultiTapeTuringMachine, Tape, SimulationLogger, TuringEncoder
import tm_logic_utils as utils


# ============================================================================
# MAIN FUNCTION - State Machine Assembly and Execution
# ============================================================================

def main():
    """
    Assemble and execute the n-ary binary multiplication Turing Machine.

    This function:
    1. Configures machine parameters (alphabet, input, logging)
    2. Composes all logic blocks into a complete state machine
    3. Runs the simulation with detailed logging
    4. Extracts and reports the final result
    5. Saves machine definition for analysis

    Configuration:
        - Input: Defined by input_str (binary numbers separated by #)
        - Output: Written to final_simulation.txt
        - Machine definition: Written to machine_definition.txt
        - Logging: Configurable step granularity and debug info
    """

    # ========================================================================
    # CONFIGURATION SECTION
    # ========================================================================

    blank = '#'                                    # Blank symbol and separator
    alphabet = ['0', '1', blank]                   # Binary alphabet
    input_str = "101#10#110#"                      # Input: 5×2×6 = 60
    output_file = "final_simulation.txt"           # Execution trace output
    machine_file = "machine_definition.txt"        # Machine encoding output
    num_tapes = 3                                  # T1=input, T2=working, T3=accumulator
    transitions = {}                               # Transition table (initially empty)

    # ========================================================================
    # STATE MACHINE COMPOSITION - Unified Architecture
    # ========================================================================
    # The state machine is built by combining tested logic blocks from
    # tm_logic_utils.py with custom navigation and control flow.

    # ------------------------------------------------------------------------
    # PHASE 1: INITIALIZATION - Copy first factor to T2
    # ------------------------------------------------------------------------
    # Copy first number x₁ from T1 to T2 (establishes initial product).
    # States: q_start → q_look_for_next
    #
    # Example: Input "101#10#" → T2 becomes "101" (5 in binary)

    utils.add_copy_logic(transitions, 'q_start', 'q_look_for_next')

    # ------------------------------------------------------------------------
    # PHASE 2: NAVIGATION - Find next factor on T1
    # ------------------------------------------------------------------------
    # After copy or transfer, T1 head may be at separator or between factors.
    # Navigate to start of next factor (skip blanks, lock onto first bit).
    #
    # States: q_look_for_next → q_seek_factor_end
    #
    # Example: T1 = "###10#11#" with head at pos 0
    #          → Skip 3 blanks, find '1' at pos 3

    for b2 in alphabet:
        for b3 in alphabet:
            # Look for start of next factor (skip separator blanks)
            # Keep moving T1 right while reading blanks
            transitions[('q_look_for_next', (blank, b2, b3))] = (
                'q_look_for_next',
                (blank, b2, b3),
                ('R', 'S', 'S')  # Only T1 moves right
            )

            # Found start of next factor (first bit '0' or '1')
            # Switch to positioning mode to find LSB
            for bit in ['0', '1']:
                transitions[('q_look_for_next', (bit, b2, b3))] = (
                    'q_seek_factor_end',
                    (bit, b2, b3),
                    ('S', 'S', 'S')  # Lock onto this bit
                )

    # ------------------------------------------------------------------------
    # PHASE 3: POSITIONING - Navigate to LSB of current factor
    # ------------------------------------------------------------------------
    # We found the start of the factor (MSB), but shift-and-add processes
    # bits from LSB to MSB. Move T1 right to find the rightmost bit.
    #
    # States: q_seek_factor_end → q_mul_select
    #
    # Example: T1 at '1' of "101#", move right through "101" → hit blank
    #          → move back left 1 position to LSB ('1' at position 2)

    for b1 in ['0', '1']:
        for b2 in alphabet:
            for b3 in alphabet:
                # Move T1 right through all bits of current factor
                transitions[('q_seek_factor_end', (b1, b2, b3))] = (
                    'q_seek_factor_end',
                    (b1, b2, b3),
                    ('R', 'S', 'S')  # Only T1 moves right
                )

    # Hit blank after factor → overshot by 1, move back to LSB
    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_seek_factor_end', (blank, b2, b3))] = (
                'q_mul_select',
                (blank, b2, b3),
                ('L', 'S', 'S')  # T1 moves left to last bit (LSB)
            )

    # ------------------------------------------------------------------------
    # PHASE 4: MULTIPLICATION CORE - Shift-and-Add Algorithm
    # ------------------------------------------------------------------------
    # Process each bit of current factor from LSB to MSB using shift-and-add.
    # For each bit:
    #   - If bit=1: Add T2 to T3, then shift T2 left (multiply by 2)
    #   - If bit=0: Just shift T2 left
    #
    # This implements: result = Σ(bit_i × T2 × 2^i) for i from 0 to n-1

    # Multiplication decision logic: q_mul_select → (q_add_setup | q_shift_t2 | q_transfer)
    # Based on current T1 bit:
    #   - '1' → add_setup (add T2 to T3, then shift)
    #   - '0' → shift_t2 (just shift, skip addition)
    #   - '#' → transfer (factor complete)
    utils.add_multiplication_logic(transitions, 'q_mul_select', 'q_add_setup',
                                    'q_shift_t2', 'q_transfer')

    # Binary addition: q_add_setup → q_shift_t2
    # Implements T3 := T3 + T2 using full-adder logic
    # Phases: Setup (position heads) → Add (with carry) → Normalize (Bug Fix #5)
    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_shift_t2')

    # Shift left: q_shift_t2 → q_mul_next_bit
    # Implements T2 := T2 × 2 by appending '0' at LSB
    # Example: T2="101" (5) → T2="1010" (10)
    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    # ------------------------------------------------------------------------
    # PHASE 5: BIT NAVIGATION - Move to next bit or complete factor
    # ------------------------------------------------------------------------
    # After processing current bit (add+shift or just shift), move to next bit.
    # T1 head is at current bit after shift. Check left (toward MSB) for more bits.
    #
    # States: q_mul_next_bit → (q_mul_select | q_skip_factor)

    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                # Another bit exists to the left → process it
                transitions[('q_mul_next_bit', (bit, b2, b3))] = (
                    'q_mul_select',
                    (bit, b2, b3),
                    ('S', 'S', 'S')  # Stay on this bit, let mul_select handle it
                )

            # Hit separator → factor exhausted
            # Current position is the separator BEFORE the factor we just finished
            # Need to skip forward past this factor before checking for more
            transitions[('q_mul_next_bit', (blank, b2, b3))] = (
                'q_skip_factor',
                (blank, b2, b3),
                ('R', 'S', 'S')  # Move T1 right past separator
            )

    # ------------------------------------------------------------------------
    # PHASE 5b: SKIP COMPLETED FACTOR
    # ------------------------------------------------------------------------
    # After finishing a factor, T1 is at the separator before it.
    # Move T1 right through the entire factor to position after it.
    #
    # States: q_skip_factor → q_check_more_factors
    #
    # Why needed: When processing factor from LSB→MSB, we end at MSB but need
    # to be positioned AFTER the factor to check for next one.

    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                # Still inside factor, keep moving right through bits
                transitions[('q_skip_factor', (bit, b2, b3))] = (
                    'q_skip_factor',
                    (bit, b2, b3),
                    ('R', 'S', 'S')  # Only T1 moves right
                )

            # Hit blank after factor → moved past it
            # Advance one more position to check next position
            transitions[('q_skip_factor', (blank, b2, b3))] = (
                'q_check_more_factors',
                (blank, b2, b3),
                ('R', 'S', 'S')  # Move right to peek at next position
            )

    # ------------------------------------------------------------------------
    # PHASE 5c: CHECK FOR MORE FACTORS
    # ------------------------------------------------------------------------
    # After skipping past completed factor, check if another factor exists.
    # Current T1 position is one past the separator after completed factor.
    #
    # States: q_check_more_factors → (q_transfer | q_transfer_final)
    #
    # Decision:
    #   - Found bit → more factors exist, transfer and continue
    #   - Found blank → end of input, final transfer and terminate

    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                # Found another factor! Transfer current result (T3→T2) then process it
                transitions[('q_check_more_factors', (bit, b2, b3))] = (
                    'q_transfer',
                    (bit, b2, b3),
                    ('S', 'S', 'S')  # Stay, let transfer handle positioning
                )

            # Only blanks ahead → no more factors, computation complete!
            # Perform final transfer (T3→T2) and go to accept state
            transitions[('q_check_more_factors', (blank, b2, b3))] = (
                'q_transfer_final',
                (blank, b2, b3),
                ('S', 'S', 'S')  # Stay for final transfer
            )

    # ------------------------------------------------------------------------
    # PHASE 5d: FINAL TRANSFER - Last T3→T2 transfer before termination
    # ------------------------------------------------------------------------
    # After processing all factors, transfer final result from T3 to T2.
    # This is similar to regular transfer but goes to q_final instead of looping.
    #
    # States: q_transfer_final → ... → q_final_copy → q_final
    #
    # Cannot reuse add_result_transfer_logic() because it has hardcoded state names.
    # Manually implement with unique state names for final transfer sequence.
    #
    # Algorithm (identical to regular transfer, see Bug Fix #4):
    #   1. Home T3 (move to leftmost data)
    #   2. Home T2 (move to leftmost data)
    #   3. CLEAR T2 completely (critical for correctness)
    #   4. Rehome T2 (return to leftmost position)
    #   5. Copy T3 → T2 and erase T3

    # Step 1: Home T3 - Move T3 head left to leftmost data
    for b1 in alphabet:
        for b2 in alphabet:
            for b3 in ['0', '1']:
                # Move T3 left through data
                transitions[('q_transfer_final', (b1, b2, b3))] = (
                    'q_transfer_final',
                    (b1, b2, b3),
                    ('S', 'S', 'L')  # Only T3 moves left
                )

            # Hit blank on T3 → at leftmost, proceed to home T2
            transitions[('q_transfer_final', (b1, b2, blank))] = (
                'q_final_t2_home',
                (b1, b2, blank),
                ('S', 'L', 'S')  # Start moving T2 left
            )

    # Step 2: Home T2 - Move T2 head left to leftmost data
    for b1 in alphabet:
        for b2 in ['0', '1']:
            # Move T2 left through data
            transitions[('q_final_t2_home', (b1, b2, blank))] = (
                'q_final_t2_home',
                (b1, b2, blank),
                ('S', 'L', 'S')  # Only T2 moves left
            )

        # Both tapes at home (leftmost) → begin clearing T2
        transitions[('q_final_t2_home', (b1, blank, blank))] = (
            'q_final_clear',
            (b1, blank, blank),
            ('S', 'R', 'S')  # Move T2 right to start clearing
        )

    # Step 3: CLEAR T2 completely (Bug Fix #4 - prevent residual data)
    for b1 in alphabet:
        for b2 in ['0', '1']:
            for b3 in alphabet:
                # Overwrite any bit on T2 with blank
                transitions[('q_final_clear', (b1, b2, b3))] = (
                    'q_final_clear',
                    (b1, blank, b3),  # Write blank to T2
                    ('S', 'R', 'S')   # Move T2 right to continue clearing
                )

        # T2 cleared (hit blank) → return T2 to home position
        for b3 in alphabet:
            transitions[('q_final_clear', (b1, blank, b3))] = (
                'q_final_rehome',
                (b1, blank, b3),
                ('S', 'L', 'S')  # Move T2 left to rehome
            )

    # Step 4: Rehome T2 - Return T2 to leftmost position for copy
    for b1 in alphabet:
        for b3 in alphabet:
            for b2 in ['0', '1']:
                # Safety check - should not happen after clearing
                transitions[('q_final_rehome', (b1, b2, b3))] = (
                    'q_final_rehome',
                    (b1, b2, b3),
                    ('S', 'L', 'S')  # Keep moving T2 left
                )

            # At home (blank on T2) → ready to copy
            transitions[('q_final_rehome', (b1, blank, b3))] = (
                'q_final_copy',
                (b1, blank, b3),
                ('S', 'R', 'R')  # Position both T2 and T3 for copy
            )

    # Step 5: Copy T3 → T2 and erase T3
    for b1 in alphabet:
        for b3 in ['0', '1']:
            for b2 in alphabet:
                # Copy bit from T3 to T2, erase T3 by writing blank
                transitions[('q_final_copy', (b1, b2, b3))] = (
                    'q_final_copy',
                    (b1, b3, blank),  # Write T3 bit to T2, blank to T3
                    ('S', 'R', 'R')   # Move both right for next bit
                )

        # T3 exhausted (hit blank) → transfer complete, go to accept state
        for b2 in alphabet:
            transitions[('q_final_copy', (b1, b2, blank))] = (
                'q_final',
                (b1, b2, blank),
                ('S', 'L', 'S')  # Position T2 at LSB for output
            )

    # ------------------------------------------------------------------------
    # PHASE 6: REGULAR TRANSFER - Move intermediate result T3→T2 and loop
    # ------------------------------------------------------------------------
    # After completing a factor (but not the last one), transfer accumulated
    # result from T3 to T2 for multiplication with next factor.
    #
    # States: q_transfer → ... → q_transfer_copy → q_look_for_next (loop back)

    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_look_for_next')

    # ------------------------------------------------------------------------
    # PHASE 7: TERMINATION
    # ------------------------------------------------------------------------
    # q_final is the accept state. No transitions needed.
    # Machine halts when it reaches q_final, result is in T2.

    # ========================================================================
    # SIMULATION EXECUTION
    # ========================================================================

    # Extract all states from transitions (including q_final which has no outgoing transitions)
    states = list(set([k[0] for k in transitions.keys()]) | {'q_final'})

    # Create Turing Machine instance
    tm = MultiTapeTuringMachine(
        states=states,
        alphabet=alphabet,
        start_state='q_start',
        accept_states=['q_final'],
        blank=blank,
        num_tapes=num_tapes
    )

    # Load all transitions into machine
    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    # Initialize T1 with input string, T2 and T3 remain blank
    tm.tapes[0] = Tape(blank, input_str)

    # ========================================================================
    # EXECUTION LOOP WITH LOGGING
    # ========================================================================

    with open(output_file, "w", encoding="utf-8") as f:
        # Header
        f.write(f"N-ary multiplication of: {input_str}\n\n")

        # Initial tape state (step 0)
        SimulationLogger.log_tapes(tm, f)

        # Safety limit to prevent infinite loops
        max_steps = 10000

        # Main execution loop: run until accept state or max steps
        while tm.current_state != 'q_final' and tm.step < max_steps:
            # Log state transition details
            SimulationLogger.log_state(tm, f)

            # Execute one step
            if not tm.step_forward():
                # No valid transition found → unexpected halt
                current_symbols = tuple(tape.read() for tape in tm.tapes)
                f.write(f"\nHALTED: No rule for state {tm.current_state} "
                       f"with symbols {current_symbols}\n")
                break

            # Log tape states after each step
            SimulationLogger.log_tapes(tm, f)

        # Log final state
        SimulationLogger.log_state(tm, f)
        SimulationLogger.log_tapes(tm, f)

        # ====================================================================
        # RESULT EXTRACTION AND REPORTING
        # ====================================================================

        if tm.current_state == 'q_final':
            f.write("\nCOMPUTATION COMPLETE\n")

            # Extract result from T2 (non-blank symbols in sorted order)
            res = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys())
                         if tm.tapes[1].data[k] != blank)
            f.write(f"RESULT ON TAPE 2: {res}\n")

            # Convert to decimal for verification
            if res:
                decimal_result = int(res, 2)
                f.write(f"RESULT IN DECIMAL: {decimal_result}\n")

            # Write machine definition to separate file
            with open(machine_file, "w", encoding="utf-8") as mf:
                # Binary encoding (unary-based)
                mf.write("=" * 80 + "\n")
                mf.write("MACHINE ENCODING (BINARY UNARY FORMAT)\n")
                mf.write("=" * 80 + "\n\n")
                mf.write(f"{TuringEncoder(tm).encode_binary()}\n\n")

                # JSON encoding (human-readable)
                mf.write("=" * 80 + "\n")
                mf.write("MACHINE ENCODING (JSON FORMAT)\n")
                mf.write("=" * 80 + "\n\n")
                mf.write(f"{TuringEncoder(tm).encode()}\n")

            f.write(f"\nMachine definition written to {machine_file}\n")
            f.write(f"Total steps executed: {tm.step}\n")

    # Final console output (minimal)
    print(f"Simulation finished. Result: {res if 'res' in locals() else 'Error'}")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
