import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from turing_machine import MultiTapeTuringMachine, Tape
import tm_logic_utils as utils

BLANK = '#'


class TestMultiplicationLogic(unittest.TestCase):
    def setUp(self):
        self.alphabet = ['0', '1', BLANK]
        self.s_select = 'q_select'
        self.s_add = 'q_add_setup'
        self.s_shift = 'q_shift'
        self.s_transfer = 'q_transfer'

    def run_one_step(self, t1_char, t2_char=BLANK, t3_char=BLANK):
        transitions = {}
        utils.add_multiplication_logic(transitions, self.s_select, self.s_add, self.s_shift, self.s_transfer)

        tm = MultiTapeTuringMachine(
            states=[self.s_select, self.s_add, self.s_shift, self.s_transfer],
            alphabet=self.alphabet,
            start_state=self.s_select,
            accept_states=[self.s_add, self.s_shift, self.s_transfer],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        # Nastavíme hlavy na konkrétní symboly
        tm.tapes[0].data[0] = t1_char
        tm.tapes[1].data[0] = t2_char
        tm.tapes[2].data[0] = t3_char

        tm.step_forward()
        return tm

    def test_select_one(self):
        tm = self.run_one_step('1')
        self.assertEqual(tm.current_state, self.s_add)

    def test_select_zero(self):
        tm = self.run_one_step('0')
        self.assertEqual(tm.current_state, self.s_shift)

    def test_select_blank(self):
        tm = self.run_one_step(BLANK)
        self.assertEqual(tm.current_state, self.s_transfer)

    def test_ignore_other_tapes(self):
        """Klíčový test: Router musí fungovat, i když jsou na T2/T3 data."""
        # Testujeme bit '1' zatímco na T2 je '0' a na T3 je '1'
        tm = self.run_one_step('1', '0', '1')
        self.assertEqual(tm.current_state, self.s_add)

    def test_invalid_input_halt(self):
        """Pokud přijde nečekaný symbol (např. 'X'), stroj nesmí přejít nikam."""
        self.alphabet.append('X')
        tm = self.run_one_step('X')
        # Stále v select stavu (nebo Halt), neprošel do cílových stavů
        self.assertEqual(tm.current_state, self.s_select)
        self.assertEqual(tm.step, 0)  # Krok se neprovedl


if __name__ == '__main__':
    unittest.main()