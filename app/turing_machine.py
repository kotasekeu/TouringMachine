"""
turing_machine.py
================================================================================
Core implementation of a Multi-Tape Turing Machine simulator for binary
multiplication using the shift-and-add algorithm.

This file provides the foundational classes for:
1. Tape - Infinite tape data structure
2. MultiTapeTuringMachine - State machine execution engine
3. TuringEncoder - Binary and JSON encoding of machine definitions
4. SimulationLogger - Logging and visualization utilities

The actual multiplication logic is defined in tm_logic_utils.py and composed
in run.py. This file contains only the generic TM infrastructure.

Author: Generated for CS Theory Project
Date: 2026-01-07
================================================================================
"""

import os
import json
from collections import defaultdict


# ============================================================================
# CONSTANTS - Global configuration for the Turing Machine
# ============================================================================

# Alphabet: Binary digits plus blank symbol
ALPHABET = ['0', '1', '#']  # '0', '1' for binary, '#' for blank/separator
BLANK = '#'                 # Blank/empty cell symbol
NUM_TAPES = 3               # Number of tapes used in multiplication (T1=input, T2=working, T3=accumulator)


# ============================================================================
# TAPE CLASS - Infinite tape data structure
# ============================================================================

class Tape:
    """
    Represents an infinite bi-directional tape for a Turing Machine.

    Uses a dictionary-based sparse storage model where only non-blank cells
    are stored in memory, allowing the tape to extend infinitely in both
    directions without memory constraints.

    Key Features:
    - Infinite extension in both directions (positive and negative indices)
    - Sparse storage: only non-blank symbols consume memory
    - Zero-indexed: initial content starts at position 0
    - Default blank symbol for uninitialized cells

    Storage Format Example:
        Input: "101"
        Storage: {0: '1', 1: '0', 2: '1'}
        Positions [-∞...0...2...+∞] all read as '#' except stored positions

    Attributes:
        blank (str): The blank/empty symbol (default '#')
        data (defaultdict): Sparse storage of non-blank symbols {position: symbol}
        head (int): Current read/write head position (can be negative)
    """

    def __init__(self, blank_symbol='#', initial_content=""):
        """
        Initialize a new tape with optional initial content.

        Args:
            blank_symbol (str): Symbol representing empty/blank cells (default '#')
            initial_content (str): Initial data to write starting at position 0

        Example:
            tape = Tape('#', "101")
            # Creates tape with '1' at pos 0, '0' at pos 1, '1' at pos 2
        """
        self.blank = blank_symbol
        self.data = defaultdict(lambda: self.blank)  # Uninitialized cells return blank
        self.head = 0  # Start at position 0

        # Load initial content starting at position 0
        for i, char in enumerate(initial_content):
            self.data[i] = char

    def read(self) -> str:
        """
        Read the symbol at the current head position.

        Returns:
            str: Symbol at current head position (blank if never written)

        Note: Reading an uninitialized position returns the blank symbol.
        """
        return self.data[self.head]

    def write(self, symbol: str):
        """
        Write a symbol to the current head position.

        Args:
            symbol (str): Symbol to write (must be in alphabet or blank)

        Note: Writing the blank symbol effectively "erases" the cell.
        """
        self.data[self.head] = symbol

    def move(self, direction: str):
        """
        Move the tape head one position in the specified direction.

        Args:
            direction (str): One of:
                'R' - Move right (increment head position)
                'L' - Move left (decrement head position)
                'S' - Stay (no movement)

        Examples:
            head=5, move('R') → head=6
            head=5, move('L') → head=4
            head=5, move('S') → head=5
            head=0, move('L') → head=-1 (tape extends into negative positions)
        """
        if direction == 'R':
            self.head += 1
        elif direction == 'L':
            self.head -= 1
        # 'S' (Stay) results in no movement

    def get_bounds(self):
        """
        Calculate the current extent of the tape based on data and head position.

        Returns:
            tuple: (min_position, max_position)
                min_position (int): Leftmost position with data or head position
                max_position (int): Rightmost position with data or head position

        This is useful for visualization to determine what range of the tape
        to display without showing infinite blank cells.

        Example:
            data = {0: '1', -2: '0', 5: '1'}, head = 3
            → returns (-2, 5)

        Note: If tape is completely blank (no data), returns (0, 0).
        """
        if not self.data:
            return 0, 0
        keys = self.data.keys()
        return min(min(keys), self.head), max(max(keys), self.head)


# ============================================================================
# MULTI-TAPE TURING MACHINE CLASS - Core execution engine
# ============================================================================

