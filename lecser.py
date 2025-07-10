import sys
import json


class Lexer:
    def __init__(self, filepath):
        self.filepath = filepath
        self.tokens = []
        self.state = 'S'
        self.word = ''
        self.letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"
        self.digits = "0123456789"
        self.service_words = ['while', 'readln', 'for', 'to', 'step', 'next',
                              '%', '!', '$', 'writeln', 'if', 'else', 'true', 'false', 'begin', 'end']
        self.limiters = ['{', '}', ';', '[', ']', ':=', '==', '!=', '<', '<=', '>', '>=',
                         '+', '-', '*', '/', '/*', '*/', '(', ')', ',', '||', '&&']
        self.identifiers = []
        self.numbers = []
        self.outputs = []

    def tokenize(self):
        with open(self.filepath, 'r') as file:
            content = file.read()

        i = 0
        length = len(content)
        while i < length:
            char = content[i]
            symbol = char
            match self.state:
                case 'S':
                    if symbol in [' ', '\t', '\n']:
                        i += 1
                        continue
                    elif symbol == '/':
                        if i + 1 < length and content[i + 1] == '*':
                            self.state = 'COMMENT'
                            i += 2
                            continue
                        else:
                            self.word += symbol
                            self.state = 'LIM'
                    elif symbol in self.letters:
                        self.word += symbol
                        self.state = 'ID'
                    elif symbol in self.digits or symbol == '.':
                        self.word += symbol
                        self.state = 'NM'
                    else:
                        self.word += symbol
                        self.state = 'LIM'
                    i += 1

                case 'COMMENT':
                    if symbol == '*' and i + 1 < length and content[i + 1] == '/':
                        self.state = 'S'
                        i += 2
                    else:
                        i += 1

                case 'ID':
                    if symbol in self.letters or symbol in self.digits:
                        self.word += symbol
                        i += 1
                    else:
                        if self.word in self.service_words:
                            group = 1
                            index = self.service_words.index(self.word) + 1
                        else:
                            group = 3
                            index = self.add_identifier(self.word)
                        self.outputs.append((group, index))
                        self.word = ''
                        self.state = 'S'
                case 'NM':
                    if symbol in self.digits or symbol == '.':
                        self.word += symbol
                        i += 1
                    else:
                        index = self.add_number(self.word)
                        self.outputs.append((4, index))
                        self.word = ''
                        self.state = 'S'
                case 'LIM':
                    if self.word in self.limiters:
                        group = 2
                        index = self.limiters.index(self.word) + 1
                        self.outputs.append((group, index))
                    else:
                        # Unknown limiter, can handle error if needed
                        pass
                    self.word = ''
                    self.state = 'S'
                    i += 1

        # Handle any remaining word
        if self.word:
            if self.state == 'ID':
                if self.word in self.service_words:
                    group = 1
                    index = self.service_words.index(self.word) + 1
                else:
                    group = 3
                    index = self.add_identifier(self.word)
                self.outputs.append((group, index))
            elif self.state == 'NM':
                index = self.add_number(self.word)
                self.outputs.append((4, index))
            elif self.state == 'LIM':
                if self.word in self.limiters:
                    group = 2
                    index = self.limiters.index(self.word) + 1
                    self.outputs.append((group, index))
            self.word = ''

    def add_identifier(self, identifier):
        if identifier not in self.identifiers:
            self.identifiers.append(identifier)
        return self.identifiers.index(identifier) + 1

    def add_number(self, number):
        if number not in self.numbers:
            self.numbers.append(number)
        return self.numbers.index(number) + 1

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
            outfile.write("\nTokens:\n")
            # Save tokens
            for token in self.outputs:
                outfile.write(f"({token[0]}, {token[1]})\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python lecser.py <input_file>")
        sys.exit(1)
    lexer = Lexer(sys.argv[1])
    lexer.tokenize()
    lexer.save_tokens("lecsems.txt")
