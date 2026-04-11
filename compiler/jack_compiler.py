"""Jack Compiler (Project 11) — compiles .jack files to .vm files."""

import sys
import os

from jack_tokenizer import JackTokenizer
from code_gen_engine import CodeGenEngine


def compile_file(jack_file):
    """Compile a single .jack file to .vm."""
    with open(jack_file) as f:
        source = f.read()

    tokenizer = JackTokenizer(source)
    engine = CodeGenEngine(tokenizer)
    vm_code = engine.compile_class()

    vm_path = jack_file.replace(".jack", ".vm")
    with open(vm_path, "w") as f:
        f.write(vm_code)

    print(f"Compiled: {jack_file} -> {vm_path}")


def main(input_path):
    if os.path.isdir(input_path):
        for fname in sorted(os.listdir(input_path)):
            if fname.endswith(".jack"):
                compile_file(os.path.join(input_path, fname))
    elif input_path.endswith(".jack"):
        compile_file(input_path)
    else:
        print("Error: input must be a .jack file or a directory")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jack_compiler.py <file.jack | directory>")
        sys.exit(1)
    main(sys.argv[1])
