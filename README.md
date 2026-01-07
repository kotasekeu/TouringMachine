# Multi-Tape Turing Machine - Binary N-ary Multiplication

A 3-tape deterministic Turing Machine implementation that performs n-ary binary multiplication using the shift-and-add algorithm.

## Overview

This project implements a theoretical computer science model: a multi-tape Turing Machine capable of multiplying an arbitrary number of binary integers. The implementation demonstrates fundamental concepts in computability theory and serves as an educational tool for understanding Turing Machines.

### Key Features

- **3-Tape Architecture**: Uses three independent tapes for input, working memory, and accumulation
- **N-ary Multiplication**: Handles any number of binary factors (2, 3, 4, or more)
- **Shift-and-Add Algorithm**: Classic binary multiplication technique
- **Complete Execution Logging**: Records every step with tape states and transitions
- **Machine Encoding**: Exports machine definition in both JSON and theoretical binary formats
- **Comprehensive Testing**: Unit tests for logic blocks and integration tests for full operations

## Algorithm

The machine implements binary multiplication via the shift-and-add method:

```
For each factor x with bits b₀, b₁, ..., bₙ (LSB to MSB):
    result = 0
    temp = previous_product
    for each bit bᵢ:
        if bᵢ = 1:
            result += temp
        temp *= 2  (left shift)
    previous_product = result
```

**Example**: `5 × 2 × 3 = 30`

```
Input:  "101#10#11#"  (binary: 5 × 2 × 3)

Phase 1: Copy 101 → T2
Phase 2: Multiply by 10 (2):
  - Bit 0 (LSB=0): Skip add, shift T2: 101 → 1010
  - Bit 1 (MSB=1): Add 1010 to T3, shift
  - Result: T2 = 1010 (10 in decimal)

Phase 3: Multiply by 11 (3):
  - Bit 0 (LSB=1): Add 1010 to T3 = 1010, shift T2 → 10100
  - Bit 1 (MSB=1): Add 10100 to T3 = 11110, shift
  - Result: T2 = 11110 (30 in decimal)

Output: "11110" (30 in binary) ✓
```

## Project Structure

```
TouringMachine/
├── app/
│   ├── turing_machine.py       # Core TM infrastructure (Tape, Machine, Logger)
│   ├── tm_logic_utils.py       # Composable logic blocks (add, shift, transfer)
│   ├── run.py                  # Main entry point and state machine assembly
│   ├── docs/                   # API documentation
│   │   ├── turing_machine_API.md
│   │   ├── tm_logic_utils_API.md
│   │   ├── run_API.md
│   │   └── requirements_verification.md
│   ├── tests/                  # Test suite
│   │   ├── test_simple_1x1.py     # Integration: 1×1
│   │   ├── test_2x3.py            # Integration: 2×3
│   │   ├── test_5x2x3.py          # Integration: 5×2×3
│   │   ├── test_01_copy_logic.py  # Unit: Copy phase
│   │   ├── test_02_navigation.py  # Unit: Navigation
│   │   ├── test_03_addition.py    # Unit: Binary addition
│   │   ├── test_04_shift_logic.py # Unit: Left shift
│   │   └── test_05_transfer.py    # Unit: Transfer T3→T2
│   └── example/                # Sample execution logs
│       ├── README.md
│       ├── final_simulation.txt
│       └── machine_definition.txt
└── README.md                   # This file
```

## Quick Start

### Prerequisites

- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### Running a Multiplication

1. **Edit the input** in `app/run.py`:
   ```python
   input_str = "101#10#11#"  # Change to your binary numbers
   ```

2. **Run the simulation**:
   ```bash
   cd app
   python3 run.py
   ```

3. **View results**:
   - Console: Final result displayed
   - `final_simulation.txt`: Complete execution trace with tape states
   - `machine_definition.txt`: Machine encoding (JSON format)

### Example Session

```bash
$ cd app
$ python3 run.py
Simulation finished. Result: 11110

$ cat final_simulation.txt
N-ary multiplication of: 101#10#11#

Step 0 (q_start)
T1 [pos:  0]: ##101#10#11#
                ^
T2 [pos:  0]: ############
                ^
T3 [pos:  0]: ############
                ^
...
Step 118 (q_final)
Result: 11110 (decimal: 30)
✓ Multiplication complete: 5 × 2 × 3 = 30
```

## Running Tests

### Integration Tests (Recommended)

Test complete multiplication operations:

```bash
cd app
python3 tests/test_simple_1x1.py   # 1×1 = 1 (28 steps)
python3 tests/test_2x3.py          # 2×3 = 6 (54 steps)
python3 tests/test_5x2x3.py        # 5×2×3 = 30 (118 steps)
```

### Unit Tests

Test individual logic blocks:

```bash
cd app
python3 tests/test_01_copy_logic.py      # Copy first factor
python3 tests/test_02_navigation.py      # Find next factor
python3 tests/test_03_addition.py        # Binary addition T3 += T2
python3 tests/test_04_shift_logic.py     # Left shift T2 *= 2
python3 tests/test_05_transfer.py        # Transfer T3 → T2
```

### Run All Tests

```bash
cd app
for f in tests/test_*.py; do
    echo "=== Running $f ==="
    python3 "$f"
    echo ""
done
```

