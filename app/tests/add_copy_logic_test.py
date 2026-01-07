import sys
import os
import unittest

# Path setup to find modules in parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from turing_machine import MultiTapeTuringMachine, Tape, SimulationLogger
import tm_logic_utils as utils

BLANK = '#'


class TestCopyLogic(unittest.TestCase):
    def setUp(self):
        self.alphabet = ['0', '1', BLANK]
        self.start = 'q_start'
        self.success = 'q_success'
        self.log_path = "add_copy_logic_test.txt"

    def run_simulation(self, input_str, test_name):
        transitions = {}
        utils.add_copy_logic(transitions, self.start, self.success)

        tm = MultiTapeTuringMachine(
            states=[self.start, self.success],
            alphabet=self.alphabet,
            start_state=self.start,
            accept_states=[self.success],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        tm.tapes[0] = Tape(BLANK, input_str)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- RUNNING TEST: {test_name} (Input: '{input_str}') ---\n")
            SimulationLogger.log_tapes(tm, f)
            while tm.current_state != self.success and tm.step < 100:
                SimulationLogger.log_state(tm, f)
                if not tm.step_forward():
                    f.write(f"HALTED: No transition for state {tm.current_state}\n")
                    break
            SimulationLogger.log_state(tm, f)
            SimulationLogger.log_tapes(tm, f)
        return tm

    def test_standard_copy(self):
        tm = self.run_simulation("101#", "Standard Copy")
        self.assertEqual(tm.current_state, self.success)
        # Verify content on Tape 2 (using our Tape.read at specific positions)
        tm.tapes[1].head = 0
        self.assertEqual(tm.tapes[1].read(), '1')
        tm.tapes[1].head = 1
        self.assertEqual(tm.tapes[1].read(), '0')
        tm.tapes[1].head = 2
        self.assertEqual(tm.tapes[1].read(), '1')

    def test_invalid_symbol(self):
        """Negative test: Ensure machine halts on symbols not in logic."""
        # '2' is in the alphabet but NOT handled by add_copy_logic
        self.alphabet.append('2')
        tm = self.run_simulation("1021#", "Invalid Symbol Interruption")

        # Machine should halt before reaching success state
        self.assertNotEqual(tm.current_state, self.success)
        # Should stop exactly where the '2' was encountered
        self.assertEqual(tm.tapes[0].read(), '2')

    def test_empty_first_number(self):
        """Testuje případ, kdy první číslo chybí (např. '##101#')."""
        tm = self.run_simulation("##101#", "Empty First Number")
        # Očekáváme: T2 je prázdná, hlava T1 je na indexu 1 (za prvním #)
        self.assertEqual(tm.current_state, self.success)
        self.assertEqual(tm.tapes[1].read(), BLANK)
        # Důležité: Tady zjistíme, jestli se stroj nezasekl na druhém '#'

    def test_multiple_numbers_copy_only_first(self):
        """Testuje, že se zkopíruje pouze první segment dat."""
        tm = self.run_simulation("110#101#", "Copy Only First Segment")
        # Na T2 musí být '110', ale NE '101'
        res2 = "".join(tm.tapes[1].data[i] for i in range(3))
        self.assertEqual(res2, "110")
        self.assertEqual(tm.tapes[1].data[3], BLANK)  # Tady nesmí být nic víc

    def test_no_data_at_all(self):
        """Testuje úplně prázdnou pásku (jen BLANK)."""
        tm = self.run_simulation("", "Total Blank Input")
        self.assertEqual(tm.current_state, self.success)
        self.assertEqual(tm.tapes[1].read(), BLANK)


if __name__ == '__main__':
    # Clear log file before starting tests
    if os.path.exists("add_copy_logic_test.txt"):
        os.remove("add_copy_logic_test.txt")
    unittest.main()