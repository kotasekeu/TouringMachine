import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from turing_machine import MultiTapeTuringMachine, Tape, SimulationLogger
import tm_logic_utils as utils

BLANK = '#'


class TestTransferLogic(unittest.TestCase):
    def setUp(self):
        self.alphabet = ['0', '1', BLANK]
        self.log_path = "add_transfer_logic_test.txt"

    def run_transfer(self, t3_val, test_name):
        transitions = {}
        utils.add_result_transfer_logic(transitions, 'q_transfer', 'q_success')

        # SEZNAM STAVŮ musí odpovídat logice v utils.py
        tm = MultiTapeTuringMachine(
            states=['q_transfer', 'q_transfer_t2_home', 'q_transfer_copy', 'q_success'],
            alphabet=self.alphabet,
            start_state='q_transfer',
            accept_states=['q_success'],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        tm.tapes[0] = Tape(BLANK, BLANK)
        # T2 má binární smetí, které chceme přepsat
        tm.tapes[1] = Tape(BLANK, "111")
        tm.tapes[2] = Tape(BLANK, t3_val)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- TEST: {test_name} (Transfer T3:'{t3_val}' -> T2) ---\n")
            SimulationLogger.log_tapes(tm, f)
            # Zvýšíme limit kroků, homing dvou pásek něco trvá
            while tm.current_state != 'q_success' and tm.step < 500:
                SimulationLogger.log_state(tm, f)
                if not tm.step_forward():
                    f.write(f"HALTED: No transition from {tm.current_state}\n")
                    break
            SimulationLogger.log_state(tm, f)
            SimulationLogger.log_tapes(tm, f)
        return tm

    # def test_result_copy_and_clear(self):
    #     tm = self.run_transfer("1010", "Full Transfer")
    #
    #     # Očista: Páska 2 musí mít 1010
    #     res2 = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != BLANK)
    #     self.assertEqual(res2, "1010")
    #
    #     # Páska 3 musí být prázdná
    #     res3 = "".join(tm.tapes[2].data[k] for k in sorted(tm.tapes[2].data.keys()) if tm.tapes[2].data[k] != BLANK)
    #     self.assertEqual(res3, "")

    def test_dirty_transfer_fail(self):
        """Simuluje stav po násobení: T1 je na separátoru, hlavy jsou rozjeté."""
        tm = self.run_transfer("1010", "Dirty Real-World Transfer")

        # Simulace reálného stavu před startem transferu:
        tm.tapes[0].head = 5  # T1 je někde uprostřed vstupu na '#'
        tm.tapes[1].head = 10  # T2 je ujetá doprava po sčítání
        tm.tapes[2].head = 4  # T3 je na konci výsledku

        # Spuštění
        while tm.current_state != 'q_success' and tm.step < 500:
            if not tm.step_forward(): break

        res2 = "".join(tm.tapes[1].data[k] for k in sorted(tm.tapes[1].data.keys()) if tm.tapes[1].data[k] != BLANK)
        self.assertEqual(res2, "1010")
        self.assertEqual(tm.current_state, 'q_success')


if __name__ == '__main__':
    # Clear log file before starting tests
    if os.path.exists("add_transfer_logic_test.txt"):
        os.remove("add_transfer_logic_test.txt")
    unittest.main()
