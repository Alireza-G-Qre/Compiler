from scanner import Scanner
import os


class Compiler:

    def __init__(self):
        self.scanner = Scanner()
        self.result = None

    def scan(self, address='input.txt'):

        with open(address, 'r') as f:
            while self.result != 'end':

                self.result = self.scanner.update(f.read(1))
                if not self.result:
                    continue

                yield self.result

    def save_scanner_results(self, directory=''):
        address = os.path.join(directory, 'tests/New/T02/lexical_errors.txt')
        with open(address, 'w') as er:
            er.write(
                self.scanner.lexical_errors_to_string or 'There is no lexical error.')

        address = os.path.join(directory, 'tests/New/T02/symbol_table.txt')
        with open(address, 'w') as sy:
            sy.write(self.scanner.symbol_table_to_string)

        address = os.path.join(directory, 'tests/New/T02/tokens.txt')
        with open(address, 'w') as to:
            to.write(self.scanner.tokens_to_string)

        os.system('cp input.txt {}'.format(os.path.join(directory, 'tests/New/T02/input.txt')))


if __name__ == '__main__':
    c = Compiler()
    _ = [token for token in c.scan()]
    c.save_scanner_results()
