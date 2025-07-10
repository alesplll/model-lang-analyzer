#!/bin/bash

# run_parser.sh
# Скрипт для запуска лексера и парсера последовательно.
# Использование: ./run_parser.sh <имя_файла_кода>

# Проверка, что передан ровно один аргумент
if [ "$#" -ne 1 ]; then
    echo "Использование: $0 <имя_файла_кода>"
    exit 1
fi

INPUT_FILE="$1"
TOKEN_FILE="lecsems2.txt"

# Проверка существования входного файла
if [ ! -f "$INPUT_FILE" ]; then
    echo "Ошибка: Файл '$INPUT_FILE' не найден."
    exit 1
fi

# Запуск лекcера
python lecser2.py "$INPUT_FILE"
LEXER_EXIT_CODE=$?

if [ $LEXER_EXIT_CODE -ne 0 ]; then
    exit $LEXER_EXIT_CODE
fi

# Проверка существования файла токенов
if [ ! -f "$TOKEN_FILE" ]; then
    echo "Ошибка: Файл токенов '$TOKEN_FILE' не найден."
    exit 1
fi

# Запуск парсера
python parser2.py "$TOKEN_FILE"
PARSER_EXIT_CODE=$?

if [ $PARSER_EXIT_CODE -ne 0 ]; then
    exit $PARSER_EXIT_CODE
fi
