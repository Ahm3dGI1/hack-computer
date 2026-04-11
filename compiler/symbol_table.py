"""Symbol table for the Jack compiler."""

# Kind constants
STATIC = "static"
FIELD = "field"
ARG = "argument"
VAR = "local"


class SymbolTable:
    def __init__(self):
        self.class_scope = {}    # {name: (type, kind, index)}
        self.sub_scope = {}
        self._counts = {STATIC: 0, FIELD: 0, ARG: 0, VAR: 0}

    def reset_subroutine(self):
        """Reset subroutine-level scope."""
        self.sub_scope = {}
        self._counts[ARG] = 0
        self._counts[VAR] = 0

    def define(self, name, type_, kind):
        """Define a new variable."""
        index = self._counts[kind]
        self._counts[kind] += 1

        if kind in (STATIC, FIELD):
            self.class_scope[name] = (type_, kind, index)
        else:
            self.sub_scope[name] = (type_, kind, index)

    def var_count(self, kind):
        return self._counts[kind]

    def lookup(self, name):
        """Return (type, kind, index) or None if not found."""
        if name in self.sub_scope:
            return self.sub_scope[name]
        if name in self.class_scope:
            return self.class_scope[name]
        return None

    def type_of(self, name):
        entry = self.lookup(name)
        return entry[0] if entry else None

    def kind_of(self, name):
        entry = self.lookup(name)
        if entry is None:
            return None
        # Map 'field' to 'this' for VM segment
        return "this" if entry[1] == FIELD else entry[1]

    def index_of(self, name):
        entry = self.lookup(name)
        return entry[2] if entry else None