class MultiTapeTuringMachine:
    """
    Deterministic Multi-Tape Turing Machine simulator.

    Implements a standard k-tape TM with:
    - Finite set of states
    - Finite alphabet (including blank symbol)
    - Transition function δ: Q × Σ^k → Q × Σ^k × {L,R,S}^k
    - Start state and accept states
    - Multiple independent tapes with synchronized transitions

    Computational Model:
    1. At each step, read one symbol from each tape
    2. Look up transition: (current_state, (symbol1, symbol2, ...))
    3. Write new symbols to each tape
    4. Move each tape head independently (L/R/S)
    5. Transition to next state
    6. Halt if no transition exists or accept state reached

    This implementation uses:
    - Dictionary-based transition table for O(1) lookup
    - Sparse tape storage (only non-blank cells stored)
    - Step counter for complexity analysis

    Attributes:
        states (list): Sorted list of all states
        alphabet (list): Sorted list of all symbols (including blank)
        start_state (str): Initial state
        accept_states (set): Set of accepting/halting states
        blank (str): Blank symbol (default '#')
        num_tapes (int): Number of tapes (default 3 for multiplication)
        transitions (dict): Transition function table
        current_state (str): Current machine state
        tapes (list[Tape]): List of tape objects
        step (int): Number of transitions executed
    """

    def __init__(self, states, alphabet, start_state, accept_states, blank='#', num_tapes=3):
        """
        Initialize a new Multi-Tape Turing Machine.

        Args:
            states (iterable): Collection of state names (will be sorted)
            alphabet (iterable): Collection of symbols (will be sorted)
            start_state (str): Initial state name
            accept_states (iterable): Collection of accepting state names
            blank (str): Blank/empty symbol (default '#')
            num_tapes (int): Number of tapes (default 3)

        Example:
            tm = MultiTapeTuringMachine(
                states=['q0', 'q1', 'q_final'],
                alphabet=['0', '1', '#'],
                start_state='q0',
                accept_states=['q_final'],
                num_tapes=2
            )
        """
        # Machine definition
        self.states = sorted(list(states))
        self.alphabet = sorted(list(alphabet))
        self.start_state = start_state
        self.accept_states = set(accept_states)
        self.blank = blank
        self.num_tapes = num_tapes

        # Transition table: {(state, (sym1, sym2, ...)) → (next_state, (write1, write2, ...), (move1, move2, ...))}
        self.transitions = {}

        # Current execution state
        self.current_state = start_state
        self.tapes = [Tape(blank) for _ in range(num_tapes)]
        self.step = 0  # Computational step counter

    def add_transition(self, curr_state, read_symbols, next_state, write_symbols, moves):
        """
        Add a transition rule to the machine's transition function.

        Transition Format:
            δ(curr_state, (read1, read2, ...)) = (next_state, (write1, write2, ...), (move1, move2, ...))

        Args:
            curr_state (str): Current state name
            read_symbols (tuple): Tuple of symbols read from each tape (length = num_tapes)
            next_state (str): Next state name
            write_symbols (tuple): Tuple of symbols to write to each tape (length = num_tapes)
            moves (tuple): Tuple of head movements for each tape, one of:
                'L' - Move left
                'R' - Move right
                'S' - Stay in place

        Example:
            # Transition: In state 'q0', if T1='1' and T2='#',
            # write '1' to T1, '1' to T2, move both right, go to 'q1'
            tm.add_transition('q0', ('1', '#'), 'q1', ('1', '1'), ('R', 'R'))

        Note:
            - All tuples must have length equal to num_tapes
            - Duplicate transitions will overwrite previous definitions
            - No validation is performed on state/symbol names
        """
        self.transitions[(curr_state, tuple(read_symbols))] = (next_state, write_symbols, moves)

    def step_forward(self):
        """
        Execute a single computational step of the Turing Machine.

        Execution Sequence:
        1. Read current symbol from each tape
        2. Look up transition for (current_state, symbols)
        3. If no transition exists, halt and return False
        4. Write new symbols to each tape (at current head positions)
        5. Move each tape head according to transition
        6. Update current state
        7. Increment step counter
        8. Return True to indicate successful step

        Returns:
            bool: True if transition executed successfully, False if halted
                  (no valid transition for current configuration)

        Side Effects:
            - Modifies tape contents
            - Moves tape heads
            - Changes current_state
            - Increments step counter

        Example:
            while tm.step_forward():
                print(f"Step {tm.step}: {tm.current_state}")
            print("Halted")
        """
        # Read current symbols from all tapes
        current_read = tuple(t.read() for t in self.tapes)
        key = (self.current_state, current_read)

        # Look up transition
        if key not in self.transitions:
            return False  # Halt: no valid transition found

        # Extract transition components
        next_state, writes, moves = self.transitions[key]

        # Execute transition: write, move, and change state
        self.current_state = next_state
        for i in range(self.num_tapes):
            self.tapes[i].write(writes[i])  # Write symbol to tape i
            self.tapes[i].move(moves[i])    # Move head on tape i

        self.step += 1
        return True


