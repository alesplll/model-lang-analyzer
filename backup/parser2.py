# parser2.py
import sys


class ParserError(Exception):
    pass


class Parser:
    def __init__(self, token_file):
        self.identifiers = []
        self.numbers = []
        self.tokens = []
        self.current = 0
        self.load_tokens(token_file)

        # Define service words and limiters as per Lexer
        self.service_words = ['while', 'readln', 'for', 'to', 'step', 'next',
                              '%', '!', '$', 'writeln', 'if', 'else', 'true', 'false', 'begin', 'end', 'not']
        self.limiters = ['{', '}', ';', '[', ']', ':=', '==', '!=', '<', '<=', '>', '>=',
                         '+', '-', '*', '/', '/*', '*/', '(', ')', ',', '||', '&&']

    def load_tokens(self, token_file):
        with open(token_file, 'r') as file:
            lines = file.readlines()

        tokens_section = False
        for line in lines:
            line = line.strip()
            if line.startswith("Tokens with Words and Positions:"):
                tokens_section = True
                continue
            if tokens_section:
                if line.startswith('(') and line.endswith(')'):
                    # Safely evaluate the tuple
                    try:
                        token = eval(line)
                        if len(token) == 5:
                            # (group, index, line_num, col_num, word)
                            self.tokens.append(token)
                        else:
                            raise ParserError(f"Invalid token format: {token}")
                    except Exception as e:
                        raise ParserError(
                            f"Failed to parse token '{line}': {e}")

    def current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def get_word(self, token):
        group, index, line_num, col_num, word = token
        if group == 1:
            return self.service_words[index - 1]
        elif group == 2:
            return self.limiters[index - 1]
        elif group == 3:
            return self.identifiers[index - 1]
        elif group == 4:
            return self.numbers[index - 1]
        else:
            return "Unknown"

    def consume(self, expected_group, expected_index):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input")
        group, index, line_num, col_num, word = token
        if group != expected_group or index != expected_index:
            expected_word = self.get_word(
                (expected_group, expected_index, 0, 0, ''))
            raise ParserError(
                f"Parsing error at line {line_num}, column {col_num}:\n"
                f"Unexpected token '{word}', expected '{expected_word}'"
            )
        self.current += 1
        return token

    def match(self, expected_group, expected_index):
        token = self.current_token()
        if token and token[0] == expected_group and token[1] == expected_index:
            self.current += 1
            return True
        return False

    def analyze(self):
        self.P()
        if self.current < len(self.tokens):
            token = self.current_token()
            if len(token) == 5:
                group, index, line_num, col_num, word = token
                remaining = self.get_word(token)
                raise ParserError(
                    f"Extra tokens after parsing complete at line {
                        line_num}, column {col_num}:\n"
                    f"Unexpected token '{remaining}'"
                )
            else:
                raise ParserError("Extra tokens after parsing complete")

    # Grammar Rules

    # P → { D1 B }
    def P(self):
        self.consume(2, self.get_limiter_index('{'))
        self.D1()
        self.B()
        self.consume(2, self.get_limiter_index('}'))

    # D1 → { D }*
    def D1(self):
        while True:
            token = self.current_token()
            if token and token[0] == 1 and token[1] in [
                self.get_service_word_index('%'),
                self.get_service_word_index('!'),
                self.get_service_word_index('$')
            ]:
                self.D()
            else:
                break

    # D → ServiceWord Identifier { ',' Identifier }
    def D(self):
        token = self.current_token()
        if token and token[0] == 1 and token[1] in [
            self.get_service_word_index('%'),
            self.get_service_word_index('!'),
            self.get_service_word_index('$')
        ]:
            self.consume(token[0], token[1])
            self.I()
            while self.match(2, self.get_limiter_index(',')):
                self.I()
            self.consume(2, self.get_limiter_index(';'))
        else:
            raise ParserError("Expected variable declaration")

    # B → begin { S ';' } end
    def B(self):
        self.consume(1, self.get_service_word_index('begin'))
        while True:
            token = self.current_token()
            if token and (token[0] == 1 and token[1] == self.get_service_word_index('end')):
                break
            self.S()
            self.consume(2, self.get_limiter_index(';'))
        self.consume(1, self.get_service_word_index('end'))

    # S → I := E | if E B else B | while E B | for S to E step S B next | B | readln(I) | writeln(E)
    def S(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input in statement")

        group, index, line_num, col_num, word = token
        if group == 3:  # Identifier
            self.I()
            self.consume(2, self.get_limiter_index(':='))
            self.E()
        elif group == 1 and index == self.get_service_word_index('if'):
            self.consume(1, self.get_service_word_index('if'))
            self.E()
            self.B()
            if self.match(1, self.get_service_word_index('else')):
                self.B()
        elif group == 1 and index == self.get_service_word_index('while'):
            self.consume(1, self.get_service_word_index('while'))
            self.E()
            self.B()
            self.S()
        elif group == 1 and index == self.get_service_word_index('for'):
            self.consume(1, self.get_service_word_index('for'))
            self.I()
            self.consume(2, self.get_limiter_index(':='))
            self.E()
            self.consume(1, self.get_service_word_index('to'))
            self.E()
            self.consume(1, self.get_service_word_index('step'))
            self.I()
            self.consume(2, self.get_limiter_index(':='))
            self.E()
            self.B()
            self.consume(1, self.get_service_word_index('next'))
        elif group == 1 and index == self.get_service_word_index('readln'):
            self.consume(1, self.get_service_word_index('readln'))
            self.consume(2, self.get_limiter_index('('))
            self.I()
            while self.match(2, self.get_limiter_index(',')):
                self.I()
            self.consume(2, self.get_limiter_index(')'))
        elif group == 1 and index == self.get_service_word_index('writeln'):
            self.consume(1, self.get_service_word_index('writeln'))
            self.consume(2, self.get_limiter_index('('))
            self.E()
            while self.match(2, self.get_limiter_index(',')):
                self.E()
            self.consume(2, self.get_limiter_index(')'))
        elif group == 1 and index == self.get_service_word_index('begin'):
            self.B()
        else:
            raise ParserError(
                f"Invalid statement starting with token '{self.get_word(token)}' at line {
                    line_num}, column {col_num}"
            )

    # E → E1 [ RelationOp E1 ]
    def E(self):
        self.E1()
        token = self.current_token()
        relation_ops = ['<', '>', '<=', '>=', '==', '!=']
        relation_indices = [self.get_limiter_index(op) for op in relation_ops]
        if token and token[0] == 2 and token[1] in relation_indices:
            self.consume(token[0], token[1])
            self.E1()

    # E1 → T { [ + | - | || ] T }

    def E1(self):
        self.T()
        while True:
            token = self.current_token()
            if token and token[0] == 2 and token[1] in [
                self.get_limiter_index('+'),
                self.get_limiter_index('-')
            ]:
                self.consume(token[0], token[1])
                self.T()
            elif token and token[0] == 1 and token[1] == self.get_limiter_index('||'):
                self.consume(token[0], token[1])
                self.T()
            else:
                break

    # T → F { [ * | / | && ] F }
    def T(self):
        self.F()
        while True:
            token = self.current_token()
            if token and token[0] == 2 and token[1] in [
                self.get_limiter_index('*'),
                self.get_limiter_index('/')
            ]:
                self.consume(token[0], token[1])
                self.F()
            elif token and token[0] == 1 and token[1] == self.get_limiter_index('&&'):
                self.consume(token[0], token[1])
                self.F()
            else:
                break

    # F → I | N | L | not F | ( E )
    def F(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input in expression")
        group, index, line_num, col_num, word = token
        if group == 3:  # Identifier
            self.I()
        elif group == 4:  # Number
            self.N()
        elif group == 1 and index in [
            self.get_service_word_index('true'),
            self.get_service_word_index('false')
        ]:
            self.L()
        elif group == 1 and index == self.get_service_word_index('not'):
            self.consume(1, self.get_service_word_index('not'))
            self.F()
        elif group == 2 and index == self.get_limiter_index('('):
            self.consume(2, self.get_limiter_index('('))
            self.E()
            self.consume(2, self.get_limiter_index(')'))
        else:
            raise ParserError(
                f"Invalid factor starting with token '{self.get_word(token)}' at line {
                    line_num}, column {col_num}"
            )

    # L → true | false
    def L(self):
        token = self.current_token()
        if token and (token[0], token[1]) == (1, self.get_service_word_index('true')):
            self.consume(1, self.get_service_word_index('true'))
        elif token and (token[0], token[1]) == (1, self.get_service_word_index('false')):
            self.consume(1, self.get_service_word_index('false'))
        else:
            if token and len(token) == 5:
                group, index, line_num, col_num, word = token
                raise ParserError(
                    f"Parsing error at line {line_num}, column {col_num}:\n"
                    f"Expected 'true' or 'false', found '{word}'"
                )
            else:
                raise ParserError("Expected 'true' or 'false'")

    # I → Identifier
    def I(self):
        token = self.current_token()
        if token and token[0] == 3:
            self.consume(3, token[1])
        else:
            if token and len(token) == 5:
                group, index, line_num, col_num, word = token
                raise ParserError(
                    f"Expected identifier at line {
                        line_num}, column {col_num}:\n"
                    f"Found '{word}'"
                )
            else:
                raise ParserError(
                    "Expected identifier but reached end of input")

    # N → Number
    def N(self):
        token = self.current_token()
        if token and token[0] == 4:
            self.consume(4, token[1])
        else:
            if token and len(token) == 5:
                group, index, line_num, col_num, word = token
                raise ParserError(
                    f"Expected number at line {line_num}, column {col_num}:\n"
                    f"Found '{word}'"
                )
            else:
                raise ParserError("Expected number but reached end of input")

    # Helper methods to get service word and limiter indices
    def get_service_word_index(self, word):
        if word in self.service_words:
            return self.service_words.index(word) + 1
        raise ValueError(f"Unknown service word: {word}")

    def get_limiter_index(self, limiter):
        if limiter in self.limiters:
            return self.limiters.index(limiter) + 1
        raise ValueError(f"Unknown limiter: {limiter}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python parser2.py <token_file>")
        sys.exit(1)

    token_file = sys.argv[1]
    parser = Parser(token_file)
    try:
        parser.analyze()
        print("___Parsing completed successfully___")
    except ParserError as e:
        print(f"Parsing error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
