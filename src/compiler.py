from lexeme import Scanner
from parser import Parser

if __name__ == '__main__': Parser(Scanner('input.txt')).proc()
