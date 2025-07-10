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
        self.symbol_table = {}  # For semantic checks
        # Declaration symbols to types
        self.declaration_types = {'%': 'int', '!': 'float', '$': 'string'}
        self.load_tokens(token_file)

        # Define service words and limiters as per Lexer
        self.service_words = ['while', 'readln', 'for', 'to', 'step', 'next',
                              '%', '!', '$', 'writeln', 'if', 'else', 'true', 'false', 'begin', 'end', 'not', 'do']
        self.limiters = ['{', '}', ';', '[', ']', ':=', '==', '!=', '<', '<=', '>', '>=',
                         '+', '-', '*', '/', '/*', '*/', '(', ')', ',', '||', '&&']

    def load_tokens(self, token_file):
        with open(token_file, 'r') as file:
            lines = file.readlines()

        tokens_section = False
        identifiers_section = False
        numbers_section = False
        for line in lines:
            line = line.strip()
            if line.startswith("Identifiers:"):
                identifiers_section = True
                numbers_section = False
                tokens_section = False
                continue
            elif line.startswith("Numbers:"):
                numbers_section = True
                identifiers_section = False
                tokens_section = False
                continue
            elif line.startswith("Tokens with Words and Positions:"):
                tokens_section = True
                identifiers_section = False
                numbers_section = False
                continue
            if identifiers_section:
                if line:
                    self.identifiers.append(line)
            elif numbers_section:
                if line:
                    self.numbers.append(line)
            elif tokens_section:
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
            if 0 < index <= len(self.identifiers):
                return self.identifiers[index - 1]
            else:
                raise ParserError(f"Identifier index out of range: {index}")
        elif group == 4:
            if 0 < index <= len(self.numbers):
                return self.numbers[index - 1]
            else:
                raise ParserError(f"Number index out of range: {index}")
        else:
            return "Unknown"

    def consume(self, expected_group, expected_index):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input")
        group, index, line_num, col_num, word = token
        if group != expected_group or index != expected_index:
            expected_word = self.get_expected_word(
                expected_group, expected_index)
            raise ParserError(
                f"Parsing error at line {line_num}, column {col_num}:\n"
                f"Unexpected token '{self.get_word(token)}', expected '{
                    expected_word}'"
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

    # D → DeclarationWord I { , I } ;
    def D(self):
        token = self.current_token()
        if token and token[0] == 1 and token[1] in [
            self.get_service_word_index('%'),
            self.get_service_word_index('!'),
            self.get_service_word_index('$')
        ]:
            decl_word = self.get_word(token)
            var_type = self.declaration_types[decl_word]
            self.consume(token[0], token[1])
            identifier_token = self.current_token()
            if identifier_token and identifier_token[0] == 3:
                identifier = self.get_word(identifier_token)
                if identifier in self.symbol_table:
                    line_num, col_num = identifier_token[2], identifier_token[3]
                    raise ParserError(
                        f"Duplicate declaration of identifier '{
                            identifier}' at line {line_num}, column {col_num}"
                    )
                self.symbol_table[identifier] = var_type
                self.consume(3, identifier_token[1])
            else:
                self.I()
            while self.match(2, self.get_limiter_index(',')):
                identifier_token = self.current_token()
                if identifier_token and identifier_token[0] == 3:
                    identifier = self.get_word(identifier_token)
                    if identifier in self.symbol_table:
                        line_num, col_num = identifier_token[2], identifier_token[3]
                        raise ParserError(
                            f"Duplicate declaration of identifier '{
                                identifier}' at line {line_num}, column {col_num}"
                        )
                    self.symbol_table[identifier] = var_type
                    self.consume(3, identifier_token[1])
                else:
                    self.I()
            self.consume(2, self.get_limiter_index(';'))
        else:
            raise ParserError("Expected variable declaration")

    # B → begin { S ; } end
    def B(self):
        self.consume(1, self.get_service_word_index('begin'))
        while True:
            token = self.current_token()
            if token and (token[0] == 1 and token[1] == self.get_service_word_index('end')):
                break
            self.S()
            self.consume(2, self.get_limiter_index(';'))
        self.consume(1, self.get_service_word_index('end'))

    # S → I := E | if E B else B | while E B | readln ( I { , I } ) | writeln ( E { , E } ) | B
    def S(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input in statement")

        group, index, line_num, col_num, word = token

        if group == 3:  # Identifier
            identifier = self.get_word(token)
            var_type = self.get_identifier_type(identifier, line_num, col_num)
            self.consume(3, token[1])
            self.consume(2, self.get_limiter_index(':='))
            expr_type = self.E()
            if not self.types_compatible(var_type, expr_type):
                raise ParserError(
                    f"Type mismatch in assignment to '{
                        identifier}' at line {line_num}, column {col_num}:\n"
                    f"Variable type: {var_type}, Expression type: {expr_type}"
                )
        elif group == 1 and index == self.get_service_word_index('if'):
            self.consume(1, self.get_service_word_index('if'))
            condition_type = self.E()
            if condition_type != 'boolean':
                raise ParserError(
                    f"Condition in 'if' statement must be boolean at line {
                        line_num}, column {col_num}"
                )
            self.B()
            if self.match(1, self.get_service_word_index('else')):
                self.B()
        elif group == 1 and index == self.get_service_word_index('while'):
            self.consume(1, self.get_service_word_index('while'))
            condition_type = self.E()
            if condition_type != 'boolean':
                raise ParserError(
                    f"Condition in 'while' statement must be boolean at line {
                        line_num}, column {col_num}"
                )
            self.B()
        elif group == 1 and index == self.get_service_word_index('for'):
            self.consume(1, self.get_service_word_index('for'))
            self.I()
            self.consume(2, self.get_limiter_index(':='))
            self.E()
            self.consume(1, self.get_service_word_index('to'))
            condition_type = self.E()
            if condition_type != 'boolean':
                raise ParserError(
                    f"Condition in 'for' statement must be integer at line {
                        line_num}, column {col_num}"
                )
            self.consume(1, self.get_service_word_index('step'))
            self.I()
            self.consume(2, self.get_limiter_index(':='))
            self.E()
            self.B()
            self.consume(1, self.get_service_word_index('next'))
        elif group == 1 and index == self.get_service_word_index('readln'):
            self.consume(1, self.get_service_word_index('readln'))
            self.consume(2, self.get_limiter_index('('))
            identifier = self.expect_identifier()
            while self.match(2, self.get_limiter_index(',')):
                identifier = self.expect_identifier()
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
        type_e1 = self.E1()
        token = self.current_token()
        relation_ops = ['<', '>', '<=', '>=', '==', '!=']
        relation_indices = [self.get_limiter_index(op) for op in relation_ops]
        if token and token[0] == 2 and token[1] in relation_indices:
            operator = self.get_word(token)
            self.consume(token[0], token[1])
            type_e2 = self.E1()
            if not self.types_compatible(type_e1, type_e2):
                raise ParserError(
                    f"Type mismatch in relation operation '{
                        operator}' at line {token[2]}, column {token[3]}"
                )
            return 'boolean'
        else:
            return type_e1

    # E1 → T { [ + | - | || ] T }
    def E1(self):
        type_t = self.T()
        while True:
            token = self.current_token()
            if token and token[0] == 2 and token[1] in [
                self.get_limiter_index('+'),
                self.get_limiter_index('-')
            ]:
                operator = self.get_word(token)
                self.consume(token[0], token[1])
                type_t2 = self.T()
                type_t = self.combine_types(type_t, type_t2, operator)
            elif token and token[0] == 2 and token[1] == self.get_limiter_index('||'):
                operator = self.get_word(token)
                self.consume(token[0], token[1])
                type_t2 = self.T()
                if type_t != 'boolean' or type_t2 != 'boolean':
                    raise ParserError(
                        f"Logical operator '{
                            operator}' requires boolean operands"
                    )
                type_t = 'boolean'
            else:
                break
        return type_t

    # T → F { [ * | / | && ] F }
    def T(self):
        type_f = self.F()
        while True:
            token = self.current_token()
            if token and token[0] == 2 and token[1] in [
                self.get_limiter_index('*'),
                self.get_limiter_index('/')
            ]:
                operator = self.get_word(token)
                self.consume(token[0], token[1])
                type_f2 = self.F()
                type_f = self.combine_types(type_f, type_f2, operator)
            elif token and token[0] == 2 and token[1] == self.get_limiter_index('&&'):
                operator = self.get_word(token)
                self.consume(token[0], token[1])
                type_f2 = self.F()
                if type_f != 'boolean' or type_f2 != 'boolean':
                    raise ParserError(
                        f"Logical operator '{
                            operator}' requires boolean operands"
                    )
                type_f = 'boolean'
            else:
                break
        return type_f

    # F → I | N | L | not F | ( E )
    def F(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input in expression")
        group, index, line_num, col_num, word = token
        if group == 3:  # Identifier
            identifier = self.get_word(token)
            var_type = self.get_identifier_type(identifier, line_num, col_num)
            self.consume(3, token[1])
            return var_type
        elif group == 4:  # Number
            num_value = self.get_word(token)
            if '.' in num_value:
                num_type = 'float'
            else:
                num_type = 'int'
            self.consume(4, token[1])
            return num_type
        elif group == 1 and index in [
            self.get_service_word_index('true'),
            self.get_service_word_index('false')
        ]:
            self.L()
            return 'boolean'
        elif group == 1 and index == self.get_service_word_index('not'):
            self.consume(1, self.get_service_word_index('not'))
            type_f = self.F()
            if type_f != 'boolean':
                raise ParserError(
                    f"Operator 'not' requires boolean operand at line {
                        line_num}, column {col_num}"
                )
            return 'boolean'
        elif group == 2 and index == self.get_limiter_index('('):
            self.consume(2, self.get_limiter_index('('))
            type_e = self.E()
            self.consume(2, self.get_limiter_index(')'))
            return type_e
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
                line_num, col_num = token[2], token[3]
                raise ParserError(
                    f"Expected 'true' or 'false' at line {
                        line_num}, column {col_num}"
                )
            else:
                raise ParserError("Expected 'true' or 'false'")

    # I → Identifier
    def I(self):
        token = self.current_token()
        if token and token[0] == 3:
            identifier = self.get_word(token)
            if identifier not in self.symbol_table:
                line_num, col_num = token[2], token[3]
                raise ParserError(
                    f"Undeclared identifier '{identifier}' at line {
                        line_num}, column {col_num}"
                )
            self.consume(3, token[1])
        else:
            if token and len(token) == 5:
                line_num, col_num = token[2], token[3]
                raise ParserError(
                    f"Expected identifier at line {line_num}, column {
                        col_num}, found '{self.get_word(token)}'"
                )
            else:
                raise ParserError(
                    "Expected identifier but reached end of input")

    def expect_identifier(self):
        token = self.current_token()
        if token and token[0] == 3:
            identifier = self.get_word(token)
            if identifier not in self.symbol_table:
                line_num, col_num = token[2], token[3]
                raise ParserError(
                    f"Undeclared identifier '{identifier}' at line {
                        line_num}, column {col_num}"
                )
            self.consume(3, token[1])
            return identifier
        else:
            if token and len(token) == 5:
                line_num, col_num = token[2], token[3]
                raise ParserError(
                    f"Expected identifier at line {line_num}, column {
                        col_num}, found '{self.get_word(token)}'"
                )
            else:
                raise ParserError(
                    "Expected identifier but reached end of input")

    def get_identifier_type(self, identifier, line_num, col_num):
        if identifier in self.symbol_table:
            return self.symbol_table[identifier]
        else:
            raise ParserError(
                f"Undeclared identifier '{identifier}' at line {
                    line_num}, column {col_num}"
            )

    # N → Number
    def N(self):
        token = self.current_token()
        if token and token[0] == 4:
            self.consume(4, token[1])
        else:
            if token and len(token) == 5:
                line_num, col_num = token[2], token[3]
                raise ParserError(
                    f"Expected number at line {line_num}, column {
                        col_num}, found '{self.get_word(token)}'"
                )
            else:
                raise ParserError("Expected number but reached end of input")

    # Helper methods to get service word and limiter indices
    def get_service_word_index(self, word):
        if word in self.service_words:
            return self.service_words.index(word) + 1
        else:
            raise ValueError(f"Unknown service word: {word}")

    def get_limiter_index(self, limiter):
        if limiter in self.limiters:
            return self.limiters.index(limiter) + 1
        else:
            raise ValueError(f"Unknown limiter: {limiter}")

    def get_expected_word(self, group, index):
        if group == 1:
            return self.service_words[index - 1]
        elif group == 2:
            return self.limiters[index - 1]
        elif group == 3:
            if 0 < index <= len(self.identifiers):
                return self.identifiers[index - 1]
            else:
                return "identifier"
        elif group == 4:
            if 0 < index <= len(self.numbers):
                return self.numbers[index - 1]
            else:
                return "number"
        else:
            return "unknown"

    # Semantic Helper Methods
    def combine_types(self, type1, type2, operator):
        arithmetic_ops = ['+', '-', '*', '/']
        if operator in arithmetic_ops:
            if 'string' in [type1, type2]:
                raise ParserError(
                    f"Arithmetic operator '{
                        operator}' cannot be applied to 'string' type"
                )
            if 'float' in [type1, type2]:
                return 'float'
            else:
                return 'int'
        elif operator == 'relation':
            if type1 != type2:
                return False
            else:
                return True
        else:
            raise ParserError(f"Unknown operator '{operator}'")

    def types_compatible(self, var_type, expr_type):
        if var_type == expr_type:
            return True
        elif var_type == 'float' and expr_type == 'int':
            return True
        else:
            return False


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


# 4 Семантические проверки реализовано:

# 1. Проверка наличия повторного объявления идентификаторов. Тест 4
# 2. Проверка наличия неопределенных идентификаторов. Тест 5
# 3. Проверка совпадения типов выражений и переменных. Тест 6
# 4. Проверка наличия логического выражения в качестве условия в if, while, for. Тест 7
