# <выражение>::= <операнд>{<операции_группы_отношения> <операнд>}
# <операнд>::= <слагаемое> {<операции_группы_сложения> <слагаемое>}
# <слагаемое>::= <множитель> {<операции_группы_умножения> <множитель>}
# <множитель>::= <идентификатор> | <число> | <логическая_константа> |
# <унарная_операция> <множитель> | «(»<выражение>«)»
# <число>::= <целое> | <действительное>
# <логическая_константа>::= true | false

# <идентификатор>::= <буква> {<буква> | <цифра>}
# <буква>::= A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P | Q | R | S | T |
#  U | V | W | X | Y | Z | a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p
#  q | r | s | t | u | v | w | x | y | z
# <цифра>::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

# <целое>::= <двоичное> | <восьмеричное> | <десятичное> |
#  <шестнадцатеричное>
# <двоичное>::= {/ 0 | 1 /} (B | b)
# <восьмеричное>::= {/ 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 /} (O | o)
# <десятичное>::= {/ <цифра> /} [D | d]
# <шестнадцатеричное>::= <цифра> {<цифра> | A | B | C | D | E | F | a | b |
#  c | d | e | f} (H | h)

# <действительное>::= <числовая_строка> <порядок> |
#  [<числовая_строка>] . <числовая_строка> [порядок]
# <числовая_строка>::= {/ <цифра> /}
# <порядок>::= ( E | e )[+ | -] <числовая_строка>


# Операции языка - <операции_группы_отношения>::= != | = = | < | <= | > | >=
# <операции_группы_сложения>:: = + | - | ||
# <операции_группы_умножения>:: = * | / | &&
# <унарная_операция>::= not

# Структура программы - <программа>::= «{» {/ (<описание> | <оператор>) ; /} «}»
# Синтаксис команд описания данных - <описание>::= <тип> <идентификатор> { , <идентификатор> }
# Описание типов(в порядке следования: целый, действительный, логический) - <тип>::= % | ! | $
# Синтаксис оператора - <составной>::= begin <оператор> { ; <оператор> } end
# Оператор присваивания - <присваивания>::= <идентификатор> := <выражение>
# Оператор условного перехода - <условный>::= if «(»<выражение> «)» <оператор> [else <оператор>]
# Синтаксис оператора цикла с фиксированным числом повторений -
# <фиксированного_цикла>::= for <присваивания> to <выражение> [step <выражение > ] < оператор > next
# Синтаксис условного оператора цикла - <условного_цикла>::= while «(»<выражение> «)» <оператор>
# Синтаксис оператора ввода - <ввода>::= readln идентификатор {, <идентификатор> }
# Синтаксис оператора вывода - <вывода>::= writeln <выражение> {, <выражение> }
# Синтаксис многострочных комментариев - Начало::= /* Конец::= */


