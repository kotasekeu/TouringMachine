import os
from collections import defaultdict


# Constants for the simulation
ALPHABET = ['0', '1', '#']  # Binary digits and blank
BLANK = '#'
NUM_TAPES = 3

# We will define states as we build the logic
# q_init: Start state
# q_copy_x1: Copy first number to Tape 2
# q_next_x: Move to the next number on Tape 1
# q_mul_setup: Prepare for multiplication of T2 and the new number on T1


def get_multiplication_transitions():
    t = {}
    # Current state from previous step: 'q_prepare_next'
    # Head of T1 is on the first bit of x2. Head of T2 is on the last bit of x1.

    # --- PHASE 2: Multiplication Setup ---
    # We need T1 head at the END of x2 to process from LSB to MSB.
    for b in ['0', '1']:
        t[('q_prepare_next', (b, b, BLANK))] = ('q_prepare_next', (b, b, BLANK), ('R', 'S', 'S'))

    # Once T1 hits blank or end of x2, move head back to the last digit
    t[('q_prepare_next', (BLANK, '0', BLANK))] = ('q_mul_bit', (BLANK, '0', BLANK), ('L', 'S', 'S'))
    t[('q_prepare_next', (BLANK, '1', BLANK))] = ('q_mul_bit', (BLANK, '1', BLANK), ('L', 'S', 'S'))

    # --- PHASE 3: Binary Multiplication (Bit by Bit) ---
    # If bit on T1 is '1' -> Add T2 to T3, then shift T2
    # If bit on T1 is '0' -> Just shift T2

    # Case: Bit is '1' -> Go to Add routine
    t[('q_mul_bit', ('1', BLANK, BLANK))] = ('q_start_add', ('1', BLANK, BLANK), ('S', 'S', 'S'))

    # Case: Bit is '0' -> Just shift T2 (add a zero at the end) and move to next bit of T1
    t[('q_mul_bit', ('0', BLANK, BLANK))] = ('q_shift_t2', ('0', BLANK, BLANK), ('S', 'S', 'S'))

    # (Logic for q_start_add and q_shift_t2 follows...)
    return t


# Simple Binary Addition: T3 = T3 + T2
def add_binary_transitions(t):
    # 'q_start_add' -> Heads move to the rightmost bits
    # 'q_adding' -> Performs the bitwise addition with carry

    # Carry states: q_add_c0 (carry 0), q_add_c1 (carry 1)
    # This is a standard 2-tape adder logic.

    # [Implementation simplified for brevity, but logically follows
    # the full-adder truth table mapped to TS states]
    pass

def get_initial_transitions():
    t = {}

    # --- PHASE 1: Copy x_1 to Tape 2 ---
    # Current State: 'q_start'
    # Action: Read T1, write to T2, move both Right.
    # If '#' is found on T1, it means x_1 is finished.

    # (state, (T1_char, T2_char, T3_char)) -> (next_state, (W1, W2, W3), (M1, M2, M3))

    for bit in ['0', '1']:
        t[('q_start', (bit, BLANK, BLANK))] = (
            'q_start',
            (bit, bit, BLANK),
            ('R', 'R', 'S')
        )

    # When we hit the first blank on T1, x_1 is copied.
    # Move T1 to the start of x_2 and reset T2 head to the end of its number.
    t[('q_start', (BLANK, BLANK, BLANK))] = (
        'q_prepare_next',
        (BLANK, BLANK, BLANK),
        ('R', 'L', 'S')
    )

    return t


class Tape:
    """
    Represents an infinite tape using a dictionary to store non-blank symbols.
    The head can move infinitely in both directions.
    """

    def __init__(self, blank_symbol='#', initial_content=""):
        self.blank = blank_symbol
        self.data = defaultdict(lambda: self.blank)
        self.head = 0

        for i, char in enumerate(initial_content):
            self.data[i] = char

    def read(self) -> str:
        return self.data[self.head]

    def write(self, symbol: str):
        self.data[self.head] = symbol

    def move(self, direction: str):
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        # 'S' (Stay) results in no movement

    def get_bounds(self):
        """Returns the current leftmost and rightmost non-blank indices."""
        if not self.data:
            return 0, 0
        keys = self.data.keys()
        return min(min(keys), self.head), max(max(keys), self.head)


class MultiTapeTuringMachine:
    """
    Core engine capable of simulating a Deterministic Turing Machine with k-tapes.
    """

    def __init__(self, states, alphabet, start_state, accept_states, blank='#', num_tapes=3):
        self.states = sorted(list(states))
        self.alphabet = sorted(list(alphabet))
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.blank = blank
        self.num_tapes = num_tapes
        self.transitions = {}

        self.current_state = start_state
        self.tapes = [Tape(blank) for _ in range(num_tapes)]
        self.step = 0

    def add_transition(self, curr_state, read_symbols, next_state, write_symbols, moves):
        """
        Maps (state, tuple of symbols) -> (next_state, tuple of writes, tuple of moves).
        read_symbols must be a tuple of length k.
        """
        self.transitions[(curr_state, tuple(read_symbols))] = (next_state, write_symbols, moves)

    def step_forward(self):
        """Executes a single computational step."""
        current_read = tuple(t.read() for t in self.tapes)
        key = (self.current_state, current_read)

        if key not in self.transitions:
            return False  # Halt: no valid transition

        next_state, writes, moves = self.transitions[key]

        self.current_state = next_state
        for i in range(self.num_tapes):
            self.tapes[i].write(writes[i])
            self.tapes[i].move(moves[i])

        self.step += 1
        return True


