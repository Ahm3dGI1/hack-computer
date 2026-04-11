"""Recursive-descent parser for Jack — produces XML parse tree or VM code."""

from jack_tokenizer import (
    KEYWORD, SYMBOL, INT_CONST, STRING_CONST, IDENTIFIER, _xml_escape,
)

OP_SYMBOLS = {"+", "-", "*", "/", "&", "|", "<", ">", "="}
UNARY_OP = {"-", "~"}
KEYWORD_CONST = {"true", "false", "null", "this"}


class CompilationEngine:
    """Parse Jack tokens and produce an XML parse tree."""

    def __init__(self, tokenizer):
        self.tk = tokenizer
        self.output = []
        self.indent_level = 0

    # ------------------------------------------------------------------
    # XML helpers
    # ------------------------------------------------------------------

    def _open_tag(self, tag):
        self.output.append("  " * self.indent_level + f"<{tag}>")
        self.indent_level += 1

    def _close_tag(self, tag):
        self.indent_level -= 1
        self.output.append("  " * self.indent_level + f"</{tag}>")

    def _write_terminal(self, ttype, value):
        escaped = _xml_escape(str(value))
        self.output.append(
            "  " * self.indent_level + f"<{ttype}> {escaped} </{ttype}>"
        )

    def _eat(self, ttype, value=None):
        tok = self.tk.expect(ttype, value)
        self._write_terminal(tok[0], tok[1])
        return tok

    def _eat_type(self):
        """Eat a type token (int | char | boolean | className)."""
        tok = self.tk.peek()
        if tok[0] == KEYWORD and tok[1] in ("int", "char", "boolean"):
            return self._eat(KEYWORD)
        return self._eat(IDENTIFIER)

    # ------------------------------------------------------------------
    # Program structure
    # ------------------------------------------------------------------

    def compile_class(self):
        self._open_tag("class")
        self._eat(KEYWORD, "class")
        self._eat(IDENTIFIER)          # className
        self._eat(SYMBOL, "{")

        while self.tk.peek() and self.tk.peek()[1] in ("static", "field"):
            self.compile_class_var_dec()

        while self.tk.peek() and self.tk.peek()[1] in ("constructor", "function", "method"):
            self.compile_subroutine()

        self._eat(SYMBOL, "}")
        self._close_tag("class")
        return "\n".join(self.output)

    def compile_class_var_dec(self):
        self._open_tag("classVarDec")
        self._eat(KEYWORD)             # static | field
        self._eat_type()
        self._eat(IDENTIFIER)          # varName

        while self.tk.peek() and self.tk.peek()[1] == ",":
            self._eat(SYMBOL, ",")
            self._eat(IDENTIFIER)

        self._eat(SYMBOL, ";")
        self._close_tag("classVarDec")

    def compile_subroutine(self):
        self._open_tag("subroutineDec")
        self._eat(KEYWORD)             # constructor | function | method

        # return type: void | type
        if self.tk.peek()[1] == "void":
            self._eat(KEYWORD, "void")
        else:
            self._eat_type()

        self._eat(IDENTIFIER)          # subroutineName
        self._eat(SYMBOL, "(")
        self.compile_parameter_list()
        self._eat(SYMBOL, ")")

        self.compile_subroutine_body()
        self._close_tag("subroutineDec")

    def compile_parameter_list(self):
        self._open_tag("parameterList")
        if self.tk.peek() and self.tk.peek()[1] != ")":
            self._eat_type()
            self._eat(IDENTIFIER)

            while self.tk.peek() and self.tk.peek()[1] == ",":
                self._eat(SYMBOL, ",")
                self._eat_type()
                self._eat(IDENTIFIER)

        self._close_tag("parameterList")

    def compile_subroutine_body(self):
        self._open_tag("subroutineBody")
        self._eat(SYMBOL, "{")

        while self.tk.peek() and self.tk.peek()[1] == "var":
            self.compile_var_dec()

        self.compile_statements()
        self._eat(SYMBOL, "}")
        self._close_tag("subroutineBody")

    def compile_var_dec(self):
        self._open_tag("varDec")
        self._eat(KEYWORD, "var")
        self._eat_type()
        self._eat(IDENTIFIER)

        while self.tk.peek() and self.tk.peek()[1] == ",":
            self._eat(SYMBOL, ",")
            self._eat(IDENTIFIER)

        self._eat(SYMBOL, ";")
        self._close_tag("varDec")

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def compile_statements(self):
        self._open_tag("statements")
        while self.tk.peek() and self.tk.peek()[1] in ("let", "if", "while", "do", "return"):
            kw = self.tk.peek()[1]
            if kw == "let":
                self.compile_let()
            elif kw == "if":
                self.compile_if()
            elif kw == "while":
                self.compile_while()
            elif kw == "do":
                self.compile_do()
            elif kw == "return":
                self.compile_return()
        self._close_tag("statements")

    def compile_let(self):
        self._open_tag("letStatement")
        self._eat(KEYWORD, "let")
        self._eat(IDENTIFIER)

        if self.tk.peek() and self.tk.peek()[1] == "[":
            self._eat(SYMBOL, "[")
            self.compile_expression()
            self._eat(SYMBOL, "]")

        self._eat(SYMBOL, "=")
        self.compile_expression()
        self._eat(SYMBOL, ";")
        self._close_tag("letStatement")

    def compile_if(self):
        self._open_tag("ifStatement")
        self._eat(KEYWORD, "if")
        self._eat(SYMBOL, "(")
        self.compile_expression()
        self._eat(SYMBOL, ")")
        self._eat(SYMBOL, "{")
        self.compile_statements()
        self._eat(SYMBOL, "}")

        if self.tk.peek() and self.tk.peek()[1] == "else":
            self._eat(KEYWORD, "else")
            self._eat(SYMBOL, "{")
            self.compile_statements()
            self._eat(SYMBOL, "}")

        self._close_tag("ifStatement")

    def compile_while(self):
        self._open_tag("whileStatement")
        self._eat(KEYWORD, "while")
        self._eat(SYMBOL, "(")
        self.compile_expression()
        self._eat(SYMBOL, ")")
        self._eat(SYMBOL, "{")
        self.compile_statements()
        self._eat(SYMBOL, "}")
        self._close_tag("whileStatement")

    def compile_do(self):
        self._open_tag("doStatement")
        self._eat(KEYWORD, "do")
        # subroutineCall: name ( or name.name (
        self._eat(IDENTIFIER)

        if self.tk.peek()[1] == ".":
            self._eat(SYMBOL, ".")
            self._eat(IDENTIFIER)

        self._eat(SYMBOL, "(")
        self.compile_expression_list()
        self._eat(SYMBOL, ")")
        self._eat(SYMBOL, ";")
        self._close_tag("doStatement")

    def compile_return(self):
        self._open_tag("returnStatement")
        self._eat(KEYWORD, "return")

        if self.tk.peek() and self.tk.peek()[1] != ";":
            self.compile_expression()

        self._eat(SYMBOL, ";")
        self._close_tag("returnStatement")

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def compile_expression(self):
        self._open_tag("expression")
        self.compile_term()

        while self.tk.peek() and self.tk.peek()[1] in OP_SYMBOLS:
            self._eat(SYMBOL)
            self.compile_term()

        self._close_tag("expression")

    def compile_term(self):
        self._open_tag("term")
        tok = self.tk.peek()

        if tok[0] == INT_CONST:
            self._eat(INT_CONST)
        elif tok[0] == STRING_CONST:
            self._eat(STRING_CONST)
        elif tok[0] == KEYWORD and tok[1] in KEYWORD_CONST:
            self._eat(KEYWORD)
        elif tok[1] == "(":
            self._eat(SYMBOL, "(")
            self.compile_expression()
            self._eat(SYMBOL, ")")
        elif tok[1] in UNARY_OP:
            self._eat(SYMBOL)
            self.compile_term()
        elif tok[0] == IDENTIFIER:
            self._eat(IDENTIFIER)
            if self.tk.peek() and self.tk.peek()[1] == "[":
                self._eat(SYMBOL, "[")
                self.compile_expression()
                self._eat(SYMBOL, "]")
            elif self.tk.peek() and self.tk.peek()[1] == "(":
                self._eat(SYMBOL, "(")
                self.compile_expression_list()
                self._eat(SYMBOL, ")")
            elif self.tk.peek() and self.tk.peek()[1] == ".":
                self._eat(SYMBOL, ".")
                self._eat(IDENTIFIER)
                self._eat(SYMBOL, "(")
                self.compile_expression_list()
                self._eat(SYMBOL, ")")

        self._close_tag("term")

    def compile_expression_list(self):
        self._open_tag("expressionList")
        if self.tk.peek() and self.tk.peek()[1] != ")":
            self.compile_expression()
            while self.tk.peek() and self.tk.peek()[1] == ",":
                self._eat(SYMBOL, ",")
                self.compile_expression()
        self._close_tag("expressionList")
