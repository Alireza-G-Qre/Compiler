import os

from scanner import Scanner
from parser import Parser


class Compiler:

    def __init__(self, address):
        self.scanner = Scanner(address)
        self.parser = Parser(self.scanner)


if __name__ == '__main__':
    c = Compiler('input.txt')
    c.parser.proc()
    c.parser.tree.show()

