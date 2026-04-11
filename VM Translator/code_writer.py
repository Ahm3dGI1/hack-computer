from constants import SEGMENT_BASES


class CodeWriter:
    def __init__(self):
        self.label_counter = 0
        self.current_file = ""
        self.current_function = ""

    def set_file_name(self, file_name):
        """Set the base file name, used to generate unique static segment labels."""
        self.current_file = file_name

    def write_bootstrap(self):
        """Emit bootstrap code: SP=256, call Sys.init."""
        return "\n".join([
            self._asm("@256", "D=A", "@SP", "M=D"),
            self._write_call("Sys.init", 0),
        ])

    # -------------------------------------------------------------------------
    # Public dispatch
    # -------------------------------------------------------------------------

    def write_assembly(self, command):
        """Translate a single parsed VM command into Hack assembly."""
        command_type = command[0]

        dispatch = {
            "C_PUSH": lambda: self._write_push(command[2], int(command[3])),
            "C_POP": lambda: self._write_pop(command[2], int(command[3])),
            "C_ARITHMETIC": lambda: self._write_arithmetic(command[1]),
            "C_LABEL": lambda: self._write_label(command[2]),
            "C_GOTO": lambda: self._write_goto(command[2]),
            "C_IF": lambda: self._write_if(command[2]),
            "C_FUNCTION": lambda: self._write_function(command[2], int(command[3])),
            "C_CALL": lambda: self._write_call(command[2], int(command[3])),
            "C_RETURN": lambda: self._write_return(),
        }

        handler = dispatch.get(command_type)
        if handler is None:
            raise ValueError(f"Unknown command type: {command_type}")
        return handler()

    # -------------------------------------------------------------------------
    # Push / Pop
    # -------------------------------------------------------------------------

    def _write_push(self, segment, index):
        if segment == "constant":
            return self._asm(
                f"@{index}",
                "D=A",
                "@SP", "A=M", "M=D",
                "@SP", "M=M+1",
            )

        if segment in ("local", "argument", "this", "that"):
            base = SEGMENT_BASES[segment]
            return self._asm(
                f"@{index}", "D=A",
                f"@{base}", "A=M+D", "D=M",
                "@SP", "A=M", "M=D",
                "@SP", "M=M+1",
            )

        if segment == "temp":
            addr = SEGMENT_BASES["temp"] + index
            return self._asm(
                f"@{addr}", "D=M",
                "@SP", "A=M", "M=D",
                "@SP", "M=M+1",
            )

        if segment == "pointer":
            addr = SEGMENT_BASES["pointer"] + index
            return self._asm(
                f"@{addr}", "D=M",
                "@SP", "A=M", "M=D",
                "@SP", "M=M+1",
            )

        if segment == "static":
            label = f"{self.current_file}.{index}"
            return self._asm(
                f"@{label}", "D=M",
                "@SP", "A=M", "M=D",
                "@SP", "M=M+1",
            )

        raise ValueError(f"Unknown segment: {segment}")

    def _write_pop(self, segment, index):
        if segment in ("local", "argument", "this", "that"):
            base = SEGMENT_BASES[segment]
            # Compute target address, stash in R13, then pop stack into it
            return self._asm(
                f"@{index}", "D=A",
                f"@{base}", "D=M+D",
                "@R13", "M=D",
                "@SP", "M=M-1", "A=M", "D=M",
                "@R13", "A=M", "M=D",
            )

        if segment == "temp":
            addr = SEGMENT_BASES["temp"] + index
            return self._asm(
                "@SP", "M=M-1", "A=M", "D=M",
                f"@{addr}", "M=D",
            )

        if segment == "pointer":
            addr = SEGMENT_BASES["pointer"] + index
            return self._asm(
                "@SP", "M=M-1", "A=M", "D=M",
                f"@{addr}", "M=D",
            )

        if segment == "static":
            label = f"{self.current_file}.{index}"
            return self._asm(
                "@SP", "M=M-1", "A=M", "D=M",
                f"@{label}", "M=D",
            )

        raise ValueError(f"Unknown segment: {segment}")

    # -------------------------------------------------------------------------
    # Arithmetic / Logic
    # -------------------------------------------------------------------------

    def _write_arithmetic(self, op):
        binary_ops = {
            "add": "M=D+M",
            "sub": "M=M-D",
            "and": "M=D&M",
            "or":  "M=D|M",
        }
        unary_ops = {
            "neg": "M=-M",
            "not": "M=!M",
        }
        comparison_jumps = {
            "eq": "JEQ",
            "gt": "JGT",
            "lt": "JLT",
        }

        if op in binary_ops:
            return self._binary_op(binary_ops[op])
        if op in unary_ops:
            return self._unary_op(unary_ops[op])
        if op in comparison_jumps:
            return self._comparison_op(comparison_jumps[op])

        raise ValueError(f"Unknown arithmetic op: {op}")

    def _binary_op(self, instruction):
        """Pop two values, apply instruction, push result."""
        return self._asm(
            "@SP", "M=M-1", "A=M", "D=M",
            "@SP", "M=M-1", "A=M",
            instruction,
            "@SP", "M=M+1",
        )

    def _unary_op(self, instruction):
        """Apply instruction to top of stack in place."""
        return self._asm(
            "@SP", "M=M-1", "A=M",
            instruction,
            "@SP", "M=M+1",
        )

    def _comparison_op(self, jump):
        """Pop two values, push -1 (true) or 0 (false) based on jump condition."""
        true_label = f"TRUE_{self.label_counter}"
        end_label = f"END_{self.label_counter}"
        self.label_counter += 1

        return self._asm(
            "@SP", "M=M-1", "A=M", "D=M",
            "@SP", "M=M-1", "A=M", "D=M-D",
            f"@{true_label}", f"D;{jump}",
            "@SP", "A=M", "M=0",
            f"@{end_label}", "0;JMP",
            f"({true_label})",
            "@SP", "A=M", "M=-1",
            f"({end_label})",
            "@SP", "M=M+1",
        )

    # -------------------------------------------------------------------------
    # Program flow
    # -------------------------------------------------------------------------

    def _scoped_label(self, label):
        """Return function-scoped label: functionName$label."""
        if self.current_function:
            return f"{self.current_function}${label}"
        return label

    def _write_label(self, label):
        return f"({self._scoped_label(label)})"

    def _write_goto(self, label):
        scoped = self._scoped_label(label)
        return self._asm(f"@{scoped}", "0;JMP")

    def _write_if(self, label):
        """Pop top of stack; jump to label if value != 0."""
        scoped = self._scoped_label(label)
        return self._asm(
            "@SP", "M=M-1", "A=M", "D=M",
            f"@{scoped}", "D;JNE",
        )

    # -------------------------------------------------------------------------
    # Functions
    # -------------------------------------------------------------------------

    def _write_function(self, function_name, n_locals):
        """Emit function entry label and initialize all local variables to 0."""
        self.current_function = function_name
        local_init = self._asm("@SP", "A=M", "M=0", "@SP", "M=M+1")
        return "\n".join(
            [f"({function_name})"] + [local_init] * n_locals
        )

    def _write_call(self, function_name, n_args):
        """Save caller state, reposition ARG/LCL, then jump to function."""
        return_label = f"{function_name}$ret.{self.label_counter}"
        self.label_counter += 1

        def push_symbol(sym):
            return self._asm(f"@{sym}", "D=M", "@SP", "A=M", "M=D", "@SP", "M=M+1")

        return "\n".join([
            # push return address
            self._asm(f"@{return_label}", "D=A", "@SP",
                      "A=M", "M=D", "@SP", "M=M+1"),
            push_symbol("LCL"),
            push_symbol("ARG"),
            push_symbol("THIS"),
            push_symbol("THAT"),
            # ARG = SP - 5 - n_args
            self._asm(f"@SP", "D=M", f"@{5 + n_args}", "D=D-A", "@ARG", "M=D"),
            # LCL = SP
            self._asm("@SP", "D=M", "@LCL", "M=D"),
            # goto function
            self._asm(f"@{function_name}", "0;JMP"),
            # inject return address label
            f"({return_label})",
        ])

    def _write_return(self):
        """Restore caller state and transfer control back."""
        return self._asm(
            # FRAME = LCL  (stash in R14)
            "@LCL", "D=M", "@R14", "M=D",
            # RET = *(FRAME - 5)  (stash in R15)
            "@5", "A=D-A", "D=M", "@R15", "M=D",
            # *ARG = pop()
            "@SP", "M=M-1", "A=M", "D=M", "@ARG", "A=M", "M=D",
            # SP = ARG + 1
            "@ARG", "D=M+1", "@SP", "M=D",
            # THAT = *(FRAME - 1)
            "@R14", "A=M-1", "D=M", "@THAT", "M=D",
            # THIS = *(FRAME - 2)
            "@R14", "D=M", "@2", "A=D-A", "D=M", "@THIS", "M=D",
            # ARG  = *(FRAME - 3)
            "@R14", "D=M", "@3", "A=D-A", "D=M", "@ARG", "M=D",
            # LCL  = *(FRAME - 4)
            "@R14", "D=M", "@4", "A=D-A", "D=M", "@LCL", "M=D",
            # goto RET
            "@R15", "A=M", "0;JMP",
        )

    # -------------------------------------------------------------------------
    # Helper
    # -------------------------------------------------------------------------

    @staticmethod
    def _asm(*instructions):
        """Join assembly instructions with newlines."""
        return "\n".join(instructions)
