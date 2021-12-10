import re
import os

from itertools import groupby


class Scanner:
    class Token:

        def __init__(self, whatis, token, lineno):
            self.object, self.token, self.lineno = whatis, token, lineno

        def __str__(self):
            return '(%s, %s)' % (self.token, self.object)

    class Error:

        class Base(Exception):

            def __str__(self):
                return '(%s, %s)' % (self.object, self.message)

            message = 'Default error'

            def __init__(self, whatis, lineno):
                self.object, self.lineno = whatis, lineno

        class InvalidNumber(Base):
            message = 'Invalid number'

        class InvalidInput(Base):
            message = 'Invalid input'

        class UnmatchedComment(Base):
            message = 'Unmatched comment'

        class UnclosedComment(Base):
            message = 'Unclosed comment'

    class State:

        @classmethod
        def initialize(cls):
            regex_alphabet = re.compile(r'[a-zA-Z]')
            regex_number = re.compile(r'[0-9]')
            regex_symbol = re.compile(r'[\;\:\,\[\]()\{\}\+\-<]')
            regex_whitespace = re.compile(r'[\s|\n|\t|\v|\f|\r]')

            cls.states = {'start': [
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star'},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal'},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment'},
                {'re': regex_symbol, 'ne': 'symbol'},
                {'re': regex_number, 'ne': 'number'},
                {'re': regex_alphabet, 'ne': 'identifier'},
                {'re': regex_whitespace, 'ne': 'whitespace'},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode'},
            ], 'whitespace': [
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace'},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode', 'refresh': True},
            ], 'symbol': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode', 'refresh': True},
            ], 'number': [
                {'re': regex_number, 'ne': 'number'},
                {'re': regex_alphabet, 'ne': 'invalid_number'},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode'},
            ], 'identifier': [
                {'re': regex_alphabet, 'ne': 'identifier'},
                {'re': regex_number, 'ne': 'identifier'},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode'},
            ], 'symbol_equal': [
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'double_equal'},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode'},
            ], 'double_equal': [
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode', 'refresh': True},
            ], 'symbol_star': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'unmatched_comment'},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode'},
            ], 'starting_comment': [
                {'re': re.compile(r'[/]'), 'ne': 'comment_line'},
                {'re': re.compile(r'[*]'), 'ne': 'ongoing_comment'},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode'},
            ], 'comment_line': [
                {'re': re.compile(r'[^\n]'), 'ne': 'comment_line'},
                {'re': re.compile(r'[\n]'), 'ne': 'whitespace', 'refresh': True},
            ], 'ongoing_comment': [
                {'re': re.compile(r'[*]'), 'ne': 'ending_comment'},
                {'re': re.compile(r'[^*]'), 'ne': 'ongoing_comment'},
            ], 'ending_comment': [
                {'re': re.compile(r'[^/]'), 'ne': 'ongoing_comment'},
                {'re': re.compile(r'[/]'), 'ne': 'start', 'refresh': True},
            ], 'invalid_number': [
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode', 'refresh': True},
            ], 'unmatched_comment': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode', 'refresh': True},
            ], 'panic_mode': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'F2'), 'ne': 'panic_mode', 'refresh': True},
            ]}

    def __init__(self, address):
        self.lexical_errors, self.tokens, self.symbol_table = [], [], []

        self.State.initialize()
        self.current_state = 'start'
        self.address = address
        self.scanning = False
        self.lineno, self.buffer = 1, ''

        self.keywords = [
            'if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return', 'endif'
        ]

        self.symbol_table.extend(self.keywords)
        self.keywords = set(self.keywords)

    @property
    def lexical_errors_to_string(self):
        grouped = groupby(self.lexical_errors, key=lambda x: x.lineno)
        return os.linesep.join([
            F'{lineno}.\t' + ' '.join([str(err) for err in errs]) for lineno, errs in grouped])

    @property
    def tokens_to_string(self):
        grouped = groupby(self.tokens, key=lambda x: x.lineno)
        return os.linesep.join([
            F'{lineno}.\t' + ' '.join([str(token) for token in tokens]) for lineno, tokens in grouped])

    @property
    def symbol_table_to_string(self):
        return '\n'.join([
            F'{lineno}.\t' + symbol for lineno, symbol in enumerate(self.symbol_table, start=1)])

    def update(self, character):

        if not character:
            self._end()
            return

        self._update(character)
        self.lineno += character == '\n'

    def get_next_token(self):
        with open(self.address, 'r') as f:
            self.scanning = True
            counter = 0

            while self.scanning:
                self.update(f.read(1))
                if len(self.tokens) > counter:
                    yield self.tokens[counter]
                    counter += 1

        yield self.Token('$', 'KEYWORD', self.lineno)

    def _save_turn(self, _buffer):

        lineno = self.lineno - self.buffer.count('\n')

        if not _buffer:
            return

        if self.current_state == 'unmatched_comment':
            self.lexical_errors.append(self.Error.UnmatchedComment(_buffer, lineno))

        elif self.current_state == 'invalid_number':
            self.lexical_errors.append(self.Error.InvalidNumber(_buffer, lineno))

        elif self.current_state in ('panic_mode', 'starting_comment'):
            self.lexical_errors.append(self.Error.InvalidInput(_buffer, lineno))

        elif self.current_state == 'identifier':
            token = self.Token(
                _buffer, 'KEYWORD' if _buffer in self.keywords else 'ID', lineno)
            self.tokens.append(token)

            if _buffer not in self.symbol_table:
                self.symbol_table.append(_buffer)
        else:

            token = {
                'number': 'NUM',
                'symbol': 'SYMBOL',
                'symbol_equal': 'SYMBOL',
                'double_equal': 'SYMBOL',
                'symbol_star': 'SYMBOL',
            }.get(self.current_state)

            if token:
                token = self.Token(_buffer, token, lineno)
                self.tokens.append(token)

    def _update(self, ch):

        for checker in self.State.states[self.current_state]:
            if not checker['re'].fullmatch(ch):
                continue

            if 'refresh' in checker:
                self._save_turn(self.buffer.strip())
                self.buffer = ch
                self.current_state = checker['ne']

            else:
                self.buffer += ch
                self.current_state = checker['ne']

            return

        lineno = self.lineno - (self.buffer + ch).count('\n')
        self.lexical_errors.append(
            self.Error.InvalidInput(
                (self.buffer + ch).strip(), lineno))

    def _end(self):
        self._update('\n')
        self.scanning = False
        if self.current_state not in ('ongoing_comment', 'ending_comment'):
            return

        _buffer = self.buffer[:-1][:7] + ('...' if len(self.buffer) > 7 else '')
        _lineno = self.lineno - self.buffer.count('\n') + 1
        self.lexical_errors.append(self.Error.UnclosedComment(_buffer, _lineno))


