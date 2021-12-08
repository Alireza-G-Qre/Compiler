from scanner import Scanner


class Parser:

    @classmethod
    def initialize(cls):
        cls.states = {
            'program': {
                'transition': [
                    {'path': ['declaration-list', '$'], 'first': ['$', 'ε', 'int', 'void']},
                ], 'follow': ['$'],
            },
            'declaration-list': {
                'transition': [
                    {'path': ['declaration', 'declaration-list'], 'first': ['int', 'void']},
                    {'path': ['ε'], 'first': ['ε']},
                ],
                'follow': ['break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'repeat', '$'],
            },
            'declaration': {
                'transition': [
                    {'path': ['declaration-initial', 'declaration-prime'], 'first': ['int', 'void']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'repeat', '$'],
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
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'repeat', '$'],
            },
            'var-declaration-prime': {
                'transition': [
                    {'path': [';'], 'first': [';']},
                    {'path': ['[', 'NUM', ']', ';'], 'first': ['[']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'repeat', '$'],
            },
            'fun-declaration-prime': {
                'transition': [
                    {'path': ['(', 'params', ')', 'compound-stmt'], 'first': ['(']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', 'repeat', '$'],
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
                    'if', 'return', '{', 'repeat', 'int', 'void', '$', '}'
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
                    {'path': ['expression'], 'first': ['(', 'NUM', 'ID']},
                    {'path': ['[', 'expression', ']', 'h'], 'first': ['[']},
                    {'path': ['simple-expression-prime'], 'first': ['(', 'ε', '*', '+', '-', '<', '==']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'h': {
                'transition': [
                    {'path': ['expression'], 'first': ['(', 'NUM', 'ID']},
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

        for state in cls.states:
            cls.states[state]['first'], cls.states[state]['follow'] = \
                set(cls.states[state]['first']), set(cls.states[state]['follow'])

    def __init__(self, scanner):
        self.get_next_token = scanner.get_next_token
        self.initialize()
        self.current_state = 'program'

    def process(self):

        def match(next_token):
            pass

        for token in self.get_next_token:
            pass
