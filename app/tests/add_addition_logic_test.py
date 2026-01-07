import sys
import os
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from turing_machine import MultiTapeTuringMachine, Tape, SimulationLogger
import tm_logic_utils as utils

BLANK = '#'


class TestAdditionLogic(unittest.TestCase):
    def setUp(self):
        self.alphabet = ['0', '1', BLANK]
        self.s_setup = 'q_add_setup'
        self.s_success = 'q_add_success'
        self.log_path = "add_addition_logic_test.txt"

    def run_addition(self, t2_val, t3_val, test_name):
        transitions = {}
        utils.add_binary_addition_logic(transitions, self.s_setup, self.s_success)

        tm = MultiTapeTuringMachine(
            states=[self.s_setup, self.s_success, 'q_add_c0', 'q_add_c1', 'q_add_finish'],
            alphabet=self.alphabet,
            start_state=self.s_setup,
            accept_states=[self.s_success],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        # Páska 1 je při sčítání irelevantní, ale musí tam být BLANK
        tm.tapes[0] = Tape(BLANK, BLANK)
        tm.tapes[1] = Tape(BLANK, t2_val)
        tm.tapes[2] = Tape(BLANK, t3_val)

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- TEST: {test_name} ({t2_val} + {t3_val}) ---\n")
            SimulationLogger.log_tapes(tm, f)
            while tm.current_state != self.s_success and tm.step < 200:
                SimulationLogger.log_state(tm, f)
                if not tm.step_forward():
                    f.write(f"HALTED at {tm.current_state}\n")
                    break
            SimulationLogger.log_state(tm, f)
            SimulationLogger.log_tapes(tm, f)
        return tm

    def test_zero_addition(self):
        # # + 101 = 101
        tm = self.run_addition("", "101", "Add to empty")
        res = "".join(tm.tapes[2].data[i] for i in range(3))
        self.assertEqual(res, "101")

    def get_tape_content(self, tape):
        # Reads all non-blank symbols from tape dictionary and joins them
        keys = sorted(tape.data.keys())
        return "".join(tape.data[k] for k in keys if tape.data[k] != BLANK)

    def test_simple_carry(self):
        tm = self.run_addition("1", "1", "Simple Carry")
        self.assertEqual(tm.current_state, self.s_success)
        res = self.get_tape_content(tm.tapes[2])
        self.assertEqual(res, "10")

    def test_different_lengths(self):
        tm = self.run_addition("111", "1", "Longer T2")
        res = self.get_tape_content(tm.tapes[2])
        self.assertEqual(res, "1000")

    def test_infinite_left_regression(self):
        """
        TEST: Zda sčítání korektně zastaví na začátku čísel a neuteče do nekonečna vlevo.
        Vstup: 1 + 1 (LSB). Po 2 krocích by mělo být hotovo.
        """
        # Nastavíme limit velmi nízko, abychom poznali zacyklení okamžitě
        max_steps_limit = 20
        tm = self.run_addition("1", "1", "Infinite Left Regression")

        # Simulace s nízkým limitem
        steps = 0
        while tm.current_state != self.s_success and steps < max_steps_limit:
            if not tm.step_forward():
                break
            steps += 1

        # Pokud stroj dojel na limit, znamená to, že se neustále hýbe L
        self.assertLess(steps, max_steps_limit, "Stroj se zacyklil v pohybu doleva!")
        self.assertEqual(tm.current_state, self.s_success)

    def test_dirty_t1_addition_fail(self):
        """Simuluje sčítání, když je na T1 symbol '1' (střed násobení)."""
        tm = self.run_addition("1", "1", "Dirty T1 Addition")

        # Simulace: Na T1 je '1' místo BLANK
        tm.tapes[0].data[0] = '1'

        steps = 0
        while tm.current_state != self.s_success and steps < 50:
            if not tm.step_forward(): break
            steps += 1

        # TADY TO SELŽE: steps bude 50 (limit), protože stroj uteče doleva
        self.assertLess(steps, 50, "Sčítání se zacyklilo kvůli symbolu na T1!")

    def test_repro_infinite_loop(self):
        """
        Tento test REPRODUKUJE chybu z main.py.
        Sčítání nesmí pokračovat doleva, pokud jsou T2 a T3 prázdné,
        i když je na T1 jakýkoliv symbol.
        """
        # 1. Setup stroje
        transitions = {}
        utils.add_binary_addition_logic(transitions, 'q_setup', 'q_success')
        tm = MultiTapeTuringMachine(
            states=['q_setup', 'q_success', 'q_add_c0', 'q_add_c1', 'q_add_finish'],
            alphabet=utils.ALPHABET,
            start_state='q_add_c0',  # Skočíme přímo do sčítání
            accept_states=['q_success'],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        # 2. KLÍČOVÝ STAV:
        # T2 a T3 jsou už na BLANK (vlevo od čísel),
        # ale T1 stále ukazuje na '1' (protože hlava T1 se při sčítání nehýbe).
        tm.tapes[0].data[0] = '1'
        tm.tapes[1].data[0] = utils.BLANK
        tm.tapes[2].data[0] = utils.BLANK

        # Nastavíme hlavy na index 0
        for i in range(3): tm.tapes[i].head = 0

        # 3. Spuštění s limitem
        max_steps = 100
        step = 0
        while tm.current_state != 'q_success' and step < max_steps:
            if not tm.step_forward():
                break
            step += 1

        # Pokud sčítání funguje správně, mělo by hned v prvním kroku
        # rozpoznat (BLANK, BLANK) a jít do finish/success.
        # Pokud step == max_steps, REPRODUKOVALI JSME CHYBU.
        self.assertLess(step, max_steps, f"CHYBA REPRODUKOVÁNA: Stroj se zacyklil ve stavu {tm.current_state}!")

    def test_repro_dirty_t2_loop(self):
        """
        Tento test simuluje 'nekonečnou nulu' na Pásce 2.
        Pokud sčítání narazí na 0 na T2 a BLANK na T3, nesmí generovat novou 0 na T3
        a posouvat se doleva donekonečna.
        """
        transitions = {}
        utils.add_binary_addition_logic(transitions, 'q_setup', 'q_success')
        tm = MultiTapeTuringMachine(
            states=['q_setup', 'q_success', 'q_add_c0', 'q_add_c1', 'q_add_finish'],
            alphabet=utils.ALPHABET,
            start_state='q_add_c0',
            accept_states=['q_success'],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        # KONFIGURACE Z LOGU:
        tm.tapes[0].data[0] = '1'  # T1: '1'
        tm.tapes[1].data[0] = '0'  # T2: '0' (Tady je ten problém!)
        tm.tapes[2].data[0] = utils.BLANK  # T3: '#'

        for i in range(3): tm.tapes[i].head = 0

        max_steps = 100
        step = 0
        while tm.current_state != 'q_success' and step < max_steps:
            if not tm.step_forward():
                break
            step += 1

        # Pokud step dosáhne max_steps, stroj se zacyklil v sčítání nul.
        self.assertLess(step, max_steps, f"CHYBA: Stroj v q_add_c0 sčítá nuly do nekonečna!")

    def test_repro_dirty_t3_persistence(self):
        """
        Simuluje stav, kdy na T3 jsou staré nuly daleko vlevo.
        Sčítání musí skončit na BLANK, i když vlevo od něj jsou nuly.
        """
        transitions = {}
        utils.add_binary_addition_logic(transitions, 'q_setup', 'q_success')
        tm = MultiTapeTuringMachine(
            states=['q_setup', 'q_success', 'q_add_c0', 'q_add_c1', 'q_add_finish'],
            alphabet=utils.ALPHABET,
            start_state='q_add_c0',
            accept_states=['q_success'],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        # KONFIGURACE:
        # Hlava je na indexu 0, kde jsou BLANKY.
        # Ale na indexu -1, -2 jsou '0'. Uteče tam stroj?
        tm.tapes[0].data[0] = '1'
        tm.tapes[1].data[0] = utils.BLANK
        tm.tapes[2].data[0] = utils.BLANK

        # "Špína" vlevo
        tm.tapes[2].data[-1] = '0'
        tm.tapes[2].data[-2] = '0'

        for i in range(3): tm.tapes[i].head = 0

        # LOGOVÁNÍ DO SOUBORU
        with open("repro_test_log.txt", "w", encoding="utf-8") as f:
            f.write("--- REPRO TEST: Dirty T3 ---\n")
            step = 0
            while tm.current_state != 'q_success' and step < 50:
                # Logujeme akci
                symbols = tuple(t.read() for t in tm.tapes)
                f.write(f"Step {step} ({tm.current_state}): Read {symbols}\n")
                if not tm.step_forward():
                    f.write(f"HALTED at {tm.current_state}\n")
                    break
                step += 1

        self.assertLess(step, 50, "Stroj neodolal špíně na T3 a utekl doleva!")

    def test_addition_termination(self):
        """
        Testuje, zda sčítání zastaví ihned po zpracování posledního bitu.
        """
        tm = self.run_addition("1", "1", "Termination Test")

        # Nastavíme rozumný limit kroků pro 1+1
        max_steps = 20
        step_count = 0

        # Simulujeme, dokud stroj neskončí v success_state nebo nevyčerpá kroky
        # success_state je u tebe pravděpodobně 'q_add_success' nebo 'q_mul_step_final'
        target_state = 'q_add_success'

        while tm.current_state != target_state and step_count < max_steps:
            # Pokud step_forward vrátí False, stroj zastavil (není přechod)
            if not tm.step_forward():
                break
            step_count += 1

        # 1. KONTROLA: Stroj nesmí vyčerpat limit (zacyklení)
        self.assertLess(step_count, max_steps, "REPRODUKCE CHYBY: Stroj se zacyklil a sčítá nekonečné prázdno vlevo!")

        # 2. KONTROLA: Hlava T3 nesmí být na nesmyslném indexu (např. -15)
        # Pro 1+1 začínající na 0 by měla hlava po sčítání a zápisu carry
        # být maximálně na indexu -1 nebo -2.
        self.assertGreater(tm.tapes[2].head, -3, f"Hlava utekla příliš daleko (index: {tm.tapes[2].head})")



    def test_repro_setup_alignment_fail(self):
        """
        Simuluje stav, kdy hlava T3 je už na konci, ale T2 má před sebou ještě dlouhé číslo.
        Pokud setup není robustní, skončí předčasně a sčítání začne na špatných indexech.
        """
        transitions = {}
        # Použijeme tvou ostrou metodu
        utils.add_binary_addition_logic(transitions, 'q_setup', 'q_success')

        tm = MultiTapeTuringMachine(
            states=['q_setup', 'q_success', 'q_add_c0', 'q_add_c1', 'q_add_finish'],
            alphabet=utils.ALPHABET,
            start_state='q_setup',
            accept_states=['q_success'],
            num_tapes=3
        )
        for k, v in transitions.items():
            tm.add_transition(k[0], k[1], v[0], v[1], v[2])

        # KONFIGURACE:
        # T2 má dlouhé číslo, hlava je na začátku (index 0)
        tm.tapes[1].data[0], tm.tapes[1].data[1], tm.tapes[1].data[2] = '1', '1', '1'
        tm.tapes[1].head = 0

        # T3 má krátké číslo, hlava je už na jeho konci (index 1)
        tm.tapes[2].data[0] = '1'
        tm.tapes[2].head = 0

        # Páska 1 je irelevantní
        tm.tapes[0].head = 0

        with open("repro_setup_log.txt", "w", encoding="utf-8") as f:
            f.write("--- REPRO TEST: Setup Alignment ---\n")
            step = 0
            while tm.current_state != 'q_add_c0' and step < 50:
                # TADY POUŽIJEME NOVÝ LOGGER
                SimulationLogger.log_tapes(tm, f)

                if not tm.step_forward():
                    f.write(f"HALTED at {tm.current_state}\n")
                    break
                step += 1
            # Logni i finální stav, kde to selhalo
            SimulationLogger.log_tapes(tm, f)

            # Smyčka musí běžet, dokud nejsme v q_add_c0
            while tm.current_state == 'q_setup' and step < 50:
                SimulationLogger.log_tapes(tm, f)
                tm.step_forward()
                step += 1

        # TEĎ jsme v q_add_c0. Hlavy se pohnuly o 1 vlevo (L).
        # Takže kontrolujeme, že jsou na posledních bitech.
        # Pokud T2 měla data na 0,1,2, hlava musí být na 2.
        self.assertEqual(tm.tapes[1].head, 2, "T2 hlava není na posledním bitu!")
        self.assertEqual(tm.tapes[2].head, 0, "T3 hlava není na posledním bitu!")
        self.assertEqual(tm.tapes[1].read(), '1')
        self.assertEqual(tm.tapes[2].read(), '1')

if __name__ == '__main__':
    # Clear log file before starting tests
    if os.path.exists("add_addition_logic_test.txt"):
        os.remove("add_addition_logic_test.txt")
    unittest.main()