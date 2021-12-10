import os

from scanner import Scanner
from parser import Parser


class Compiler:

    def __init__(self, address):
        self.scanner = Scanner(address)
        self.parser = Parser(self.scanner)

    def compile(self):
        self.parser.proc()
        return self

    def document(self):
        self.parser.tree.save2file(key=False, filename='parse_tree.txt')
        with open('syntax_errors.txt', 'w') as f:
            f.writelines(
                F'#{x["lineno"]} : syntax error, {x["message"]}\n'
                for x in self.parser.errors)

        return self


if __name__ == '__main__':
    Compiler('input.txt').compile().document()
