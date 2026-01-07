import os
from turing_machine import MultiTapeTuringMachine, Tape, SimulationLogger, TuringEncoder
import tm_logic_utils as utils


def main():
    # --- Configuration ---
    blank = '#'
    alphabet = ['0', '1', blank]
    input_str = "10#11#"  # 2 * 3 = 6 (110 binary)
    output_file = "final_simulation.txt"
    num_tapes = 3
    transitions = {}

    # --- MACHINE ARCHITECTURE (Unified State Names) ---

    # 1. COPY: First number x1 from T1 to T2
    # State: q_start -> q_look_for_next
    utils.add_copy_logic(transitions, 'q_start', 'q_look_for_next')

    # 2. NAVIGATION: Find next factor on T1
    # If we find a bit, lock onto it. If we hit end (blank), we're done.
    for b2 in alphabet:
        for b3 in alphabet:
            # Look for start of next number (skip separators)
            transitions[('q_look_for_next', (blank, b2, b3))] = ('q_look_for_next', (blank, b2, b3), ('R', 'S', 'S'))

            # If we find a bit, switch to finding end of this number
            for bit in ['0', '1']:
                transitions[('q_look_for_next', (bit, b2, b3))] = ('q_seek_factor_end', (bit, b2, b3), ('S', 'S', 'S'))

    # 3. POSITIONING: Navigate to end of current number on T1 (LSB for multiplication)
    for b1 in ['0', '1']:
        for b2 in alphabet:
            for b3 in alphabet:
                transitions[('q_seek_factor_end', (b1, b2, b3))] = ('q_seek_factor_end', (b1, b2, b3), ('R', 'S', 'S'))

    # Hit blank after number -> move back 1 position to last bit
    for b2 in alphabet:
        for b3 in alphabet:
            transitions[('q_seek_factor_end', (blank, b2, b3))] = ('q_mul_select', (blank, b2, b3), ('L', 'S', 'S'))

    # 4. MULTIPLICATION CORE (Tested blocks)
    # q_mul_select -> (q_add_setup | q_shift_t2 | q_transfer)
    utils.add_multiplication_logic(transitions, 'q_mul_select', 'q_add_setup', 'q_shift_t2', 'q_transfer')

    # Addition: q_add_setup -> q_shift_t2
    utils.add_binary_addition_logic(transitions, 'q_add_setup', 'q_shift_t2')

    # Shift: q_shift_t2 -> q_mul_next_bit
    utils.add_shift_logic(transitions, 'q_shift_t2', 'q_mul_next_bit')

    # 5. DECISION AFTER BIT: Is there another bit to the left in current number?
    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                # Another bit exists -> return to operation selection
                transitions[('q_mul_next_bit', (bit, b2, b3))] = ('q_mul_select', (bit, b2, b3), ('S', 'S', 'S'))
            # Factor exhausted (we're at separator before the factor we just finished)
            # Skip forward past this factor before transfer
            transitions[('q_mul_next_bit', (blank, b2, b3))] = ('q_skip_factor', (blank, b2, b3), ('R', 'S', 'S'))

    # 5b. SKIP PAST COMPLETED FACTOR: Move T1 right until we pass the factor we just processed
    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                # Still on the factor, keep moving right
                transitions[('q_skip_factor', (bit, b2, b3))] = ('q_skip_factor', (bit, b2, b3), ('R', 'S', 'S'))
            # Hit blank after the factor -> check if there's more input
            # Move right one more time to see if there's another factor
            transitions[('q_skip_factor', (blank, b2, b3))] = ('q_check_more_factors', (blank, b2, b3), ('R', 'S', 'S'))

    # 5c. CHECK IF MORE FACTORS EXIST: After skipping past completed factor, check next position
    for b2 in alphabet:
        for b3 in alphabet:
            for bit in ['0', '1']:
                # Found another factor! Transfer current result then process it
                transitions[('q_check_more_factors', (bit, b2, b3))] = ('q_transfer', (bit, b2, b3), ('S', 'S', 'S'))
            # Only blanks ahead -> no more factors, we're done!
            # Transfer result and terminate
            transitions[('q_check_more_factors', (blank, b2, b3))] = ('q_transfer_final', (blank, b2, b3), ('S', 'S', 'S'))

    # 5d. FINAL TRANSFER: T3 -> T2 then go to q_final
    # Manually implement with UNIQUE state names (cannot reuse add_result_transfer_logic due to hardcoded states)
    # Step 1: Home T3
    for b1 in alphabet:
        for b2 in alphabet:
            for b3 in ['0', '1']:
                transitions[('q_transfer_final', (b1, b2, b3))] = ('q_transfer_final', (b1, b2, b3), ('S', 'S', 'L'))
            transitions[('q_transfer_final', (b1, b2, blank))] = ('q_final_t2_home', (b1, b2, blank), ('S', 'L', 'S'))

    # Step 2: Home T2
    for b1 in alphabet:
        for b2 in ['0', '1']:
            transitions[('q_final_t2_home', (b1, b2, blank))] = ('q_final_t2_home', (b1, b2, blank), ('S', 'L', 'S'))
        transitions[('q_final_t2_home', (b1, blank, blank))] = ('q_final_clear', (b1, blank, blank), ('S', 'R', 'S'))

    # Step 3: CLEAR T2 completely
    for b1 in alphabet:
        for b2 in ['0', '1']:
            for b3 in alphabet:
                transitions[('q_final_clear', (b1, b2, b3))] = ('q_final_clear', (b1, blank, b3), ('S', 'R', 'S'))
        for b3 in alphabet:
            transitions[('q_final_clear', (b1, blank, b3))] = ('q_final_rehome', (b1, blank, b3), ('S', 'L', 'S'))

    # Step 4: Return T2 to home position
    for b1 in alphabet:
        for b3 in alphabet:
            for b2 in ['0', '1']:
                transitions[('q_final_rehome', (b1, b2, b3))] = ('q_final_rehome', (b1, b2, b3), ('S', 'L', 'S'))
            transitions[('q_final_rehome', (b1, blank, b3))] = ('q_final_copy', (b1, blank, b3), ('S', 'R', 'R'))

    # Step 5: Copy T3 -> T2 and erase T3
    for b1 in alphabet:
        for b3 in ['0', '1']:
            for b2 in alphabet:
                transitions[('q_final_copy', (b1, b2, b3))] = ('q_final_copy', (b1, b3, blank), ('S', 'R', 'R'))
        for b2 in alphabet:
            transitions[('q_final_copy', (b1, b2, blank))] = ('q_final', (b1, b2, blank), ('S', 'L', 'S'))

    # 6. TRANSFER & LOOP: T3 -> T2 and look for next number
    # q_transfer -> q_look_for_next
    utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_look_for_next')

    # 7. TERMINATION: Final state reached after q_transfer_final completes
    # No additional transitions needed - q_final is accept state

    # --- RUN SIMULATION ---
    states = list(set([k[0] for k in transitions.keys()]) | {'q_final'})
    tm = MultiTapeTuringMachine(states, alphabet, 'q_start', ['q_final'], blank, num_tapes)

    for (state, symbols), (next_state, next_symbols, moves) in transitions.items():
        tm.add_transition(state, symbols, next_state, next_symbols, moves)

    tm.tapes[0] = Tape(blank, input_str)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"N-ary multiplication of: {input_str}\n\n")

        SimulationLogger.log_tapes(tm, f)

        max_steps = 1000
        while tm.current_state != 'q_final' and tm.step < max_steps:
            if tm.step % 10 == 0:
                print(f"Step {tm.step}: State={tm.current_state}, T1_Head={tm.tapes[0].head}, T1_Char='{tm.tapes[0].read()}'")

                SimulationLogger.log_state(tm, f)
            if tm.current_state in ['q_mul_select', 'q_shift_t2', 'q_add_finish']:
                # Debug: print T2 and T3 contents at key states
                t2_data = {k: tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank}
                t3_data = {k: tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != blank}
                f.write(f"  DEBUG: T2={t2_data}, T3={t3_data}\n")
            if not tm.step_forward():
                # Read symbols under heads directly from tapes
                current_symbols = tuple(tape.read() for tape in tm.tapes)
                f.write(f"\nHALTED: No rule for state {tm.current_state} with symbols {current_symbols}\n")
                break

        SimulationLogger.log_state(tm, f)
        SimulationLogger.log_tapes(tm, f)

        if tm.current_state == 'q_final':
            f.write("\nCOMPUTATION COMPLETE\n")
            # Final result extraction from T2
            res = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != blank)
            f.write(f"RESULT ON TAPE 2: {res}\n")
            f.write(f"\nENCODED MACHINE:\n{TuringEncoder(tm).encode()}")

    print(f"Simulation finished. Result: {res if 'res' in locals() else 'Error'}. Check {output_file}")


if __name__ == "__main__":
    main()