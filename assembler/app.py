from modules.parser import parse
from modules.coder import Translator

import sys


def main(rom_name):
    """
    Main function to parse assembly instructions and translate them to binary.

    Args:
        assembly_instructions: List of assembly instruction strings.
    """

    translator = Translator()

    with open(f"{rom_name}.asm", 'r') as rom:
        instructions = rom.readlines()
        for instruction in instructions:
            instruction.strip()

    parsed_instructions = parse(instructions)
    binary_instructions = []
    for parsed_instruction in parsed_instructions:
        binary = translator.translate_to_binary(parsed_instruction)

        if binary is not None:
            binary_instructions.append(binary)

    with open(f"{rom_name}.hack", 'w') as output_file:
        output_file.write("\n".join(binary_instructions))

    return binary_instructions


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)

    input_file = sys.argv[1]
    main(input_file)