class TuringEncoder:
    """
    Encodes the machine definition into a binary string representation.
    Standard: States q_i -> 0^(i+1), Symbols a_j -> 0^(j+1), Directions L,R,S -> 0, 00, 000.
    """

    def __init__(self, machine: MultiTapeTuringMachine):
        self.m = machine
        self.state_map = {s: '0' * (i + 1) for i, s in enumerate(self.m.states)}
        self.alpha_map = {a: '0' * (i + 1) for i, a in enumerate(self.m.alphabet)}
        self.move_map = {'L': '0', 'R': '00', 'S': '000'}

    def encode(self) -> str:
        encoded_rules = []
        for (q_curr, symbols_read), (q_next, symbols_write, moves) in self.m.transitions.items():
            # Standard encoding extended for k-tapes:
            # state_in | symbols_in | state_out | symbols_out | moves
            parts = [
                self.state_map[q_curr],
                *[self.alpha_map[s] for s in symbols_read],
                self.state_map[q_next],
                *[self.alpha_map[s] for s in symbols_write],
                *[self.move_map[m] for m in moves]
            ]
            encoded_rules.append("1".join(parts))

        return "11".join(encoded_rules)


class SimulationLogger:
    @staticmethod
    def log_tapes(machine, file):
        file.write(f"Step {machine.step} ({machine.current_state})\n")
        # Dynamic window based on actual data positions
        # Find min and max positions across all tapes
        min_pos = -2
        max_pos = 6
        for tape in machine.tapes:
            if tape.data:
                data_positions = [k for k in tape.data.keys() if tape.data[k] != machine.blank]
                if data_positions:
                    min_pos = min(min_pos, min(data_positions) - 1, tape.head - 2)
                    max_pos = max(max_pos, max(data_positions) + 2, tape.head + 4)

        r = range(min_pos, max_pos)
        for i, tape in enumerate(machine.tapes):
            line = "".join(tape.data.get(j, machine.blank) for j in r)
            # Arrow at actual position within window
            arrow = [" "] * len(r)
            if tape.head in r:
                arrow[tape.head - r.start] = "^"
            file.write(f"T{i+1} [pos:{tape.head:3}]: {line}\n")
            file.write(f"              {''.join(arrow)}\n")
        file.write("-" * 40 + "\n")

    @staticmethod
    def log_state(machine: MultiTapeTuringMachine, file):
        current_read = tuple(t.read() for t in machine.tapes)
        key = (machine.current_state, current_read)

        if key in machine.transitions:
            next_state, writes, moves = machine.transitions[key]
            read_str = ",".join(current_read)
            write_str = ",".join(writes)
            move_str = ",".join(moves)
            file.write(f"Step {machine.step} ({machine.current_state}): Read ({read_str}) -> Write ({write_str}), Move ({move_str}), Next: {next_state}\n")
        else:
            read_str = ",".join(current_read)
            file.write(f"Step {machine.step} ({machine.current_state}): Read ({read_str}) -> HALT (No transition)\n")


if __name__ == "__main__":
    # Define our test machine
    # Replace states in your __main__
    states = ['q_start', 'q_prepare_next', 'q_mul_bit', 'q_final']
    transitions = get_initial_transitions()  # your existing copy logic

    # Add the "seek end of x2" logic
    for b in ['0', '1']:
        transitions[('q_prepare_next', (b, '0', BLANK))] = ('q_prepare_next', (b, '0', BLANK), ('R', 'S', 'S'))
        transitions[('q_prepare_next', (b, '1', BLANK))] = ('q_prepare_next', (b, '1', BLANK), ('R', 'S', 'S'))

    # Stop when you find the end of the input
    transitions[('q_prepare_next', (BLANK, '0', BLANK))] = ('q_final', (BLANK, '0', BLANK), ('S', 'S', 'S'))
    transitions[('q_prepare_next', (BLANK, '1', BLANK))] = ('q_final', (BLANK, '1', BLANK), ('S', 'S', 'S'))

    tm = MultiTapeTuringMachine(
        states=states,
        alphabet=ALPHABET,
        start_state='q_start',
        accept_states=['q_final'],
        num_tapes=3
    )

    # Load transitions
    for k, v in transitions.items():
        tm.add_transition(k[0], k[1], v[0], v[1], v[2])

    # Load Input: x1 = 101 (5), x2 = 10 (2) -> Result should be 1010 (10)
    # Note: Using # as separator as per your instruction (epsilon)
    input_str = "101#10#"
    tm.tapes[0] = Tape(BLANK, input_str)

    # Simulation loop
    with open("simulation_log.txt", "w", encoding="utf-8") as log_file:
        log_file.write(f"Initial Input: {input_str}\n")
        log_file.write("=" * 30 + "\n")

        SimulationLogger.log_tapes(tm, log_file)

        while tm.current_state not in tm.accept_states:
            SimulationLogger.log_state(tm, log_file)
            if not tm.step_forward():
                log_file.write("HALTED: No transition found.\n")
                break

        SimulationLogger.log_tapes(tm, log_file)
        log_file.write("\nFinal result on T2 (Accumulator) should be 101.\n")