# parser.py
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
                              '%', '!', '$', 'writeln', 'if', 'else', 'true', 'false', 'begin', 'end']
        self.limiters = ['{', '}', ';', '[', ']', ':=', '==', '!=', '<', '<=', '>', '>=',
                         '+', '-', '*', '/', '/*', '*/', '(', ')', ',', '||', '&&']

    def load_tokens(self, token_file):
        with open(token_file, 'r') as file:
            section = None
            for line in file:
                line = line.strip()
                if line == "Identifiers:":
                    section = 'identifiers'
                    continue
                elif line == "Numbers:":
                    section = 'numbers'
                    continue
                elif line == "Tokens:":
                    section = 'tokens'
                    continue
                elif line == "Tokens with Words:":
                    section = 'tokens_with_words'
                    continue

                if section == 'identifiers':
                    if line:
                        self.identifiers.append(line)
                elif section == 'numbers':
                    if line:
                        self.numbers.append(line)
                elif section == 'tokens':
                    if line:
                        token = eval(line)  # (group, index)
                        self.tokens.append(token)
                elif section == 'tokens_with_words':
                    if line:
                        token = eval(line)  # (group, index, word)
                        # Only (group, index) needed for parsing
                        self.tokens.append(token[:2])

    def current_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def consume(self, expected_group, expected_index):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input")
        group, index = token
        if group != expected_group or index != expected_index:
            word = self.get_word(token)
            expected_word = self.get_word((expected_group, expected_index))
            raise ParserError(f"Unexpected token {
                              word}, expected {expected_word}")
        self.current += 1
        return token

    def match(self, expected_group, expected_index):
        token = self.current_token()
        if token and token[0] == expected_group and token[1] == expected_index:
            self.current += 1
            return True
        return False

    def get_word(self, token):
        group, index = token
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

    def analyze(self):
        self.P()
        if self.current < len(self.tokens):
            remaining = self.get_word(self.tokens[self.current])
            raise ParserError(
                f"Extra tokens after parsing complete: {remaining}")

    # P → program D1 ; B
    def P(self):
        self.consume(1, self.get_service_word_index('program'))
        self.D1()
        self.consume(2, self.get_limiter_index(';'))
        self.B()

    # D1 → var D { , D }
    def D1(self):
        self.consume(1, self.get_service_word_index('var'))
        self.D()
        while self.match(2, self.get_limiter_index(',')):
            self.D()

    # D → I { , I } : [int | bool]
    def D(self):
        self.I()
        while self.match(2, self.get_limiter_index(',')):
            self.I()
        if self.match(1, self.get_service_word_index('%')):
            pass
        elif self.match(1, self.get_service_word_index('!')):
            pass
        elif self.match(1, self.get_service_word_index('$')):
            pass
        else:
            raise ParserError("Expected type '%' or '!' or '$'")

    # B → begin S { ; S } end
    def B(self):
        self.consume(1, self.get_service_word_index('begin'))
        self.S()
        while self.match(2, self.get_limiter_index(';')):
            self.S()
        self.consume(1, self.get_service_word_index('end'))

    # S → I := E | if E then S else S | while E do S | B | readln(I) | writeln(E)
    def S(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input")

        if token[0] == 3:  # Identifier
            self.I()
            self.consume(2, self.get_limiter_index(':='))
            self.E()
        elif token == (1, self.get_service_word_index('if')):
            self.consume(1, self.get_service_word_index('if'))
            self.E()
            self.consume(1, self.get_service_word_index('then'))
            self.S()
            if self.match(1, self.get_service_word_index('else')):
                self.S()
        elif token == (1, self.get_service_word_index('while')):
            self.consume(1, self.get_service_word_index('while'))
            self.E()
            self.consume(1, self.get_service_word_index('do'))
            self.S()
        elif token == (1, self.get_service_word_index('begin')):
            self.B()
        elif token == (1, self.get_service_word_index('readln')):
            self.consume(1, self.get_service_word_index('readln'))
            self.consume(2, self.get_limiter_index('('))
            self.I()
            while self.match(2, self.get_limiter_index(',')):
                self.I()
            self.consume(2, self.get_limiter_index(')'))
        elif token == (1, self.get_service_word_index('writeln')):
            self.consume(1, self.get_service_word_index('writeln'))
            self.consume(2, self.get_limiter_index('('))
            self.E()
            while self.match(2, self.get_limiter_index(',')):
                self.E()
            self.consume(2, self.get_limiter_index(')'))
        else:
            raise ParserError(f"Invalid statement starting with token '{
                              self.get_word(token)}'")

    # E → E1 { [= | > | < | >= | <= | !=] E1 }
    def E(self):
        self.E1()
        token = self.current_token()
        relation_ops = ['!=', '==', '<', '<=', '>', '>=']
        if token and token in [(1, self.get_service_word_index(op)) for op in relation_ops]:
            self.current += 1
            self.E1()

    # E1 → T { [ + | - | || ] T }
    def E1(self):
        self.T()
        while True:
            token = self.current_token()
            if token and token in [
                (2, self.get_limiter_index('+')),
                (2, self.get_limiter_index('-')),
                (1, self.get_service_word_index('||'))
            ]:
                self.current += 1
                self.T()
            else:
                break

    # T → F { [ * | / | && ] F }
    def T(self):
        self.F()
        while True:
            token = self.current_token()
            if token and token in [
                (2, self.get_limiter_index('*')),
                (2, self.get_limiter_index('/')),
                (1, self.get_service_word_index('&&'))
            ]:
                self.current += 1
                self.F()
            else:
                break

    # F → I | N | L | not F | ( E )
    def F(self):
        token = self.current_token()
        if token is None:
            raise ParserError("Unexpected end of input")

        if token[0] == 3:  # Identifier
            self.I()
        elif token[0] == 4:  # Number
            self.N()
        elif token == (1, self.get_service_word_index('true')) or token == (1, self.get_service_word_index('false')):
            self.L()
        elif token == (1, self.get_service_word_index('not')):
            self.consume(1, self.get_service_word_index('not'))
            self.F()
        elif token == (2, self.get_limiter_index('(')):
            self.consume(2, self.get_limiter_index('('))
            self.E()
            self.consume(2, self.get_limiter_index(')'))
        else:
            raise ParserError(f"Invalid factor starting with token '{
                              self.get_word(token)}'")

    # L → true | false
    def L(self):
        token = self.current_token()
        if token == (1, self.get_service_word_index('true')):
            self.consume(1, self.get_service_word_index('true'))
        elif token == (1, self.get_service_word_index('false')):
            self.consume(1, self.get_service_word_index('false'))
        else:
            raise ParserError("Expected 'true' or 'false'")

    # I → Identifier
    def I(self):
        token = self.current_token()
        if token and token[0] == 3:
            self.consume(3, token[1])
        else:
            raise ParserError("Expected identifier")

    # N → Number
    def N(self):
        token = self.current_token()
        if token and token[0] == 4:
            self.consume(4, token[1])
        else:
            raise ParserError("Expected number")

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
        print("Usage: python parser.py lecsems.txt")
        sys.exit(1)

    parser = Parser(sys.argv[1])
    try:
        parser.analyze()
        print("Parsing completed successfully.")
    except ParserError as e:
        print(f"Parsing error: {e}")


if __name__ == "__main__":
    main()
