"""Jack Syntax Analyzer (Project 10) — produces XML parse trees from .jack files."""

import sys
import os

from jack_tokenizer import JackTokenizer
from compilation_engine import CompilationEngine


def analyze_file(jack_file):
    """Analyze a single .jack file and write XML output."""
    with open(jack_file) as f:
        source = f.read()

    tokenizer = JackTokenizer(source)

    # Write tokenizer XML (xxxT.xml)
    token_xml_path = jack_file.replace(".jack", "T.xml")
    with open(token_xml_path, "w") as f:
        f.write(tokenizer.tokens_xml() + "\n")

    # Write parse tree XML (xxx.xml)
    tokenizer.pos = 0  # reset
    engine = CompilationEngine(tokenizer)
    xml = engine.compile_class()

    xml_path = jack_file.replace(".jack", ".xml")
    with open(xml_path, "w") as f:
        f.write(xml + "\n")

    print(f"Analyzed: {jack_file}")


def main(input_path):
    if os.path.isdir(input_path):
        for fname in sorted(os.listdir(input_path)):
            if fname.endswith(".jack"):
                analyze_file(os.path.join(input_path, fname))
    elif input_path.endswith(".jack"):
        analyze_file(input_path)
    else:
        print("Error: input must be a .jack file or a directory")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jack_analyzer.py <file.jack | directory>")
        sys.exit(1)
    main(sys.argv[1])
