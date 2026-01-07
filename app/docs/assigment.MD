Zadání semestrální práce
V libovolném programovacím jazyce realizujte program, který bude simulovat deterministický k-páskový Turingův stroj tak, aby bylo možno ve vašem programu definovat:

konečnou množinu stavů,

koncové stavy,

počáteční stav,

konečnou abecedu obsahující prázdný symbol,

přechodové funkce

a poskytne zakódovanou podobu simulovaného stroje.

Nechť váš program poskytne jako výstup stav pásky pro každý krok simulace a na závěr kód zakódovaného Turingova stroje viz kódování Turingova stroje.

Nechť je na začátku simulace pozice čtecí/zapisovací hlavy Turingova stroje na prvním neprázdném symbolu vstupní pásky. Pozice čtecí/zapisovací hlavy po skončení simulace není podstatná.


Vaše řešení demonstrujte vytvořením Turingova stroje realizujícího funkci fun. Nechť vstupem funkce fun je entice čísel x, které jsou kódovány v binární soustavě. Nechť jsou objekty vstupní entice odděleny prázdným symbolem ε. Nechť je funkce fun definována jako:

fun(x_1, ... x_n) = Π_{i=1}^{n} x_i


Vhodně označte vstupní a výstupní pásku. Příklad vstupu a výstupu TS pro 1 pásku:

Počáteční stav pásky: 

                                                      ↓

                                        T1: # # # # # 1 0 1 # 1 0 # 1 1 0 # # # #



Koncový stav pásky:

                                                        ↓

                                        T1: # # # # # # 1 1 1 1 0 0 # # # # # # #


Zvolte vhodnou reprezentaci TS ve vašem programu a abecedu na pásce. Nezapomeňte, že stavový diagram není jediný způsob reprezentace konfigurace Turingova stroje. Můžete využít množinu přechodových funkcí ve tvaru:

(aktuální stav, čtený symbol) = (následující stav, zapisovaný symbol, posun hlavou)

Příklad:

(q_0, 1) = {q_1, 1, R},

(q_0, 0) = {q_1, 0, R},

(q_1, #) = {q_1, #, S} = {F},

...

Využití k-páskového přístupu vám usnadní práci, ale můžete realizovat i jako jednopáskový TS. Využijte znalosti primitivně rekurzivních funkcí.

HINT
(nezapomeňte rozšířit na k-páskovou variantu pokud si chcete usnadnit práci)


State {

   name: String		// identifikátor stavu

   start: boolean       // počáteční stav

   end: boolean         // koncový stav

}



Tape {

symbols: String[] 	// ["1", "0", "0", "1", "0", "0", "0"]

}



Rule {

currentState: State

readSymbol: String

nextState: State

writeSymbol: String	

operation: {R, L, S}

}



Machine {

rules: Rule[]

tape: Tape

head: Number         // pozice čtecí/zapisovací hlavy na pásce

}