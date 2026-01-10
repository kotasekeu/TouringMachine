class TuringDecoder:
    """
    Decoder for binary-encoded Turing machines using unary representation.

    Decodes machines encoded by TuringEncoder.encode_binary() back to
    structured format.
    """

    def __init__(self, binary_code: str):
        """
        Initialize decoder with binary string.

        Args:
            binary_code: Binary string to decode (unary format with separators)
        """
        self.binary_code = binary_code.strip()

    def decode_unary(self, unary_str: str) -> int:
        """
        Decode unary number to integer.

        Args:
            unary_str: String of '0' characters representing number

        Returns:
            int: Decoded value (count of '0' characters)

        Example:
            "000" -> 3
            "0" -> 1
            "" -> 0
        """
        return unary_str.count('0')

    def decode_binary(self) -> dict:
        """
        Decode complete Turing machine from binary string.

        Returns:
            dict: Decoded machine with structure:
                {
                    'num_tapes': int,
                    'initial_state': int,
                    'blank_symbol': int,
                    'final_states': list[int],
                    'transitions': list[dict]
                }

        Format expected:
            num_tapes '111' initial_state '111' blank_symbol '111'
            final_states '111' transitions

        Where transitions format is:
            state_in '1' symbols_in '1' state_out '1' symbols_out '1' moves

        Multiple transitions separated by '11'.
        """
        # Split major sections by '111' separator
        parts = self.binary_code.split('111')

        if len(parts) < 5:
            raise ValueError(f"Invalid encoding: expected 5 sections, got {len(parts)}")

        # 1. Decode number of tapes
        num_tapes = self.decode_unary(parts[0])

        # 2. Decode initial state
        initial_state = self.decode_unary(parts[1])

        # 3. Decode blank symbol
        blank_symbol = self.decode_unary(parts[2])

        # 4. Decode final (accepting) states
        # Empty string means no final states
        final_states = []
        if parts[3]:
            final_states = [
                self.decode_unary(state)
                for state in parts[3].split('1')
                if state
            ]

        # 5. Decode transitions
        transitions = self._decode_transitions(parts[4], num_tapes)

        return {
            'num_tapes': num_tapes,
            'initial_state': initial_state,
            'blank_symbol': blank_symbol,
            'final_states': final_states,
            'transitions': transitions
        }

    def _decode_transitions(self, transitions_str: str, num_tapes: int) -> list:
        """
        Decode transition rules from binary string.

        Args:
            transitions_str: Binary string containing all transitions
            num_tapes: Number of tapes (needed for parsing)

        Returns:
            list[dict]: List of decoded transitions, each containing:
                {
                    'current_state': int,
                    'read_symbols': list[int],
                    'next_state': int,
                    'write_symbols': list[int],
                    'moves': list[int]
                }

        Format per transition:
            state_in '1' symbols_in(×num_tapes) '1' state_out '1'
            symbols_out(×num_tapes) '1' moves(×num_tapes)
        """
        if not transitions_str:
            return []

        # Split individual transitions by '11' separator
        transitions_raw = transitions_str.split('11')
        transitions = []

        for trans_raw in transitions_raw:
            if not trans_raw:
                continue

            # Split components within single transition by '1' separator
            components = trans_raw.split('1')

            # Remove empty parts (can occur with consecutive separators)
            components = [c for c in components if c]

            # Expected number of components:
            # 1 (current_state) + num_tapes (read) + 1 (next_state) +
            # num_tapes (write) + num_tapes (moves)
            expected_components = 2 + 3 * num_tapes

            if len(components) < expected_components:
                continue  # Skip malformed transitions

            # Decode all components from unary
            decoded = [self.decode_unary(c) for c in components]

            # Parse components based on position
            idx = 0

            # Current state
            current_state = decoded[idx]
            idx += 1

            # Read symbols (one per tape)
            read_symbols = decoded[idx:idx + num_tapes]
            idx += num_tapes

            # Next state
            next_state = decoded[idx]
            idx += 1

            # Write symbols (one per tape)
            write_symbols = decoded[idx:idx + num_tapes]
            idx += num_tapes

            # Head movements (one per tape)
            moves = decoded[idx:idx + num_tapes]
            idx += num_tapes

            transitions.append({
                'current_state': current_state,
                'read_symbols': read_symbols,
                'next_state': next_state,
                'write_symbols': write_symbols,
                'moves': moves
            })

        return transitions

    def to_readable_format(self, decoded: dict,
                           state_names: dict = None,
                           symbol_names: dict = None,
                           move_names: dict = None) -> dict:
        """
        Convert decoded integers to readable format using provided mappings.

        Args:
            decoded: Decoded machine (output from decode_binary)
            state_names: Optional mapping {int: str} for state names
            symbol_names: Optional mapping {int: str} for symbol names
            move_names: Optional mapping {int: str} for move names
                       (default: {0: 'L', 1: 'R', 2: 'S'})

        Returns:
            dict: Machine with human-readable names instead of integers
        """
        # Default move mapping
        if move_names is None:
            move_names = {0: 'L', 1: 'R', 2: 'S'}

        # Helper to convert value using mapping or keep as is
        def convert(value, mapping):
            if mapping and value in mapping:
                return mapping[value]
            return f"q{value}" if isinstance(value, int) else value

        result = {
            'num_tapes': decoded['num_tapes'],
            'initial_state': convert(decoded['initial_state'], state_names),
            'blank_symbol': convert(decoded['blank_symbol'], symbol_names),
            'final_states': [
                convert(s, state_names) for s in decoded['final_states']
            ],
            'transitions': []
        }

        for t in decoded['transitions']:
            result['transitions'].append({
                'current_state': convert(t['current_state'], state_names),
                'read_symbols': [convert(s, symbol_names) for s in t['read_symbols']],
                'next_state': convert(t['next_state'], state_names),
                'write_symbols': [convert(s, symbol_names) for s in t['write_symbols']],
                'moves': [convert(m, move_names) for m in t['moves']]
            })

        return result

    def print_summary(self, decoded: dict, verbose: bool = True):
        """
        Print human-readable summary of decoded machine.

        Args:
            decoded: Decoded machine (output from decode_binary)
            verbose: If True, print all transitions; if False, just summary
        """
        print(f"Number of tapes: {decoded['num_tapes']}")
        print(f"Initial state: q{decoded['initial_state']}")
        print(f"Blank symbol: {decoded['blank_symbol']}")
        print(f"Final states: {['q' + str(s) for s in decoded['final_states']]}")
        print(f"Number of transitions: {len(decoded['transitions'])}\n")

        if verbose and decoded['transitions']:
            move_names = {0: 'L', 1: 'R', 2: 'S'}

            print("Transitions:")
            print("-" * 80)
            for i, t in enumerate(decoded['transitions'], 1):
                read_str = ','.join(map(str, t['read_symbols']))
                write_str = ','.join(map(str, t['write_symbols']))
                moves_str = ','.join(move_names.get(m, str(m)) for m in t['moves'])

                print(f"{i:3d}. δ(q{t['current_state']}, [{read_str}]) = "
                      f"(q{t['next_state']}, [{write_str}], [{moves_str}])")


# Usage examples:
if __name__ == "__main__":
    import json
    import re

    # Read binary code from file
    with open('machine_binary.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract binary code (find longest sequence of 0s and 1s)
    binary_match = re.search(r'([01]{100,})', content)

    if not binary_match:
        print("Error: No binary code found in machine.txt")
        exit(1)

    binary_code = binary_match.group(1)
    print(f"Found binary code: {len(binary_code)} bits\n")
    print("=" * 80)

    # Decode the machine
    decoder = TuringDecoder(binary_code)
    decoded = decoder.decode_binary()

    # Print summary
    decoder.print_summary(decoded, verbose=True)

    # Optional: Convert to readable format if you have the mappings
    # (You would need to extract these from the JSON section of machine.txt)
    readable = decoder.to_readable_format(decoded)

    # Save decoded machine to JSON file
    print("\n" + "=" * 80)
    print("Saving to decoded_machine.json...")
    with open('decoded_machine.json', 'w', encoding='utf-8') as f:
        json.dump(readable, f, indent=2, ensure_ascii=False)

    print("Done! Decoded machine saved to decoded_machine.json")