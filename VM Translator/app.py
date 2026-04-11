import sys
import os

from parser import Parser
from code_writer import CodeWriter


def translate(vm_file):
    file_name = os.path.splitext(os.path.basename(vm_file))[0]
    output_file = os.path.splitext(vm_file)[0] + ".asm"

    parser = Parser()
    writer = CodeWriter()
    writer.set_file_name(file_name)

    commands = parser.parse_file(vm_file)
    assembly = [writer.write_assembly(cmd) for cmd in commands]

    with open(output_file, "w") as f:
        f.write("".join(assembly) + "")

    print(f"Translated: {vm_file} -> {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <file.vm>")
        sys.exit(1)

    input_file = sys.argv[1]

    if not input_file.endswith(".vm"):
        print("Error: input file must have a .vm extension")
        sys.exit(1)

    if not os.path.isfile(input_file):
        print(f"Error: file not found: {input_file}")
        sys.exit(1)

    translate(input_file)
