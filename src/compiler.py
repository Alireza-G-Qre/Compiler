import os

from scanner import Scanner
from parser import Parser


class Compiler:

    def __init__(self, address):
        self.scanner = Scanner(address)
        self.parser = Parser(self.scanner)


if __name__ == '__main__':
    c = Compiler('/home/alireza/Project/qre_compiler/src/tests/T01/input.txt')
    c.parser.proc()
    c.parser.tree.show(key=False)
    print(c.parser.founds)

