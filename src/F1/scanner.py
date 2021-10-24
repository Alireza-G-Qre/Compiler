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
            message = 'Default error'

            def __init__(self, whatis, lineno):
                self.object, self.lineno = whatis, lineno

            def __str__(self):
                return '(%s, %s)' % (self.object, self.message)

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
                {'re': re.compile(r'.'), 'ne': 'panic_mode'},
            ], 'whitespace': [
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace'},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode', 'refresh': True},
            ], 'symbol': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode', 'refresh': True},
            ], 'number': [
                {'re': regex_number, 'ne': 'number'},
                {'re': regex_alphabet, 'ne': 'invalid_number'},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode'},
            ], 'identifier': [
                {'re': regex_alphabet, 'ne': 'identifier'},
                {'re': regex_number, 'ne': 'identifier'},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode'},
            ], 'symbol_equal': [
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'double_equal'},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode'},
            ], 'double_equal': [
                {'re': re.compile(r'[*]'), 'ne': 'symbol_star', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode', 'refresh': True},
            ], 'symbol_star': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'unmatched_comment'},
                {'re': re.compile(r'.'), 'ne': 'panic_mode'},
            ], 'starting_comment': [
                {'re': re.compile(r'[/]'), 'ne': 'comment_line'},
                {'re': re.compile(r'[*]'), 'ne': 'ongoing_comment'},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode'},
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
                {'re': re.compile(r'.'), 'ne': 'panic_mode', 'refresh': True},
            ], 'unmatched_comment': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode', 'refresh': True},
            ], 'panic_mode': [
                {'re': regex_whitespace, 'ne': 'whitespace', 'refresh': True},
                {'re': regex_symbol, 'ne': 'symbol', 'refresh': True},
                {'re': regex_number, 'ne': 'number', 'refresh': True},
                {'re': regex_alphabet, 'ne': 'identifier', 'refresh': True},
                {'re': re.compile(r'[=]'), 'ne': 'symbol_equal', 'refresh': True},
                {'re': re.compile(r'[/]'), 'ne': 'starting_comment', 'refresh': True},
                {'re': re.compile(r'.'), 'ne': 'panic_mode', 'refresh': True},
            ]}

    def __init__(self):
        self.lexical_errors, self.tokens, self.symbol_table = [], [], []

        self.State.initialize()
        self.current_state = 'start'
        self.lineno, self.buffer, self.next = 1, '', None

        self.keywords = [
            'if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'
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

        result, self.next = self.next, None

        if not character:
            return self._end()

        self._update(character)
        self.lineno += character == '\n'

        return result

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
            self.next = token

            if _buffer not in self.symbol_table:
                self.symbol_table.append(_buffer)
        else:

            token = {
                'number': 'NUM',
                'symbol': 'SYMBOL',
                'symbol_equal': 'SYMBOL',
                'symbol_star': 'SYMBOL',
                'double_equal': 'SYMBOL'
            }.get(self.current_state)

            if token:
                token = self.Token(_buffer, token, lineno)
                self.next = token
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
        if self.current_state not in ('ongoing_comment', 'ending_comment'):
            return 'end'

        _buffer = self.buffer[:7] + ('...' if len(self.buffer) > 7 else '')
        _lineno = self.lineno - self.buffer.count('\n') + 1
        self.lexical_errors.append(self.Error.UnclosedComment(_buffer, _lineno))

        return 'end'
