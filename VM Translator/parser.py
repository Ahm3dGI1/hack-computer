from constants import COMMAND_TYPES


class Parser:
    def __init__(self):
        self.vm_commands = []

    def _get_lines(self, vm_file):
        with open(vm_file) as f:
            return f.readlines()

    def _is_valid_line(self, line_parts):
        """Return True if the line contains an executable VM command."""
        return bool(line_parts) and not line_parts[0].startswith("//")

    def parse_file(self, vm_file):
        """Parse a .vm file and return a list of [command_type, op, ...args] lists."""
        for line in self._get_lines(vm_file):
            line_parts = line.strip().split()

            if not self._is_valid_line(line_parts):
                continue

            command_type = COMMAND_TYPES.get(line_parts[0])
            if command_type is None:
                continue

            # Store as flat list: [command_type, op, arg1?, arg2?]
            self.vm_commands.append([command_type] + line_parts)

        return self.vm_commands
