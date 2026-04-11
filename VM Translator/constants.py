# Maps RAM pointer names to their addresses (0-based, per Hack spec)
RAM_POINTERS = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
}

# Maps VM segment names to their base address or pointer symbol.
# - Pointer-based segments (local, argument, this, that) map to the RAM symbol
#   whose value holds the base address (indirect addressing).
# - Fixed segments (temp, pointer) map to their literal base addresses.
SEGMENT_BASES = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    "temp": 5,      # R5-R12; base is fixed, not a pointer
    "pointer": 3,   # R3 = THIS, R4 = THAT
}

COMMAND_TYPES = {
    "add": "C_ARITHMETIC",
    "sub": "C_ARITHMETIC",
    "neg": "C_ARITHMETIC",
    "eq": "C_ARITHMETIC",
    "gt": "C_ARITHMETIC",
    "lt": "C_ARITHMETIC",
    "and": "C_ARITHMETIC",
    "or": "C_ARITHMETIC",
    "not": "C_ARITHMETIC",
    "push": "C_PUSH",
    "pop": "C_POP",
    "label": "C_LABEL",
    "goto": "C_GOTO",
    "if-goto": "C_IF",
    "function": "C_FUNCTION",
    "call": "C_CALL",
    "return": "C_RETURN",
}
