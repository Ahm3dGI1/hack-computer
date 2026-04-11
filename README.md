# hack-computer
**Course:** Build a Modern Computer from First Principles  

This repository contains my implementations for the [Nand2Tetris](https://www.nand2tetris.org/) course, also known as *Build a Modern Computer from First Principles*. The course walks through building a complete computer system — from logic gates all the way to an operating system — entirely from the ground up.

---

## Projects

### Hardware (HDL)

| # | Project | Directory | Description |
|---|---------|-----------|-------------|
| 1 | Boolean Logic | `chips/` | Basic logic gates built from NAND (And, Or, Mux, DMux, etc.) |
| 2 | Boolean Arithmetic | `chips/` | HalfAdder, FullAdder, Add16, Inc16, ALU |
| 3 | Sequential Logic | `chips/` | Bit, Register, RAM8/64/512/4K/16K, PC |
| 4 | Machine Language | `scripts/` | Hack assembly programs (Mult, Fill) |
| 5 | Computer Architecture | `chips/` | CPU, Memory, and the complete Computer chip |

### Software (Python & Jack)

| # | Project | Directory | Description |
|---|---------|-----------|-------------|
| 6 | Assembler | `assembler/` | Two-pass assembler translating Hack assembly (`.asm`) to binary (`.hack`) |
| 7-8 | VM Translator | `VM Translator/` | Translates VM code (`.vm`) to Hack assembly — stack arithmetic, memory access, program flow, and function calls |
| 9 | Jack Program | `jack_program/` | A Snake game written in the Jack language |
| 10 | Syntax Analyzer | `compiler/` | Tokenizer and recursive-descent parser producing XML parse trees from `.jack` files |
| 11 | Compiler | `compiler/` | Full Jack-to-VM compiler with symbol table and code generation |
| 12 | Operating System | `jack_os/` | Jack OS standard library — Math, String, Memory, Screen, Output, Keyboard, Sys, Array |

---

## Usage

**Assembler** — translate `.asm` to `.hack`:
```bash
python assembler/app.py path/to/file.asm
```

**VM Translator** — translate `.vm` file or directory to `.asm`:
```bash
python "VM Translator/app.py" path/to/file.vm
python "VM Translator/app.py" path/to/directory/
```

**Syntax Analyzer** — produce XML parse trees from `.jack` files:
```bash
python compiler/jack_analyzer.py path/to/file.jack
python compiler/jack_analyzer.py path/to/directory/
```

**Compiler** — compile `.jack` files to `.vm`:
```bash
python compiler/jack_compiler.py path/to/file.jack
python compiler/jack_compiler.py path/to/directory/
```

---

## About

These projects were completed as part of my journey to deepen my understanding of computer architecture and low-level systems design.
