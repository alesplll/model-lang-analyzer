class Parser
{
    Lex curr_lex;    // текущая лексема
    lex_type c_type; // её тип
    int c_val;       // её значение
    Lexer lexer;
    int stack[100]; // стек переменных для контроля
    повторного объявления int top = 0;
    // Рекурсивные функции
    void P();
    void D1();
    void D();
    void B();
    void S();
    void E();
    void E1();
    void T();
    void F();
    // Получить очередную лексему
    void gl()
    {
        curr_lex = lexer.getLex();
        c_type = curr_lex.getType();
        c_val = curr_lex.getValue();
    }
    void reset()
    {
        top = 0;
    }
    void push(int i)
    {
        stack[top] = i;
        ++top;
        19 Продолжение листинга Б .1
    }
    int pop()
    {
        --top;
        return stack[top];
    }
    void dec(lex_type type)
    {
        int i;
        while (top)
        {
            i = pop();
            if (TID[i].isDeclared())
            {
                throw "decalred twice";
            }
            TID[i].setDeclared();
            TID[i].setType(type);
        }
    }

public:
    // Провести синтаксический разбор
    void analyze()
    {
        gl();
        P();
    }
    // Конструктор
    Parser(const char *filename) : lexer(filename),
                                   top(0) {}
};
// P→program D1;B@
void Parser::P()
{
    if (c_type == LEX_PROGRAM)
    {
        gl();
    }
    else
    {
        throw curr_lex;
        20 Продолжение листинга Б .1
    }
    D1();
    if (c_type == LEX_SEMICOLON)
    {
        gl();
    }
    else
    {
        throw curr_lex;
    }
    B();
    if (c_type != LEX_FIN)
    {
        throw curr_lex;
    }
}
// D1→var D {,D}
void Parser::D1()
{
    if (c_type != LEX_VAR)
    {
        throw curr_lex;
    }
    gl();
    D();
    while (c_type == LEX_COMMA)
    {
        gl();
        D();
    }
}
// D→I {,I}:[int│bool]
void Parser::D()
{
    reset();
    if (c_type != LEX_ID)
    {
        throw curr_lex;
    }
    push(c_val);
    gl();
    while (c_type == LEX_COMMA)
    {
        gl();
        if (c_type != LEX_ID)
        {
            throw curr_lex;
        }
        else
        {
            21 Продолжение листинга Б .1 push(c_val);
            gl();
        }
    }
    if (c_type != LEX_COLON)
    {
        throw curr_lex;
    }
    gl();
    if (c_type == LEX_INT)
    {
        this->dec(LEX_INT);
        gl();
    }
    else if (c_type == LEX_BOOL)
    {
        this->dec(LEX_BOOL);
        gl();
    }
    else
    {
        throw curr_lex;
    }
}
// B→begin S {;S} end
void Parser::B()
{
    if (c_type != LEX_BEGIN)
    {
        throw curr_lex;
    }
    gl();
    S();
    while (c_type == LEX_SEMICOLON)
    {
        gl();
        S();
    }
    if (c_type == LEX_END)
    {
        gl();
    }
    else
    {
        throw curr_lex;
    }
}
22 Продолжение листинга Б .1
    // S→I::=E | if E then S else S | while E do S | B |
    read(I) |
    write(E) void Parser::S()
{
    if (c_type == LEX_IF)
    {
        gl();
        E();
        if (c_type == LEX_THEN)
        {
            gl();
            S();
            if (c_type == LEX_ELSE)
            {
                gl();
                S();
            }
        }
        else
        {
            throw curr_lex;
        }
    }
    else if (c_type == LEX_WHILE)
    {
        gl();
        E();
        if (c_type != LEX_DO)
        {
            throw curr_lex;
        }
        gl();
        S();
    }
    else if (c_type == LEX_READ)
    {
        gl();
        if (c_type != LEX_LPAREN)
        {
            throw curr_lex;
        }
        gl();
        if (c_type != LEX_ID)
        {
            throw curr_lex;
        }
        gl();
        if (c_type != LEX_RPAREN)
        {
            throw curr_lex;
        }
        gl();
    }
    23 Продолжение листинга Б .1 else if (c_type == LEX_WRITE)
    {
        gl();
        if (c_type != LEX_LPAREN)
        {
            throw curr_lex;
        }
        gl();
        E();
        if (c_type != LEX_RPAREN)
        {
            throw curr_lex;
        }
        gl();
    }
    else if (c_type == LEX_ID)
    {
        gl();
        if (c_type != LEX_ASSIGN)
        {
            throw curr_lex;
        }
        gl();
        E();
    }
    else
    {
        B();
    }
}
// E→E1{[=|>|<|>=|<=|!=]E1}
void Parser::E()
{
    E1();
    if (c_type == LEX_EQ ||
        c_type == LEX_LSS ||
        c_type == LEX_GTR ||
        c_type == LEX_LEQ ||
        c_type == LEX_GEQ ||
        c_type == LEX_NEQ)
    {
        gl();
        E1();
    }
}
// E1→T{[ + | - | or ] T}
void Parser::E1() 24 Продолжение листинга Б .1
{
    T();
    while (c_type == LEX_PLUS || c_type == LEX_MINUS ||
           c_type == LEX_OR)
    {
        gl();
        T();
    }
}
// T→F{[ * | / | and ] F}
void Parser::T()
{
    F();
    while (c_type == LEX_TIMES || c_type == LEX_SLASH ||
           c_type == LEX_AND)
    {
        gl();
        F();
    }
}
// F→I | N | L | not F | (E)
void Parser::F()
{
    if (c_type == LEX_ID)
    {
        gl();
    }
    else if (c_type == LEX_NUM)
    {
        gl();
    }
    else if (c_type == LEX_TRUE || c_type == LEX_FALSE)
    {
        gl();
    }
    else if (c_type == LEX_NOT)
    {
        gl();
        F();
    }
    else if (c_type == LEX_LPAREN)
    {
        gl();
        E();
        if (c_type != LEX_RPAREN)
        {
            throw curr_lex;
        }
        gl();
        25 Окончание листинга Б .1
    }
    else
    {
        throw curr_lex;
    }
}