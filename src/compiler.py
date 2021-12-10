from scanner import Scanner
from parser import Parser


class Compiler:

    def __init__(self, address):
        self.scanner = Scanner(address)
        self.parser = Parser(self.scanner)

    def compile(self):
        self.parser.proc()
        return self


if __name__ == '__main__':
    Compiler('input.txt').compile()
