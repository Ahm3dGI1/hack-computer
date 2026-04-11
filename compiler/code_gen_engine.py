"""Jack compiler — recursive-descent parser that emits VM code."""

from jack_tokenizer import KEYWORD, SYMBOL, INT_CONST, STRING_CONST, IDENTIFIER
from symbol_table import SymbolTable, STATIC, FIELD, ARG, VAR
from vm_writer import VMWriter

OP_MAP = {
    "+": "add", "-": "sub", "=": "eq", ">": "gt", "<": "lt",
    "&": "and", "|": "or",
}
UNARY_OP = {"-": "neg", "~": "not"}


class CodeGenEngine:
    """Compile Jack tokens into VM code."""

    def __init__(self, tokenizer):
        self.tk = tokenizer
        self.symbols = SymbolTable()
        self.vm = VMWriter()
        self.class_name = ""
        self.label_counter = 0

    def _unique_label(self, prefix):
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def _eat(self, ttype, value=None):
        return self.tk.expect(ttype, value)

    def _eat_type(self):
        tok = self.tk.peek()
        if tok[0] == KEYWORD and tok[1] in ("int", "char", "boolean"):
            return self.tk.advance()
        return self._eat(IDENTIFIER)

    # ------------------------------------------------------------------
    # Program structure
    # ------------------------------------------------------------------

    def compile_class(self):
        self._eat(KEYWORD, "class")
        self.class_name = self._eat(IDENTIFIER)[1]
        self._eat(SYMBOL, "{")

        while self.tk.peek() and self.tk.peek()[1] in ("static", "field"):
            self._compile_class_var_dec()

        while self.tk.peek() and self.tk.peek()[1] in ("constructor", "function", "method"):
            self._compile_subroutine()

        self._eat(SYMBOL, "}")
        return self.vm.get_vm_code()

    def _compile_class_var_dec(self):
        kind = self._eat(KEYWORD)[1]  # static | field
        type_ = self._eat_type()[1]
        name = self._eat(IDENTIFIER)[1]
        self.symbols.define(name, type_, kind)

        while self.tk.peek() and self.tk.peek()[1] == ",":
            self._eat(SYMBOL, ",")
            name = self._eat(IDENTIFIER)[1]
            self.symbols.define(name, type_, kind)

        self._eat(SYMBOL, ";")

    def _compile_subroutine(self):
        sub_kind = self._eat(KEYWORD)[1]  # constructor | function | method
        # return type
        if self.tk.peek()[1] == "void":
            self._eat(KEYWORD, "void")
        else:
            self._eat_type()

        sub_name = self._eat(IDENTIFIER)[1]
        func_name = f"{self.class_name}.{sub_name}"

        self.symbols.reset_subroutine()

        # Methods have 'this' as implicit argument 0
        if sub_kind == "method":
            self.symbols.define("this", self.class_name, ARG)

        self._eat(SYMBOL, "(")
        self._compile_parameter_list()
        self._eat(SYMBOL, ")")

        # Subroutine body
        self._eat(SYMBOL, "{")
        while self.tk.peek() and self.tk.peek()[1] == "var":
            self._compile_var_dec()

        n_locals = self.symbols.var_count(VAR)
        self.vm.write_function(func_name, n_locals)

        if sub_kind == "constructor":
            n_fields = self.symbols.var_count(FIELD)
            self.vm.write_push("constant", n_fields)
            self.vm.write_call("Memory.alloc", 1)
            self.vm.write_pop("pointer", 0)
        elif sub_kind == "method":
            self.vm.write_push("argument", 0)
            self.vm.write_pop("pointer", 0)

        self._compile_statements()
        self._eat(SYMBOL, "}")

    def _compile_parameter_list(self):
        if self.tk.peek() and self.tk.peek()[1] != ")":
            type_ = self._eat_type()[1]
            name = self._eat(IDENTIFIER)[1]
            self.symbols.define(name, type_, ARG)

            while self.tk.peek() and self.tk.peek()[1] == ",":
                self._eat(SYMBOL, ",")
                type_ = self._eat_type()[1]
                name = self._eat(IDENTIFIER)[1]
                self.symbols.define(name, type_, ARG)

    def _compile_var_dec(self):
        self._eat(KEYWORD, "var")
        type_ = self._eat_type()[1]
        name = self._eat(IDENTIFIER)[1]
        self.symbols.define(name, type_, VAR)

        while self.tk.peek() and self.tk.peek()[1] == ",":
            self._eat(SYMBOL, ",")
            name = self._eat(IDENTIFIER)[1]
            self.symbols.define(name, type_, VAR)

        self._eat(SYMBOL, ";")

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _compile_statements(self):
        while self.tk.peek() and self.tk.peek()[1] in ("let", "if", "while", "do", "return"):
            kw = self.tk.peek()[1]
            if kw == "let":
                self._compile_let()
            elif kw == "if":
                self._compile_if()
            elif kw == "while":
                self._compile_while()
            elif kw == "do":
                self._compile_do()
            elif kw == "return":
                self._compile_return()

    def _compile_let(self):
        self._eat(KEYWORD, "let")
        var_name = self._eat(IDENTIFIER)[1]
        is_array = False

        if self.tk.peek() and self.tk.peek()[1] == "[":
            is_array = True
            self._eat(SYMBOL, "[")
            self._compile_expression()
            self._eat(SYMBOL, "]")
            # Push base address + index
            self.vm.write_push(self.symbols.kind_of(var_name),
                               self.symbols.index_of(var_name))
            self.vm.write_arithmetic("add")

        self._eat(SYMBOL, "=")
        self._compile_expression()
        self._eat(SYMBOL, ";")

        if is_array:
            self.vm.write_pop("temp", 0)
            self.vm.write_pop("pointer", 1)
            self.vm.write_push("temp", 0)
            self.vm.write_pop("that", 0)
        else:
            self.vm.write_pop(self.symbols.kind_of(var_name),
                              self.symbols.index_of(var_name))

    def _compile_if(self):
        self._eat(KEYWORD, "if")
        self._eat(SYMBOL, "(")
        self._compile_expression()
        self._eat(SYMBOL, ")")

        false_label = self._unique_label("IF_FALSE")
        end_label = self._unique_label("IF_END")

        self.vm.write_arithmetic("not")
        self.vm.write_if(false_label)

        self._eat(SYMBOL, "{")
        self._compile_statements()
        self._eat(SYMBOL, "}")

        if self.tk.peek() and self.tk.peek()[1] == "else":
            self.vm.write_goto(end_label)
            self.vm.write_label(false_label)
            self._eat(KEYWORD, "else")
            self._eat(SYMBOL, "{")
            self._compile_statements()
            self._eat(SYMBOL, "}")
            self.vm.write_label(end_label)
        else:
            self.vm.write_label(false_label)

    def _compile_while(self):
        loop_label = self._unique_label("WHILE_EXP")
        end_label = self._unique_label("WHILE_END")

        self.vm.write_label(loop_label)

        self._eat(KEYWORD, "while")
        self._eat(SYMBOL, "(")
        self._compile_expression()
        self._eat(SYMBOL, ")")

        self.vm.write_arithmetic("not")
        self.vm.write_if(end_label)

        self._eat(SYMBOL, "{")
        self._compile_statements()
        self._eat(SYMBOL, "}")

        self.vm.write_goto(loop_label)
        self.vm.write_label(end_label)

    def _compile_do(self):
        self._eat(KEYWORD, "do")
        self._compile_subroutine_call()
        self._eat(SYMBOL, ";")
        # Discard void return value
        self.vm.write_pop("temp", 0)

    def _compile_return(self):
        self._eat(KEYWORD, "return")
        if self.tk.peek() and self.tk.peek()[1] != ";":
            self._compile_expression()
        else:
            self.vm.write_push("constant", 0)
        self._eat(SYMBOL, ";")
        self.vm.write_return()

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def _compile_subroutine_call(self):
        """Compile: name(args) or name.name(args)"""
        first_name = self._eat(IDENTIFIER)[1]
        n_args = 0

        if self.tk.peek() and self.tk.peek()[1] == ".":
            self._eat(SYMBOL, ".")
            sub_name = self._eat(IDENTIFIER)[1]

            # Check if first_name is an object variable
            entry = self.symbols.lookup(first_name)
            if entry:
                # Method call on object: push object as arg 0
                self.vm.write_push(self.symbols.kind_of(first_name),
                                   self.symbols.index_of(first_name))
                func_name = f"{entry[0]}.{sub_name}"
                n_args = 1
            else:
                # Static function call: ClassName.function
                func_name = f"{first_name}.{sub_name}"
        else:
            # Unqualified call — method on current object
            func_name = f"{self.class_name}.{first_name}"
            self.vm.write_push("pointer", 0)
            n_args = 1

        self._eat(SYMBOL, "(")
        n_args += self._compile_expression_list()
        self._eat(SYMBOL, ")")

        self.vm.write_call(func_name, n_args)

    def _compile_expression(self):
        self._compile_term()

        while self.tk.peek() and self.tk.peek()[1] in OP_MAP or (
            self.tk.peek() and self.tk.peek()[1] == "*"
        ) or (self.tk.peek() and self.tk.peek()[1] == "/"):
            op = self._eat(SYMBOL)[1]
            self._compile_term()
            if op == "*":
                self.vm.write_call("Math.multiply", 2)
            elif op == "/":
                self.vm.write_call("Math.divide", 2)
            else:
                self.vm.write_arithmetic(OP_MAP[op])

    def _compile_term(self):
        tok = self.tk.peek()

        if tok[0] == INT_CONST:
            val = self._eat(INT_CONST)[1]
            self.vm.write_push("constant", val)

        elif tok[0] == STRING_CONST:
            s = self._eat(STRING_CONST)[1]
            self.vm.write_push("constant", len(s))
            self.vm.write_call("String.new", 1)
            for ch in s:
                self.vm.write_push("constant", ord(ch))
                self.vm.write_call("String.appendChar", 2)

        elif tok[0] == KEYWORD and tok[1] in ("true", "false", "null", "this"):
            kw = self._eat(KEYWORD)[1]
            if kw == "true":
                self.vm.write_push("constant", 0)
                self.vm.write_arithmetic("not")
            elif kw in ("false", "null"):
                self.vm.write_push("constant", 0)
            elif kw == "this":
                self.vm.write_push("pointer", 0)

        elif tok[1] == "(":
            self._eat(SYMBOL, "(")
            self._compile_expression()
            self._eat(SYMBOL, ")")

        elif tok[1] in UNARY_OP:
            op = self._eat(SYMBOL)[1]
            self._compile_term()
            self.vm.write_arithmetic(UNARY_OP[op])

        elif tok[0] == IDENTIFIER:
            # Look ahead to distinguish var, array, subroutine call
            self.tk.advance()
            next_tok = self.tk.peek()

            if next_tok and next_tok[1] == "[":
                # array access: varName[expression]
                var_name = tok[1]
                self._eat(SYMBOL, "[")
                self._compile_expression()
                self._eat(SYMBOL, "]")
                self.vm.write_push(self.symbols.kind_of(var_name),
                                   self.symbols.index_of(var_name))
                self.vm.write_arithmetic("add")
                self.vm.write_pop("pointer", 1)
                self.vm.write_push("that", 0)

            elif next_tok and next_tok[1] in ("(", "."):
                # Subroutine call — put token back and use subroutine_call
                self.tk.pos -= 1
                self._compile_subroutine_call()

            else:
                # Simple variable
                var_name = tok[1]
                self.vm.write_push(self.symbols.kind_of(var_name),
                                   self.symbols.index_of(var_name))

    def _compile_expression_list(self):
        """Compile comma-separated expressions. Returns the count."""
        count = 0
        if self.tk.peek() and self.tk.peek()[1] != ")":
            self._compile_expression()
            count = 1
            while self.tk.peek() and self.tk.peek()[1] == ",":
                self._eat(SYMBOL, ",")
                self._compile_expression()
                count += 1
        return count
