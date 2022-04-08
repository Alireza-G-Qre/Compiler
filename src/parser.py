from anytree import NodeMixin

from toMC import CodeGen


class ParserNode(NodeMixin):

    def __init__(self, name, parent=None, children=None, **kwargs):
        self.__dict__.update(kwargs)
        if children:
            self.children = children

        self.name = name
        self.parent = parent

    @classmethod
    def set_nts(cls, none_terminals):
        cls.none_terminals = none_terminals

    def __repr__(self):
        return self.name.capitalize() \
            if self.name in self.none_terminals else self.name


class Parser:

    def __init__(self, scanner):
        self.get_next_token = (
            (token.token if token.token in {'NUM', 'ID'} else token.lexeme, token, token.lineno)
            for token in scanner.get_next_token()
        )

        cg = CodeGen(self)
        self.cg = cg

        self.states = {
            'program': {
                'transition': [{'path': [cg.start_program, 'declaration-list', '$', cg.end_program],
                                'first': ['$', 'int', 'void']}], 'follow': [],
            },
            'declaration-list': {
                'transition': [
                    {'path': ['declaration', cg.semantic_refresh, 'declaration-list'], 'first': ['int', 'void']},
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
                    {'path': [cg.push, 'type-specifier', cg.push, 'ID'], 'first': ['int', 'void']},
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
                    {'path': [cg.declare, ';'], 'first': [';']},
                    {'path': ['[', cg.push, 'NUM', ']', cg.dec_arr, ';'], 'first': ['[']},
                ],
                'follow': ['int', 'void', 'break', ';', 'ID', '(', 'NUM', 'if', 'return', '{', '}', 'repeat', '$'],
            },
            'fun-declaration-prime': {
                'transition': [
                    {'path': [cg.dec_fun, '(', 'params', ')', 'compound-stmt', cg.end_func], 'first': ['(']},
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
                    {'path': [cg.push, 'int', cg.push, 'ID', 'param-prime', 'param-list'], 'first': ['int']},
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
                    {'path': ['[', ']', cg.dec_parr], 'first': ['[']},
                    {'path': ['ε', cg.dec_pvar], 'first': ['ε']},
                ], 'follow': [',', ')'],
            },
            'compound-stmt': {
                'transition': [
                    {'path': [cg.start_scope, '{', 'declaration-list', 'statement-list', '}', cg.finish_scope],
                     'first': ['{']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', '}', 'repeat', 'int', 'void', '$'
                ],
            },
            'statement-list': {
                'transition': [
                    {
                        'path': ['statement', cg.semantic_refresh, 'statement-list'],
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
                    {'path': ['expression', cg.pop3, ';'], 'first': ['ID', '(', 'NUM']},
                    {'path': ['break', cg.scope_break, ';'], 'first': ['break']},
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
                        'path': ['if', '(', 'expression', ')', cg.save, 'statement', 'else-stmt'],
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
                    {'path': [cg.fill_jpf, 'endif'], 'first': ['endif']},
                    {'path': [cg.ifc_action, 'else', 'statement', cg.fill_jp, 'endif'], 'first': ['else']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'iteration-stmt': {
                'transition': [
                    {
                        'path': [cg.loop, 'repeat', 'statement', 'until', '(', 'expression', ')', cg.until],
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
                    {'path': ['return', 'return-stmt-prime', cg.fun_return], 'first': ['return']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'return-stmt-prime': {
                'transition': [
                    {'path': [';'], 'first': [';']},
                    {'path': ['expression', cg.function_return, ';'], 'first': ['ID', '(', 'NUM']},
                ],
                'follow': [
                    'until', 'endif', 'else', 'break', ';', 'ID', '(', 'NUM',
                    'if', 'return', '{', 'repeat', '}'
                ],
            },
            'expression': {
                'transition': [
                    {'path': ['simple-expression-zegond'], 'first': ['(', 'NUM']},
                    {'path': [cg.pid, 'ID', 'b'], 'first': ['ID']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'b': {
                'transition': [
                    {'path': ['=', 'expression', cg.assign], 'first': ['=']},
                    {'path': ['[', 'expression', ']', cg.parr, 'h'], 'first': ['[']},
                    {'path': ['simple-expression-prime'], 'first': ['(', 'ε', '*', '+', '-', '<', '==']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'h': {
                'transition': [
                    {'path': ['=', 'expression', cg.assign], 'first': ['=']},
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
                    {'path': ['relop', 'additive-expression', cg.opera], 'first': ['<', '==']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': [',', ')', ']', ';'],
            },
            'relop': {
                'transition': [
                    {'path': [cg.push, '<'], 'first': ['<']},
                    {'path': [cg.push, '=='], 'first': ['==']},
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
                    {'path': ['addop', 'term', cg.opera, 'd'], 'first': ['+', '-']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['<', '==', ',', ')', ']', ';'],
            },
            'addop': {
                'transition': [
                    {'path': [cg.push, '+'], 'first': ['+']},
                    {'path': [cg.push, '-'], 'first': ['-']},
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
                    {'path': [cg.push, '*', 'factor', cg.opera, 'g'], 'first': ['*']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['+', '-', '<', '==', ',', ')', ']', ';'],
            },
            'factor': {
                'transition': [
                    {'path': ['(', 'expression', ')'], 'first': ['(']},
                    {'path': [cg.pid, 'ID', 'var-call-prime'], 'first': ['ID']},
                    {'path': [cg.pnum, 'NUM'], 'first': ['NUM']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'var-call-prime': {
                'transition': [
                    {'path': ['(', 'args', ')', cg.call], 'first': ['(']},
                    {'path': ['var-prime'], 'first': ['[', 'ε']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'var-prime': {
                'transition': [
                    {'path': ['[', 'expression', ']', cg.parr], 'first': ['[']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'factor-prime': {
                'transition': [
                    {'path': ['(', 'args', ')', cg.call], 'first': ['(']},
                    {'path': ['ε'], 'first': ['ε']},
                ], 'follow': ['*', '<', '==', '+', '-', ',', ')', ']', ';'],
            },
            'factor-zegond': {
                'transition': [
                    {'path': ['(', 'expression', ')'], 'first': ['(']},
                    {'path': [cg.pnum, 'NUM'], 'first': ['NUM']},
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
                    {'path': ['expression', cg.add_args, 'arg-list-prime'], 'first': ['ID', '(', 'NUM']},
                ], 'follow': [')'],
            },
            'arg-list-prime': {
                'transition': [
                    {'path': [',', 'expression', cg.add_args, 'arg-list-prime'], 'first': [',']},
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
        self.actions = []
        self.parsing = True
        self.pid, self.cnt = None, 0
        self.lineno_prev = self.lineno
        ParserNode.set_nts(self.none_terminals)

    def match(self, entry, before):

        if entry in self.none_terminals: return self.proc(entry, before)

        if self.lookahead != entry and entry != 'ε':
            name = entry.capitalize() if entry in self.none_terminals else entry
            self.errors.append({'message': F'missing {name}', 'lineno': self.lineno})
            return

        name = 'epsilon' if entry == 'ε' else '$' if entry == '$' else str(self.token)
        if entry not in {'$', 'ε'} and self.lookahead != '$':
            self.lookahead, self.token, self.lineno = next(self.get_next_token)

        return ParserNode(name)

    def proc(self, state='program', before=None):

        current = ParserNode(state, parent=before)

        for transition in self.states[state]['transition']:
            if self.lookahead in transition['first'] or \
                    (self.lookahead in self.states[state]['follow'] and 'ε' in transition['first']):

                children = []
                for entry in transition['path']:
                    if self.parsing:
                        if type(entry) == str:
                            children.append(self.match(entry, current))
                            continue

                        if self.lineno != self.lineno_prev:
                            self.cg.semantic_refresh()
                            self.lineno_prev = self.lineno

                        entry()
                        self.actions.append(entry.__name__)

                children = [child for child in children if child]
                if children:
                    return ParserNode(state, children=children)

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
        return self.proc(state)
