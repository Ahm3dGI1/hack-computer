import sys
import os

from parser import Parser
from code_writer import CodeWriter


def translate_file(vm_file, writer):
    """Translate a single .vm file, returning assembly lines."""
    file_name = os.path.splitext(os.path.basename(vm_file))[0]
    writer.set_file_name(file_name)

    parser = Parser()
    commands = parser.parse_file(vm_file)
    return [writer.write_assembly(cmd) for cmd in commands]


def main(input_path):
    writer = CodeWriter()

    if os.path.isdir(input_path):
        vm_files = sorted(
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.endswith(".vm")
        )
        if not vm_files:
            print(f"Error: no .vm files found in {input_path}")
            sys.exit(1)

        dir_name = os.path.basename(os.path.normpath(input_path))
        output_file = os.path.join(input_path, f"{dir_name}.asm")

        assembly = [writer.write_bootstrap()]
        for vm_file in vm_files:
            assembly.extend(translate_file(vm_file, writer))

    elif os.path.isfile(input_path) and input_path.endswith(".vm"):
        output_file = os.path.splitext(input_path)[0] + ".asm"
        assembly = translate_file(input_path, writer)

    else:
        print("Error: input must be a .vm file or a directory containing .vm files")
        sys.exit(1)

    with open(output_file, "w") as f:
        f.write("\n".join(assembly) + "\n")

    print(f"Translated -> {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <file.vm | directory>")
        sys.exit(1)

    main(sys.argv[1])