## Input Format

Binary numbers separated by `#` symbols:

```
x₁ # x₂ # x₃ # ... # xₙ #
```

**Examples**:
- `1#1#` → 1 × 1 = 1
- `10#11#` → 2 × 3 = 6
- `101#10#11#` → 5 × 2 × 3 = 30
- `111#10#11#101#` → 7 × 2 × 3 × 5 = 210

**Constraints**:
- Numbers must be in binary (only `0` and `1`)
- At least 2 factors required
- Each factor must be at least 1 bit
- Maximum factor length: Limited by computational resources
- Maximum number of factors: Unlimited (theoretically)

## Tape Usage

| Tape | Purpose | Access | Notes |
|------|---------|--------|-------|
| T1 | Input factors | Read-only | Original input preserved |
| T2 | Working/Product | Read-write | Current product, modified during multiplication |
| T3 | Accumulator | Read-write | Temporary sum during single factor processing |

## Implementation Details

### State Machine Phases

The complete state machine is composed of 7 phases:

1. **COPY**: Copy first factor from T1 to T2
2. **NAVIGATION**: Find next factor on T1
3. **POSITIONING**: Move to LSB of current factor
4. **MULTIPLICATION CORE**: For each bit, decide add/shift based on bit value
5. **CONTROL FLOW**: Navigate to next bit or complete factor
6. **TRANSFER**: Move accumulated result from T3 to T2
7. **FINAL TRANSFER**: Check for more factors or terminate

## Performance Characteristics

### Time Complexity

For n factors with maximum length m:
- **Overall**: O(n × m²)
- Per factor: O(m²) due to repeated additions and shifts

### Space Complexity

- **Tape storage**: O(m × 2ⁿ) - product grows exponentially
- **State machine**: O(1) - fixed number of states (~20)

### Benchmark Results

| Operation | Factors | Steps | Time |
|-----------|---------|-------|------|
| 1 × 1 | 2 | 28 | < 1ms |
| 2 × 3 | 2 | 54 | < 1ms |
| 5 × 2 × 3 | 3 | 118 | < 1ms |
| 7 × 6 × 5 | 3 | ~200 | < 1ms |

## Documentation

Comprehensive API documentation is available in `app/docs/`:

- **[turing_machine_API.md](app/docs/turing_machine_API.md)**: Core infrastructure (Tape, MultiTapeTuringMachine, TuringEncoder, SimulationLogger)
- **[tm_logic_utils_API.md](app/docs/tm_logic_utils_API.md)**: Algorithm details, logic blocks, bug fixes
- **[run_API.md](app/docs/run_API.md)**: State machine composition, configuration, usage examples
- **[requirements_verification.md](app/docs/requirements_verification.md)**: Assignment requirements verification

## Examples

See `app/example/` for sample output files:

- **Input**: `101#10#110#` (5 × 2 × 6 = 60)
- **Output**: Complete execution trace with all tape states
- **Machine Definition**: JSON encoding of the complete state machine

## Educational Use

This implementation is designed for educational purposes in computer science theory courses:

- **Computability Theory**: Demonstrates Church-Turing thesis
- **Algorithm Design**: Shows shift-and-add multiplication decomposition
- **State Machine Design**: Illustrates composable logic blocks
- **Testing Methodology**: Unit vs integration testing for complex systems

## Theoretical Background

### Turing Machine Model

A Turing Machine is defined by the tuple:

```
M = (Q, Σ, δ, q₀, F)

Q  = finite set of states
Σ  = finite alphabet (including blank symbol)
δ  = transition function: Q × Σᵏ → Q × Σᵏ × {L,R,S}ᵏ
q₀ = start state
F  = set of accept states
k  = number of tapes (3 in this implementation)
```

### Computational Model

At each step:
1. Read one symbol from each tape
2. Look up transition: (current_state, symbols) → (next_state, writes, moves)
3. Write new symbols to tapes
4. Move each head (Left/Right/Stay)
5. Update state
6. Halt if no transition exists or accept state reached

### Encoding

The machine can be encoded in binary using unary representation:
- States: q_i → 0^(i+1)
- Symbols: a_j → 0^(j+1)
- Moves: L='0', R='00', S='000'

See `TuringEncoder` class for implementation.

## Troubleshooting

### Common Issues

**Issue**: "ModuleNotFoundError: No module named 'turing_machine'"
**Solution**: Ensure you're running from the `app/` directory or use `PYTHONPATH`:
```bash
PYTHONPATH=/path/to/app python3 tests/test_*.py
```

**Issue**: Simulation exceeds max_steps
**Solution**: Increase `max_steps` in `run.py` or check input format

**Issue**: Incorrect result
**Solution**: Check input format (must end with `#`), verify binary digits only

### Debugging

Enable detailed logging by examining `final_simulation.txt`:
- Check tape states at each step
- Verify state transitions
- Look for unexpected halts

For unit test failures, run individual logic block tests to isolate the issue.

## References

- Sipser, M. (2012). *Introduction to the Theory of Computation* (3rd ed.)
- Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2006). *Introduction to Automata Theory, Languages, and Computation*

## Version History

**v1.0** (2026-01-07)
- Initial implementation with 3-tape multiplication
- Complete test suite (unit + integration)
- Comprehensive documentation
