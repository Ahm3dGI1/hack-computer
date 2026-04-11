"""VM code writer for the Jack compiler."""


class VMWriter:
    def __init__(self):
        self.output = []

    def write_push(self, segment, index):
        self.output.append(f"push {segment} {index}")

    def write_pop(self, segment, index):
        self.output.append(f"pop {segment} {index}")

    def write_arithmetic(self, command):
        self.output.append(command)

    def write_label(self, label):
        self.output.append(f"label {label}")

    def write_goto(self, label):
        self.output.append(f"goto {label}")

    def write_if(self, label):
        self.output.append(f"if-goto {label}")

    def write_call(self, name, n_args):
        self.output.append(f"call {name} {n_args}")

    def write_function(self, name, n_locals):
        self.output.append(f"function {name} {n_locals}")

    def write_return(self):
        self.output.append("return")

    def get_vm_code(self):
        return "\n".join(self.output) + "\n"

    def reset(self):
        self.output = []
