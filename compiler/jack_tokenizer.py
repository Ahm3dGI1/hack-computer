"""Jack tokenizer — breaks .jack source into tokens."""

import re

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static",
    "var", "int", "char", "boolean", "void", "true", "false", "null",
    "this", "let", "do", "if", "else", "while", "return",
}

SYMBOLS = set("{}()[].,;+-*/&|<>=~")

# Token types
KEYWORD = "keyword"
SYMBOL = "symbol"
INT_CONST = "integerConstant"
STRING_CONST = "stringConstant"
IDENTIFIER = "identifier"

# Regex for tokenizing (order matters)
_TOKEN_RE = re.compile(
    r"""
    (/\*\*?.*?\*/)  |  # block comment
    (//[^\n]*)      |  # line comment
    (\d+)           |  # integer constant
    ("([^"\n]*)")   |  # string constant (group 4 = inner text)
    ([a-zA-Z_]\w*)  |  # keyword or identifier
    ([{}()\[\].,;+\-*/&|<>=~])  # symbol
    """,
    re.VERBOSE | re.DOTALL,
)


class JackTokenizer:
    def __init__(self, source):
        self.tokens = []
        self._tokenize(source)
        self.pos = 0

    def _tokenize(self, source):
        for m in _TOKEN_RE.finditer(source):
            if m.group(1) or m.group(2):
                continue  # skip comments
            if m.group(3):
                self.tokens.append((INT_CONST, int(m.group(3))))
            elif m.group(4):
                self.tokens.append((STRING_CONST, m.group(5)))
            elif m.group(6):
                word = m.group(6)
                if word in KEYWORDS:
                    self.tokens.append((KEYWORD, word))
                else:
                    self.tokens.append((IDENTIFIER, word))
            elif m.group(7):
                self.tokens.append((SYMBOL, m.group(7)))

    def has_more_tokens(self):
        return self.pos < len(self.tokens)

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def token_type(self):
        return self.tokens[self.pos][0]

    def token_value(self):
        return self.tokens[self.pos][1]

    def expect(self, ttype, value=None):
        """Consume and return the next token, raising if it doesn't match."""
        tok = self.advance()
        if tok[0] != ttype or (value is not None and tok[1] != value):
            raise SyntaxError(
                f"Expected ({ttype}, {value!r}), got ({tok[0]}, {tok[1]!r})"
            )
        return tok

    def tokens_xml(self):
        """Return XML representation of all tokens."""
        lines = ["<tokens>"]
        for ttype, value in self.tokens:
            escaped = _xml_escape(str(value))
            lines.append(f"<{ttype}> {escaped} </{ttype}>")
        lines.append("</tokens>")
        return "\n".join(lines)


def _xml_escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
