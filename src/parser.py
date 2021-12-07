from scanner import Scanner


class Parser:

    class State:

        @classmethod
        def initialize(cls):
            pass

    def __init__(self, scanner):
        self.get_next_token = scanner.get_next_token