# ============================================================================
# TURING ENCODER CLASS - Machine encoding/serialization
# ============================================================================

class TuringEncoder:
    """
    Encodes Turing Machine definitions into binary or JSON formats.

    Provides two encoding schemes:
    1. Binary encoding - Standard unary encoding for theoretical analysis
    2. JSON encoding - Human-readable serialization for storage/debugging

    Binary Encoding Scheme (Unary-Based):
        States: q_i → 0^(i+1)     (e.g., q0='0', q1='00', q2='000')
        Symbols: a_j → 0^(i+1)    (e.g., '#'='0', '0'='00', '1'='000')
        Moves: L='0', R='00', S='000'

        Transition format: state_in|syms_in|state_out|syms_out|moves
        Separator: '1' within transitions, '11' between transitions

        Example (simplified 1-tape):
            δ(q0, 'a') = (q1, 'b', R)
            Encoded: "0|0|00|00|00" = "010000000"

    JSON Encoding Scheme:
        Human-readable dictionary with all machine components:
        - states, alphabet, start_state, accept_states
        - transition list with explicit labels

    Attributes:
        m (MultiTapeTuringMachine): Machine to encode
        state_map (dict): State name → unary string mapping
        alpha_map (dict): Symbol → unary string mapping
        move_map (dict): Direction → unary string mapping
    """

    def __init__(self, machine: MultiTapeTuringMachine):
        """
        Initialize encoder for a given Turing Machine.

        Args:
            machine (MultiTapeTuringMachine): Machine to encode

        Note:
            State and alphabet ordering is based on sorted order,
            affecting the unary encoding indices.
        """
        self.m = machine

        # Create unary mappings (index-based)
        self.state_map = {s: '0' * (i + 1) for i, s in enumerate(self.m.states)}
        self.alpha_map = {a: '0' * (i + 1) for i, a in enumerate(self.m.alphabet)}
        self.move_map = {'L': '0', 'R': '00', 'S': '000'}

    def encode_binary(self) -> str:
        """
        Encode machine as a binary string using unary representation.

        Returns:
            str: Binary-encoded machine (unary + separators)

        Format per transition:
            state_in '1' symbols_in '1' state_out '1' symbols_out '1' moves

        Multiple transitions separated by '11'.

        Example:
            For 3-tape machine with transition:
            δ(q_start, ('1', '#', '#')) = (q_start, ('1', '1', '#'), ('R', 'R', 'S'))

            If q_start is 0th state (='0') and symbols map as:
            '#'='0', '0'='00', '1'='000'

            Then encoded as:
            "0 | 000,0,0 | 0 | 000,000,0 | 00,00,000"
            (without spaces, with '1' separators)

        Note:
            This encoding is primarily for theoretical analysis (e.g., Kolmogorov complexity).
            For practical use, prefer JSON encoding.
        """
        encoded_rules = []

        for (q_curr, symbols_read), (q_next, symbols_write, moves) in self.m.transitions.items():
            # Encode each component using unary representation
            parts = [
                self.state_map[q_curr],                    # Current state
                *[self.alpha_map[s] for s in symbols_read],  # Input symbols (all tapes)
                self.state_map[q_next],                    # Next state
                *[self.alpha_map[s] for s in symbols_write], # Output symbols (all tapes)
                *[self.move_map[m] for m in moves]         # Head movements (all tapes)
            ]
            # Join parts with '1' separator within transition
            encoded_rules.append("1".join(parts))

        # Join transitions with '11' separator
        return "11".join(encoded_rules)

    def encode(self) -> str:
        """
        Encode machine as a human-readable JSON string.

        Returns:
            str: JSON-formatted machine definition

        JSON Structure:
        {
            "states": [...],
            "alphabet": [...],
            "start_state": "...",
            "accept_states": [...],
            "blank": "...",
            "num_tapes": N,
            "transitions": [
                {
                    "current_state": "...",
                    "read_symbols": [...],
                    "next_state": "...",
                    "write_symbols": [...],
                    "moves": [...]
                },
                ...
            ]
        }

        Use Cases:
            - Saving machine configurations to disk
            - Debugging transition tables
            - Sharing machine definitions
            - Visualization tools
        """
        # Convert transitions from dict to list of explicit records
        transitions_list = []
        for (q_curr, symbols_read), (q_next, symbols_write, moves) in self.m.transitions.items():
            transitions_list.append({
                "current_state": q_curr,
                "read_symbols": list(symbols_read),
                "next_state": q_next,
                "write_symbols": list(symbols_write),
                "moves": list(moves)
            })

        # Build complete machine definition
        machine_def = {
            "states": self.m.states,
            "alphabet": self.m.alphabet,
            "start_state": self.m.start_state,
            "accept_states": list(self.m.accept_states),
            "blank": self.m.blank,
            "num_tapes": self.m.num_tapes,
            "transitions": transitions_list
        }

        return json.dumps(machine_def, indent=2)


