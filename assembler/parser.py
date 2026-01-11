def parse(instructions):
    """Parses a list of assembly instructions into their components."""
    decomposed_instructions = []
    i = 0

    for instruction in instructions:
        instruction = instruction.replace(" ", "").strip()
        
        # Skip empty lines and comments
        if not instruction or instruction.startswith("//"):
            continue
        
        # Remove inline comments
        instruction = instruction.split("//")[0]

        # Lable
        if instruction[0] == "(":
            symbol = instruction[1:-1]
            decomposed_instructions.append([i, symbol])
            continue

        i += 1
        
    
    for instruction in instructions:
        instruction = instruction.replace(" ", "").strip()

        # Skip empty lines and comments
        if not instruction or instruction.startswith("//"):
            continue

        instruction = instruction.split("//")[0]
        
        if instruction[0] == "(":
            continue


        # A-instruction
        elif instruction[0] == "@":
            value = instruction[1:]
            decomposed_instructions.append(["@", value])

        # C-instruction
        else:
            dest = "null"
            comp = instruction
            jmp = "null"

            if "=" in instruction:
                dest, rest = instruction.split("=")
                comp = rest
            else:
                rest = instruction
            
            if ";" in rest:
                comp, jmp = rest.split(";")

            decomposed_instructions.append([dest, comp, jmp.upper() if jmp != "null" else jmp])

    return decomposed_instructions