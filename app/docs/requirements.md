# Assignment Requirements Checklist

This document serves as a verification checklist to ensure the project meets all assignment requirements.

## Core Requirements

### 1. Machine Definition
- [ ] **Finite set of states** - Machine must define all states used in computation
- [ ] **Final/Accept states** - Clearly defined terminal states
- [ ] **Initial state** - Defined starting state for computation
- [ ] **Finite alphabet** - Including blank symbol `#`
- [ ] **Transition functions** - Complete set of rules defining state transitions

### 2. Machine Output
- [ ] **Tape state per step** - Output shows tape configuration at each computation step
- [ ] **Encoded machine representation** - Provide encoded form of the Turing machine (see encoding specification)

### 3. Initial Configuration
- [ ] **Read/Write head position** - Must start on first non-blank symbol of input tape
- [ ] **Final head position** - Not required to be specific after computation ends

## Function Implementation Requirements

### Input Specification
- [ ] **Binary encoded numbers** - Input numbers must be in binary format
- [ ] **Separator symbol** - Numbers separated by blank symbol `ε` (implemented as `#`)
- [ ] **Input format**: `x₁ # x₂ # ... # xₙ #`

### Function Definition
```
fun(x₁, x₂, ..., xₙ) = ∏(i=1 to n) xᵢ
```
- [ ] **Multiplication function** - Compute product of all input numbers
- [ ] **N-ary multiplication** - Support arbitrary number of operands (n ≥ 1)

### Example Verification
**Initial tape state:**
```
                  ↓
T1: # # # # # 1 0 1 # 1 0 # 1 1 0 # # # #
```

**Final tape state:**
```
                    ↓
T1: # # # # # # 1 1 1 1 0 0 # # # # # # #
```

- [ ] **Example test case** - 101₂ × 10₂ × 110₂ = 5 × 2 × 6 = 60₁₀ = 111100₂

## Representation Requirements

### Transition Function Format
```
(current_state, read_symbol) = (next_state, write_symbol, head_movement)
```

- [ ] **Tuple notation** - Use `(qᵢ, symbol) → (qⱼ, symbol, direction)`
- [ ] **Extended for k-tapes** - For multi-tape: `(qᵢ, (s₁, s₂, ..., sₖ)) → (qⱼ, (w₁, w₂, ..., wₖ), (m₁, m₂, ..., mₖ))`

### State Structure
```
State {
    name: String      // state identifier
    start: boolean    // is initial state
    end: boolean      // is accept/final state
}
```
- [ ] **State naming** - Clear, descriptive state names
- [ ] **Start/end markers** - Properly marked initial and final states

### Tape Structure
```
Tape {
    symbols: String[]  // tape contents as array
}
```
- [ ] **Tape representation** - Array or appropriate data structure
- [ ] **Infinite tape simulation** - Ability to extend in both directions

### Rule Structure
```
Rule {
    currentState: State
    readSymbol: String
    nextState: State
    writeSymbol: String
    operation: {R, L, S}  // Right, Left, Stay
}
```
- [ ] **Complete transition rules** - All necessary transitions defined
- [ ] **Valid operations** - Only R (right), L (left), S (stay) movements

### Machine Structure
```
Machine {
    rules: Rule[]
    tape: Tape (or Tape[])
    head: Number  // head position on tape
}
```
- [ ] **Rule collection** - All transition rules stored
- [ ] **Tape management** - Single or multiple tapes
- [ ] **Head tracking** - Current position of read/write head(s)

## K-Tape Implementation (Optional but Recommended)

- [ ] **Multi-tape support** - Implement k-tape variant (k=3 recommended)
- [ ] **Tape designation** - Clearly mark input and output tapes
- [ ] **Auxiliary tapes** - Use helper tapes for intermediate computation

## Encoding Specification

- [ ] **Machine encoding** - Provide binary encoding of the complete machine
- [ ] **Encoding format** - Follow standard Turing machine encoding conventions
- [ ] **Output encoding** - Include encoded machine in final output

## Documentation Requirements

- [ ] **Code comments** - Technical, specific comments in English
- [ ] **Variable names** - All identifiers in English
- [ ] **MD files** - All documentation in English
- [ ] **Algorithm explanation** - Clear description of multiplication algorithm
- [ ] **Usage instructions** - How to run and test the machine

## Testing Requirements

- [ ] **Single number** - Test with n=1 (identity function)
- [ ] **Two numbers** - Test basic multiplication (n=2)
- [ ] **Multiple numbers** - Test n-ary multiplication (n≥3)
- [ ] **Edge cases** - Test with 0, 1, powers of 2
- [ ] **Binary output verification** - Confirm results are correct in binary

## Implementation Hints

- [ ] **Primitive recursive functions** - Utilize knowledge of primitive recursive functions
- [ ] **k-tape advantage** - Leverage multiple tapes to simplify logic
- [ ] **State diagram alternative** - Transition functions sufficient (state diagram not required)