# ============================================================================
# SIMULATION LOGGER CLASS - Logging and visualization utilities
# ============================================================================

class SimulationLogger:
    """
    Static utility class for logging Turing Machine execution.

    Provides formatted output for:
    1. Tape visualization with dynamic windowing
    2. State transition logging with read/write details

    All methods are static and take a machine instance as parameter.
    Output is written to file handles for persistence.
    """

    @staticmethod
    def log_tapes(machine, file):
        """
        Log visual representation of all tapes with current state and head positions.

        Output Format (per step):
            Step N (current_state)
            T1 [pos:  X]: ########101##10##
                                   ^
            T2 [pos:  Y]: ######10#########
                                ^
            T3 [pos:  Z]: ####################
                          ^
            ----------------------------------------

        Args:
            machine (MultiTapeTuringMachine): Machine to visualize
            file: File handle for output (must support write())

        Features:
            - Dynamic window sizing: Only shows relevant tape regions
            - Head position indicator: '^' marks current head location
            - Position labels: Shows absolute head position on tape
            - Context padding: Includes cells around data and heads

        Implementation:
            - Scans all tapes to find min/max positions with data
            - Expands window to include head positions ± padding
            - Default window: positions -2 to 6 if no data exists
            - Displays only computed window range, hiding infinite blanks
        """
        file.write(f"Step {machine.step} ({machine.current_state})\n")

        # Calculate dynamic window boundaries based on tape content and head positions
        min_pos = -2  # Default minimum (handles carry bits in negative positions)
        max_pos = 6   # Default maximum

        # Scan all tapes to find actual data extent
        for tape in machine.tapes:
            if tape.data:
                # Find positions with non-blank data
                data_positions = [k for k in tape.data.keys() if tape.data[k] != machine.blank]
                if data_positions:
                    # Expand window to include:
                    # - Leftmost data position (with padding)
                    # - Current head position (with padding)
                    min_pos = min(min_pos, min(data_positions) - 1, tape.head - 2)
                    max_pos = max(max_pos, max(data_positions) + 2, tape.head + 4)

        # Create range for display window
        r = range(min_pos, max_pos)

        # Display each tape
        for i, tape in enumerate(machine.tapes):
            # Build tape content string for window
            line = "".join(tape.data.get(j, machine.blank) for j in r)

            # Build head position indicator (arrow line)
            arrow = [" "] * len(r)
            if tape.head in r:
                arrow[tape.head - r.start] = "^"

            # Write tape contents and head indicator
            file.write(f"T{i+1} [pos:{tape.head:3}]: {line}\n")
            file.write(f"              {''.join(arrow)}\n")

        file.write("-" * 40 + "\n")

    @staticmethod
    def log_state(machine: MultiTapeTuringMachine, file):
        """
        Log the current state and transition being executed.

        Output Format:
            Step N (current_state): Read (sym1,sym2,sym3) -> Write (sym1,sym2,sym3), Move (dir1,dir2,dir3), Next: next_state

        Or if no transition exists:
            Step N (current_state): Read (sym1,sym2,sym3) -> HALT (No transition)

        Args:
            machine (MultiTapeTuringMachine): Machine to log
            file: File handle for output (must support write())

        Details Logged:
            - Current step number
            - Current state name
            - Symbols read from each tape
            - Symbols to be written to each tape
            - Head movement directions for each tape
            - Next state to transition to
            - HALT indication if no valid transition

        Note:
            This logs the transition *before* it is executed,
            showing what *will* happen in the next step.
        """
        # Read current symbols from all tapes
        current_read = tuple(t.read() for t in machine.tapes)
        key = (machine.current_state, current_read)

        if key in machine.transitions:
            # Transition exists - log full details
            next_state, writes, moves = machine.transitions[key]
            read_str = ",".join(current_read)
            write_str = ",".join(writes)
            move_str = ",".join(moves)
            file.write(
                f"Step {machine.step} ({machine.current_state}): "
                f"Read ({read_str}) -> Write ({write_str}), "
                f"Move ({move_str}), Next: {next_state}\n"
            )
        else:
            # No transition - machine will halt
            read_str = ",".join(current_read)
            file.write(
                f"Step {machine.step} ({machine.current_state}): "
                f"Read ({read_str}) -> HALT (No transition)\n"
            )


# ============================================================================
# END OF MODULE
# ============================================================================
#
# This module provides generic Turing Machine infrastructure.
# For the actual multiplication implementation, see:
#   - tm_logic_utils.py: Logic blocks (add, shift, transfer, etc.)
#   - run.py: Main entry point and state machine composition
#
# To run tests:
#   PYTHONPATH=/path/to/app python3 tests/test_*.py
#
# To run multiplication:
#   python3 run.py
# ============================================================================