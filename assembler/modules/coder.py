A_INSTRUCTION_PREFIX = "0"
C_INSTRUCTION_PREFIX = "111"
A_INSTRUCTION_BITS = 15

DEST_MAP = {
    "null": "000",
    "M": "001",
    "D": "010",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "AD": "110",
    "AMD": "111"
}

COMP_MAP = {
    "0": "0101010",
    "1": "0111111",
    "-1": "0111010",
    "D": "0001100",
    "A": "0110000",
    "M": "1110000",
    "!D": "0001101",
    "!A": "0110001",
    "!M": "1110001",
    "-D": "0001111",
    "-A": "0110011",
    "-M": "1110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "M+1": "1110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "M-1": "1110010",
    "D+A": "0000010",
    "D+M": "1000010",
    "D-A": "0010011",
    "D-M": "1010011",
    "A-D": "0000111",
    "M-D": "1000111",
    "D&A": "0000000",
    "D&M": "1000000",
    "D|A": "0010101",
    "D|M": "1010101"
}

JUMP_MAP = {
    "null": "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


class Translator:
    def __init__(self):
        self.symbols_table = {
            "R0": 0, "R1": 1, "R2": 2, "R3": 3,
            "R4": 4, "R5": 5, "R6": 6, "R7": 7,
            "R8": 8, "R9": 9, "R10": 10, "R11": 11,
            "R12": 12, "R13": 13, "R14": 14, "R15": 15,
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576
        }
        self.num_vars = 16

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