from treelib import Tree
from uuid import uuid4


class Parser:

    def __init__(self, scanner):
        self.get_next_token = (
            (token.token if token.token in {'NUM', 'ID'} else token.object, token, token.lineno)
            for token in scanner.get_next_token()
        )

        self.states = {
            'program': {
                'transition': [{'path': ['declaration-list', '$'], 'first': ['$', 'int', 'void']}], 'follow': [],
            },
            'declaration-list': {
                'transition': [
                    {'path': ['declaration', 'declaration-list'], 'first': ['int', 'void']},
                    {'path': ['ε'], 'first': ['ε']},
                ],
                'follow': ['break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', '}', 'repeat', '$'],
            },
            'declaration': {
                'transition': [
                    {'path': ['declaration-initial', 'declaration-prime'], 'first': ['int', 'void']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', '}', 'repeat', '$'],
            },
            'declaration-initial': {
                'transition': [
                    {'path': ['type-specifier', 'ID'], 'first': ['int', 'void']},
                ], 'follow': ['[', '(', ';', ',', ')'],
            },
            'declaration-prime': {
                'transition': [
                    {'path': ['fun-declaration-prime'], 'first': ['(']},
                    {'path': ['var-declaration-prime'], 'first': [';', '[']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', '}', 'repeat', '$'],
            },
            'var-declaration-prime': {
                'transition': [
                    {'path': [';'], 'first': [';']},
                    {'path': ['[', 'NUM', ']', ';'], 'first': ['[']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', '}', 'repeat', '$'],
            },
            'fun-declaration-prime': {
                'transition': [
                    {'path': ['(', 'params', ')', 'compound-stmt'], 'first': ['(']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', '}', 'repeat', '$'],
            },
            'type-specifier': {
                'transition': [
                    {'path': ['int'], 'first': ['int']},
                    {'path': ['void'], 'first': ['void']},
                ], 'follow': ['ID'],
            },
            'params': {
                'transition': [
                    {'path': ['int', 'ID', 'param-prime', 'param-list'], 'first': ['int']},
                    {'path': ['void'], 'first': ['void']},
                ], 'follow': [')'],
            },
            'param-list': {
                'transition': [
                    {'path': [',', 'param', 'param-list'], 'first': [',']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': [')'],
            },
            'param': {
                'transition': [
                    {'path': ['declaration-initial', 'param-prime'], 'first': ['int', 'void']},
                ], 'follow': [',', ')'],
            },
            'param-prime': {
                'transition': [
                    {'path': ['[', ']'], 'first': ['[']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': [',', ')'],
            },
            'compound-stmt': {
                'transition': [
                    {'path': ['{', 'declaration-list', 'statement-list', '}'], 'first': ['{']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', '}', 'repeat', 'int', 'void', '$'
                ],
            },
            'statement-list': {
                'transition': [
                    {
                        'path': ['statement', 'statement-list'],
                        'first': ['break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'repeat']
                    },
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['}'],
            },
            'statement': {
                'transition': [
                    {'path': ['expression-stmt'], 'first': ['break', ';', 'ID', '(', 'NUM']},
                    {'path': ['return-stmt'], 'first': ['return']},
                    {'path': ['compound-stmt'], 'first': ['{']},
                    {'path': ['selection-stmt'], 'first': ['if']},
                    {'path': ['iteration-stmt'], 'first': ['repeat']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'expression-stmt': {
                'transition': [
                    {'path': ['expression', ';'], 'first': ['ID', '(', 'NUM']},
                    {'path': ['break', ';'], 'first': ['break']},
                    {'path': [';'], 'first': [';']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'selection-stmt': {
                'transition': [
                    {
                        'path': ['if', '(', 'expression', ')', 'statement', 'else-stmt'],
                        'first': ['if']
                    },
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'else-stmt': {
                'transition': [
                    {'path': ['endif'], 'first': ['endif']},
                    {'path': ['else', 'statement', 'endif'], 'first': ['else']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'iteration-stmt': {
                'transition': [
                    {
                        'path': ['repeat', 'statement', 'until', '(', 'expression', ')'],
                        'first': ['repeat']
                    },
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'return-stmt': {
                'transition': [
                    {'path': ['return', 'return-stmt-prime'], 'first': ['return']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'return-stmt-prime': {
                'transition': [
                    {'path': [';'], 'first': [';']},
                    {'path': ['expression', ';'], 'first': ['ID', '(', 'NUM']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'expression': {
                'transition': [
                    {'path': ['simple-expression-zegond'], 'first': ['(', 'NUM']},
                    {'path': ['ID', 'b'], 'first': ['ID']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'b': {
                'transition': [
                    {'path': ['=', 'expression'], 'first': ['=']},
                    {'path': ['[', 'expression', ']', 'h'], 'first': ['[']},
                    {'path': ['simple-expression-prime'], 'first': ['(', 'ε', '*', '+', '-', '<', '==']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'h': {
                'transition': [
                    {'path': ['=', 'expression'], 'first': ['=']},
                    {'path': ['g', 'd', 'c'], 'first': ['*', '==', '<', '+', '-', 'ε']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'simple-expression-zegond': {
                'transition': [
                    {'path': ['additive-expression-zegond', 'c'], 'first': ['(', 'NUM']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'simple-expression-prime': {
                'transition': [
                    {
                        'path': ['additive-expression-prime', 'c'],
                        'first': ['(', 'ε', '*', '+', '-', '<', '==']
                    },
                ],
                'follow': [',', ')', ']', ';'],
            },
            'c': {
                'transition': [
                    {'path': ['relop', 'additive-expression'], 'first': ['<', '==']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'relop': {
                'transition': [
                    {'path': ['<'], 'first': ['<']},
                    {'path': ['=='], 'first': ['==']},
                ], 'follow': ['(', 'ID', 'NUM'],
            },
            'additive-expression': {
                'transition': [
                    {'path': ['term', 'd'], 'first': ['(', 'ID', 'NUM']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'additive-expression-prime': {
                'transition': [
                    {'path': ['term-prime', 'd'], 'first': ['(', 'ε', '*', '+', '-']},
                ], 'follow': ['<', '==', ',', ')', ']', ';'],
            },
            'additive-expression-zegond': {
                'transition': [
                    {'path': ['term-zegond', 'd'], 'first': ['(', 'NUM']},
                ], 'follow': ['<', '==', ',', ')', ']', ';'],
            },
            'd': {
                'transition': [
                    {'path': ['addop', 'term', 'd'], 'first': ['+', '-']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['<', '==', ',', ')', ']', ';'],
            },
            'addop': {
                'transition': [
                    {'path': ['+'], 'first': ['+']},
                    {'path': ['-'], 'first': ['-']},
                ], 'follow': ['(', 'ID', 'NUM'],
            },
            'term': {
                'transition': [
                    {'path': ['factor', 'g'], 'first': ['(', 'ID', 'NUM']},
                ], 'follow': ['+', '-', '<', '==', ',', ')', ']', ';'],
            },
            'term-prime': {
                'transition': [
                    {'path': ['factor-prime', 'g'], 'first': ['(', 'ε', '*']},
                ], 'follow': ['+', '-', '<', '==', ',', ')', ']', ';'],
            },
            'term-zegond': {
                'transition': [
                    {'path': ['factor-zegond', 'g'], 'first': ['(', 'NUM']},
                ], 'follow': ['+', '-', '<', '==', ',', ')', ']', ';'],
            },
            'g': {
                'transition': [
                    {'path': ['*', 'factor', 'g'], 'first': ['*']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['+', '-', '<', '==', ',', ')', ']', ';'],
            },
            'factor': {
                'transition': [
                    {'path': ['(', 'expression', ')'], 'first': ['(']},
                    {'path': ['ID', 'var-call-prime'], 'first': ['ID']},
                    {'path': ['NUM'], 'first': ['NUM']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'var-call-prime': {
                'transition': [
                    {'path': ['(', 'args', ')'], 'first': ['(']},
                    {'path': ['var-prime'], 'first': ['[', 'ε']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'var-prime': {
                'transition': [
                    {'path': ['[', 'expression', ']'], 'first': ['[']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'factor-prime': {
                'transition': [
                    {'path': ['(', 'args', ')'], 'first': ['(']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'factor-zegond': {
                'transition': [
                    {'path': ['(', 'expression', ')'], 'first': ['(']},
                    {'path': ['NUM'], 'first': ['NUM']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'args': {
                'transition': [
                    {'path': ['arg-list'], 'first': ['ID', '(', 'NUM']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': [')'],
            },
            'arg-list': {
                'transition': [
                    {'path': ['expression', 'arg-list-prime'], 'first': ['ID', '(', 'NUM']},
                ], 'follow': [')'],
            },
            'arg-list-prime': {
                'transition': [
                    {'path': [',', 'expression', 'arg-list-prime'], 'first': [',']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': [')'],
            },
        }

        for state in self.states:
            firsts = set()
            for transition in self.states[state]['transition']:
                transition['first'] = set(transition['first'])
                firsts.update(transition['first'])

            self.states[state]['first'] = firsts

        self.lookahead, self.token, self.lineno = next(self.get_next_token)
        self.none_terminals = set(self.states)
        self.errors, self.up_stack = [], []
        self.parsing = True
        self.pid, self.cnt, self.tree = None, 0, Tree()

    def match(self, entry, parent):

        if entry in self.none_terminals:
            self.proc(entry, parent)
            return

        if self.lookahead == entry or entry == 'ε':
            self.tree.create_node(
                'epsilon' if entry == 'ε' else '$' if entry == '$' else str(self.token),
                identifier=uuid4(), parent=parent)
            if entry not in {'$', 'ε'} and self.lookahead != '$':
                self.lookahead, self.token, self.lineno = next(self.get_next_token)
        else:
            self.errors.append(
                {
                    'message': F'missing {entry.capitalize() if entry in self.none_terminals else entry}',
                    'lineno': self.lineno
                })

    def proc(self, state='program', parent=None):

        idn = uuid4()
        self.tree.create_node(state.capitalize(), identifier=idn, parent=parent)

        for transition in self.states[state]['transition']:
            if self.lookahead in transition['first'] or \
                    (self.lookahead in self.states[state]['follow'] and 'ε' in transition['first']):
                for entry in transition['path']:
                    if self.parsing:
                        self.match(entry, idn)
                return

        self.tree.remove_node(idn)

        if self.lookahead in self.states[state]['follow']:
            self.errors.append(
                {'message': F'missing {state.capitalize() if state in self.none_terminals else state}',
                 'lineno': self.lineno}
            )
            return

        if self.lookahead == '$':
            self.errors.append({'message': 'Unexpected EOF', 'lineno': self.lineno})
            self.parsing = False
            return

        else:
            self.errors.append({'message': F'illegal {self.lookahead}', 'lineno': self.lineno})

        self.lookahead, self.token, self.lineno = next(self.get_next_token)
        self.proc(state, parent=parent)


class Compiler:

    def __init__(self, address):
        self.scanner = Scanner(address)
        self.parser = Parser(self.scanner)

    def compile(self):
        self.parser.proc()
        return self

    def document(self):
        if os.path.exists('parse_tree.txt'): os.remove('parse_tree.txt')
        self.parser.tree.save2file(key=False, filename='parse_tree.txt')

        with open('syntax_errors.txt', 'w') as f:
            errors = '\n'.join([F'#{x["lineno"]} : syntax error, {x["message"]}'
                                for x in self.parser.errors])

            f.write(errors or 'There is no syntax error.')

        return self


if __name__ == '__main__':
    Compiler('input.txt').compile().document()
