# lecser2.py
import sys


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tokens = []
        self.state = 'S'
        self.word = ''
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
        self.digits = "0123456789"
        self.service_words = ['while', 'readln', 'for', 'to', 'step', 'next',
                              '%', '!', '$', 'writeln', 'if', 'else', 'true', 'false', 'begin', 'end', 'not']
        self.limiters = ['{', '}', ';', '[', ']', ':=', '==', '!=', '<', '<=', '>', '>=',
                         '+', '-', '*', '/', '/*', '*/', '(', ')', ',', '||', '&&']
        self.identifiers = []
        self.numbers = []
        self.outputs = []
        self.backtrack = False
        self.last_char_was_star = False

    def tokenize(self):
        with open(self.filepath, 'r') as file:
            line_num = 1
            while True:
                line = file.readline()
                if not line:
                    break
                i = 0
                line_length = len(line)
                while i < line_length:
                    char = line[i]
                    proceed = self.process_char(char, line_num, i + 1)
                    if self.backtrack:
                        self.backtrack = False
                        # Do not increment 'i', reprocess this character
                    else:
                        i += 1
                line_num += 1
        # Handle any remaining word
        if self.word:
            self.finalize_token(line_num, 1)  # Assume column 1 at end

    def process_char(self, char, line_num, col_num):
        match self.state:
            case 'S':
                if char in [' ', '\t', '\n']:
                    pass  # Ignore whitespace
                elif char in self.service_words and len(char) == 1:
                    # Directly add as service word
                    group = 1
                    index = self.get_service_word_index(char)
                    self.add_token(group, index, line_num, col_num, char)
                elif char.isalpha() or char == '_':
                    self.word += char
                    self.state = 'ID'
                    self.token_start = (line_num, col_num)
                elif char.isdigit() or char == '.':
                    self.word += char
                    self.state = 'NM'
                    self.token_start = (line_num, col_num)
                elif char == '/':
                    self.word += char
                    self.state = 'DIV_OR_COMMENT'
                else:
                    self.word += char
                    self.state = 'LIM'
                    self.token_start = (line_num, col_num)
            case 'ID':
                if char.isalnum() or char == '_':
                    self.word += char
                else:
                    self.reprocess_char(char, line_num, col_num)
            case 'NM':
                if char.isdigit() or char == '.':
                    self.word += char
                else:
                    self.reprocess_char(char, line_num, col_num)
            case 'LIM':
                potential_two_char = self.word + char
                if potential_two_char in self.limiters:
                    self.word = potential_two_char
                    self.state = 'LIM2'
                    self.token_start = (line_num, col_num - 1)
                else:
                    self.reprocess_char(char, line_num, col_num)
            case 'LIM2':
                self.finalize_token(line_num, col_num)
            case 'COMMENT':
                if self.last_char_was_star and char == '/':
                    self.state = 'S'
                    self.word = ''
                    self.last_char_was_star = False
                elif char == '*':
                    self.last_char_was_star = True
                else:
                    self.last_char_was_star = False
                    # Stay in COMMENT
            case 'DIV_OR_COMMENT':
                if char == '*':
                    self.state = 'COMMENT'
                    self.last_char_was_star = False
                    self.word = ''
                else:
                    self.add_token(2, self.get_limiter_index(
                        '/'), line_num, self.token_start[1], '/')
                    self.reprocess_char(char, line_num, col_num)
        return True

    def reprocess_char(self, char, line_num, col_num):
        # Push back the character for next token processing
        self.finalize_token(line_num, col_num - 1)
        self.backtrack = True

    def finalize_limiter(self, line_num, col_num):
        limiter = self.word
        if limiter in self.service_words:
            group = 1  # Service words group
            index = self.get_service_word_index(limiter)
            self.add_token(group, index, line_num, col_num, limiter)
        elif limiter in self.limiters:
            group = 2  # Limiters group
            index = self.get_limiter_index(limiter)
            self.add_token(group, index, line_num, col_num, limiter)
        else:
            raise LexerError(f"Unknown limiter '{limiter}' at line {
                             line_num}, column {col_num}")
        self.word = ''
        self.state = 'S'

    def finalize_token(self, line_num, col_num):
        if self.state == 'ID':
            if self.word in self.service_words:
                group = 1  # Service words group
                index = self.get_service_word_index(self.word)
                self.add_token(
                    group, index, self.token_start[0], self.token_start[1], self.word)
            else:
                group = 3  # Identifiers group
                index = self.add_identifier(self.word)
                self.add_token(
                    group, index, self.token_start[0], self.token_start[1], self.word)
        elif self.state == 'NM':
            if self.is_number(self.word):
                group = 4  # Numbers group
                index = self.add_number(self.word)
                self.add_token(
                    group, index, self.token_start[0], self.token_start[1], self.word)
            else:
                raise LexerError(f"Invalid number '{self.word}' at line {
                                 line_num}, column {self.token_start[1]}")
        elif self.state in ['LIM', 'LIM2']:
            self.finalize_limiter(line_num, col_num - 1)
        self.word = ''
        self.state = 'S'

    def add_token(self, group, index, line_num, col_num, word):
        self.tokens.append((group, index, line_num, col_num, word))

    def add_identifier(self, identifier):
        if identifier not in self.identifiers:
            self.identifiers.append(identifier)
        return self.identifiers.index(identifier) + 1

    def add_number(self, number):
        if number not in self.numbers:
            self.numbers.append(number)
        return self.numbers.index(number) + 1

    def is_number(self, word):
        try:
            float(word)
            return True
        except ValueError:
            return False

    def get_service_word_index(self, word):
        if word in self.service_words:
            return self.service_words.index(word) + 1
        raise ValueError(f"Unknown service word: {word}")

    def get_limiter_index(self, limiter):
        if limiter in self.limiters:
            return self.limiters.index(limiter) + 1
        raise ValueError(f"Unknown limiter: {limiter}")

    def save_tokens(self, output_path):
        with open(output_path, 'w') as outfile:
            # Save identifiers
            outfile.write("Identifiers:\n")
            for identifier in self.identifiers:
                outfile.write(f"{identifier}\n")
            outfile.write("\nNumbers:\n")
            # Save numbers
            for number in self.numbers:
                outfile.write(f"{number}\n")
            outfile.write("\nTokens with Words and Positions:\n")
            # Save tokens as (group, index, line_num, col_num, word)
            for token in self.tokens:
                outfile.write(f"{token}\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: python lecser2.py <source_file>")
        sys.exit(1)

    source_file = sys.argv[1]
    output_token_file = "lecsems2.txt"
    lexer = Lexer(source_file)
    try:
        lexer.tokenize()
        lexer.save_tokens(output_token_file)
        print("___Tokenization completed successfully___")
    except LexerError as e:
        print(f"Lexer error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
