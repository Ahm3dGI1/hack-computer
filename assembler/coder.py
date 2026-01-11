from .constants import (
    A_INSTRUCTION_PREFIX, A_INSTRUCTION_BITS, C_INSTRUCTION_PREFIX,
    PREDEFINED_SYMBOLS, VARIABLE_START_ADDRESS,
    DEST_MAP, COMP_MAP, JUMP_MAP,
)


class Translator:
    def __init__(self):
        self.symbols_table = PREDEFINED_SYMBOLS.copy()
        self.num_vars = VARIABLE_START_ADDRESS

    def translate_label(self, line, symbol):
        """Add label to the symbols table."""
        self.symbols_table[symbol] = line

    def translate_a_instruction(self, value_str):
        """Translate A-instruction to 16-bit binary."""
        if value_str in self.symbols_table:
            value = self.symbols_table[value_str]
        elif value_str.isdigit():
            value = int(value_str)

        else:
            self.symbols_table[value_str] = self.num_vars
            value = self.symbols_table[value_str]
            self.num_vars += 1

        binary = bin(value)[2:]
        return A_INSTRUCTION_PREFIX + binary.zfill(A_INSTRUCTION_BITS)

    def translate_c_instruction(self, dest, comp, jump):
        """Translate C-instruction to 16-bit binary."""

        return (C_INSTRUCTION_PREFIX +
                COMP_MAP[comp] +
                DEST_MAP[dest] +
                JUMP_MAP[jump])

    def translate_to_binary(self, instruction_components):
        """
        Translate parsed instruction to 16-bit binary.

        Args:
            instruction_components: Either ["@", value] or [dest, comp, jump]

        Returns:
            16-bit binary string
        """
        if instruction_components[0] == "@":
            return self.translate_a_instruction(instruction_components[1])
        elif type(instruction_components[0]) is int:
            return self.translate_label(instruction_components[0], instruction_components[1])
        else:
            dest, comp, jump = instruction_components
            return self.translate_c_instruction(dest, comp, jump)
