import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from turing_machine import MultiTapeTuringMachine, Tape, SimulationLogger
import tm_logic_utils as utils

BLANK = '#'


class TestShiftLogic(unittest.TestCase):
    def setUp(self):
        self.alphabet = ['0', '1', BLANK]
        self.s_shift = 'q_shift_t2'
        self.s_next = 'q_mul_next_bit_t1'
        self.log_path = "add_shift_logic_test.txt"

    def run_shift(self, t2_val, t1_char='1'):
        transitions = {}
        utils.add_shift_logic(transitions, self.s_shift, self.s_next)

        tm = MultiTapeTuringMachine(
            states=[self.s_shift, self.s_next],
            alphabet=self.alphabet,
            start_state=self.s_shift,
            accept_states=[self.s_next],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        tm.tapes[0] = Tape(BLANK, t1_char)
        tm.tapes[1] = Tape(BLANK, t2_val)
        tm.tapes[2] = Tape(BLANK, BLANK)

        # LOGGING ENABLED:
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- TEST: Shift ('{t2_val}' -> '{t2_val}0') ---\n")
            SimulationLogger.log_tapes(tm, f)
            while tm.current_state != self.s_next and tm.step < 100:
                SimulationLogger.log_state(tm, f)
                if not tm.step_forward():
                    break
            SimulationLogger.log_state(tm, f)
            SimulationLogger.log_tapes(tm, f)
        return tm

    def test_single_shift(self):
        # 101 -> 1010
        tm = self.run_shift("101")
        res2 = "".join(tm.tapes[1].data[i] for i in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[i] != BLANK)
        self.assertEqual(res2, "1010")
        # Check T1 head moved left (from 0 to -1)
        self.assertEqual(tm.tapes[0].head, -1)

    def test_empty_shift(self):
        # Should not happen in logic, but test robustness: # -> 0
        tm = self.run_shift("")
        res2 = "".join(tm.tapes[1].data[i] for i in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[i] != BLANK)
        self.assertEqual(res2, "0")

if __name__ == '__main__':
    # Clear log file before starting tests
    if os.path.exists("add_shift_logic_test.txt"):
        os.remove("add_shift_logic_test.txt")
    unittest.main()
