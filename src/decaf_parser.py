
import ply.yacc as yacc
import sys
from decaf_lexer import tokens
from decaf_ast import *
precedence = (
    ('right', 'SETEQUAL'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'NOTEQUAL', 'EQUAL'),
    ('nonassoc', 'LESS', 'GREATEREQ', 'LESSEQ', 'GREATER'),
    ('left', 'PLUS', 'MINUS'),  
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'NOT'),
)

def p_start(p):
    '''start : start_statement
             | empty'''
    p[0] = Classes(p[1], p.lineno(1))

def p_start_statement(p):
    '''start_statement : class_decl
                       | class_decl start_statement'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_class(p):
    '''class_decl : CLASS ID LCURLY class_body RCURLY
                  | CLASS ID EXTENDS ID LCURLY class_body RCURLY'''

    if p[3] == '{':
        p[0] = Class(p[2], None, p[4], p.lineno(1))
    else:
        p[0] = Class(p[2], p[4] ,p[6], p.lineno(1))


def p_class_body(p):
    '''class_body : field_decl
                  | constructor_decl
                  | method_decl
                  | class_body field_decl
                  | class_body constructor_decl
                  | class_body method_decl'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]] 
def p_field_decl(p):
    '''field_decl : var_decl
                  | modifier var_decl'''
    if len(p) > 2:
      p[0] = FieldDecl(p[1], p[2], p.lineno(1))
    else:
      p[0] = FieldDecl(None, p[1], p.lineno(1))

def p_modifier(p):
    '''modifier : PUBLIC
                | PRIVATE
                | STATIC
                | PUBLIC STATIC
                | PRIVATE STATIC
                | empty'''
    if len(p) > 2:
      p[0] = [p[1], p[2]]
    else:
      p[0] = [p[1]]

def p_var_decl(p):
    '''var_decl : type variables SEMICOLON'''
    p[0] = Variables(p[1], p[2], p.lineno(1))

#put new types here
def p_type(p):
    '''type : INT
            | FLOAT
            | BOOLEAN
            | STRING
            | ID'''
    p[0] = Type(p[1], p.lineno(1))

def p_variables(p):
    '''variables : variable
                 | variables COMMA variable'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]] 

def p_variable(p):
    '''variable : ID'''
    p[0] = Var(p[1], p.lineno(1))

def p_method_decl(p):
    '''method_decl : modifier type ID LPAREN RPAREN block
                   | modifier type ID LPAREN formals RPAREN block
                   | modifier VOID ID LPAREN RPAREN block
                   | modifier VOID ID LPAREN formals RPAREN block
                   | type ID LPAREN RPAREN block
                   | type ID LPAREN formals RPAREN block
                   | VOID ID LPAREN RPAREN block
                   | VOID ID LPAREN formals RPAREN block'''
    if len(p) == 7:
      if (p[3] == '('):
         p[0] = Method([], p[1], p[2],  p[4], p[6], p.lineno(1))
      else:
        p[0] = Method(p[1], p[2],  p[3],  None,  p[6], p.lineno(1))
    elif len(p) == 8:
        p[0] = Method(p[1], p[2],  p[3],  p[5],  p[7], p.lineno(1))
    else:
        p[0] = Method([], p[1], p[2],  None,  p[5], p.lineno(1))

def p_constructor(p):
    '''constructor_decl : modifier ID LPAREN RPAREN block 
                        | modifier ID LPAREN formals RPAREN block
                        | ID LPAREN RPAREN block 
                        | ID LPAREN formals RPAREN block'''
    if len(p) == 7:
      p[0] = Constructor( p[1], p[2], p[4], p[6], p.lineno(1))
    elif len(p) == 5:
      p[0] = Constructor([], p[1], None, p[4], p.lineno(1))
    else:
      if p[2] == '(':
        p[0] = Constructor([], p[1], p[3], p[5], p.lineno(1))
      else:
        p[0] = Constructor(p[1], p[2],None, p[5], p.lineno(1))

def p_formals(p):
    '''formals : formal_param
               | formal_param COMMA formals '''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]



def p_formals_param(p):
    '''formal_param : type variable'''
    p[0] = ArgVar(p[1], p[2], p.lineno(1))

def p_block(p):
    '''block : LCURLY stmtlist RCURLY
             | empty'''
    if len(p) > 2:
      p[0] = Block(p[2], p.lineno(1))
    else:
      p[0] = Block([], p.lineno(1))

def p_stmtlist(p):
    '''stmtlist : stmt
                | stmtlist stmt'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]



def p_stmt(p):
    '''stmt : IF LPAREN expression RPAREN stmt
            | IF LPAREN expression RPAREN stmt ELSE stmt
            | WHILE LPAREN expression RPAREN stmt
            | FOR LPAREN stmt_expression SEMICOLON expression SEMICOLON stmt_expression RPAREN stmt
            | FOR LPAREN stmt_expression SEMICOLON expression SEMICOLON RPAREN stmt
            | FOR LPAREN stmt_expression SEMICOLON SEMICOLON stmt_expression RPAREN stmt
            | FOR LPAREN SEMICOLON expression SEMICOLON stmt_expression RPAREN stmt
            | FOR LPAREN stmt_expression SEMICOLON SEMICOLON RPAREN stmt
            | FOR LPAREN SEMICOLON SEMICOLON stmt_expression RPAREN stmt
            | FOR LPAREN SEMICOLON expression SEMICOLON RPAREN stmt
            | FOR LPAREN SEMICOLON SEMICOLON RPAREN stmt
            | RETURN expression SEMICOLON
            | RETURN SEMICOLON
            | stmt_expression SEMICOLON
            | BREAK SEMICOLON
            | CONTINUE SEMICOLON
            | block
            | var_decl
            | SEMICOLON'''
    if p[1] == 'if':
       if len(p) == 6:
          p[0] = If(p[3], p[5], None, p.lineno(1))
       else:
          p[0] = If(p[3], p[5], p[7], p.lineno(1))
    elif p[1] == 'while':
       p[0] = While(p[3], p[5], p.lineno(1))
    elif p[1] == 'return':
       if len(p) == 2:
          p[0]=Return(None, p.lineno(1))
       else:
          p[0] = Return(p[2], p.lineno(1))
    elif p[1] == 'for':
      if len(p) == 10 :
          p[0] = For(p[3], p[5], p[7], p[9], p.lineno(1))
      elif len(p) == 9:
          if p[7] == ';':
            p[0] = For(p[3], p[5], None, p[8], p.lineno(1))
          elif p[5] == ';':
            p[0] = For(p[3], None, p[6], p[8], p.lineno(1))
          elif p[3] == ';':
            p[0] = For(None, p[4], p[6], p[8], p.lineno(1))
      elif len(p) == 8 :
          if p[4] == ';' and p[5] == ';':
            p[0] = For(p[3], None, None, p[7], p.lineno(1))
          if p[3] == ';' and p[4] == ';':
            p[0] = For(None, None, p[5], p[7], p.lineno(1))
          else:
            p[0] = For(None, p[4], None, p[7], p.lineno(1))
      else:
          For(None, None, None, p[5], p.lineno(1))
      
    elif p[1] == 'continue' or p[1] == 'break' or p[1] == ';':  
        p[0] = StmtWord(p[1])
    elif p[1] == ';':
       pass
    else:
       p[0] = p[1]
          
       
    
def p_literal(p):
    '''literal : Integer
               | Float
               | String
               | Null
               | False
               | True'''
    p[0] = Literal(p[1], p.lineno(1))

def p_int(p):
    '''Integer : INTEGER'''
    p[0] = ["Integer", p[1]]

def p_float(p):
    '''Float : FLOAT'''
    p[0] = ["Float", p[1]]

def p_string(p):
    '''String : STRING_LITERAL'''
    p[0] = ["String", p[1]]

def p_null(p):
    '''Null : NULL'''
    p[0] = ["Null", p[1]]

def p_false(p):
    '''False : FALSE'''
    p[0] = ["Boolean", p[1]]

def p_true(p):
    '''True : TRUE'''
    p[0] = ["Boolean", p[1]]
    
def p_primary(p):
    '''primary : literal
               | THIS
               | SUPER
               | LPAREN expression RPAREN
               | newObj
               | method_invocation
               | lhs'''
    if p[1]== 'this' or p[1] == 'super':
       p[0] = Primary(p[1], None, p.lineno(1))
    elif p[1] == '(':
       p[0] = Primary('expression', p[2], p.lineno(1))
    else:
        if (isinstance(p[1] , Lhs)):
          p[0] = Primary('single', p[1], p.lineno(1))
        elif (isinstance(p[1] , New)):
            p[0] = Primary('single', p[1], p.lineno(1))
        else:
           p[0] = p[1]
def p_new(p):
    '''newObj : NEW ID LPAREN RPAREN
               | NEW ID LPAREN arguments RPAREN'''
    if len(p) == 5:
      p[0] = New(p[2], [], p.lineno(1))
    else:
      p[0] = New(p[2], p[4], p.lineno(1))


def p_arg(p):
    '''arguments : expression
                 | expression COMMA arguments'''
    if len(p) == 2:
      p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]



def p_lhs(p):
    '''lhs : field_access'''
    p[0] = Lhs(p[1], p.lineno(1))

def p_field(p):
    '''field_access : primary DOT ID
                    | ID'''
    if len(p) == 2:
      p[0] =  Field(None, p[1], p.lineno(1))
    else:
      p[0] =  Field(p[1], p[3], p.lineno(2))

def p_method_invo(p):
    '''method_invocation : field_access LPAREN arguments RPAREN
                         | field_access LPAREN RPAREN'''
    if len(p) == 5:
      p[0] = MethInvo(p[1],p[3], p.lineno(1))
    else:
      p[0] =MethInvo(p[1], [], p.lineno(1))

def p_expr(p):
    '''expression : primary
                  | assign
                  | expression arith_op expression
                  | expression bool_op expression
                  | unary_op expression'''
    if len(p) == 2:
      p[0] = p[1]
    elif len(p) == 4:
       p[0] = BinOpExp(p[1], p[2], p[3], p.lineno(2))
    else:
       p[0] = UniOpExp(p[1], p[2], p.lineno(1))

def p_op(p):
    '''operation  : expression arith_op expression
                  | expression bool_op expression '''
    p[0] = BinOpExp(p[1], p[2], p[3],  p.lineno(1))


def p_assign(p):
    '''assign : lhs SETEQUAL expression
              | lhs PLUSPLUS
              | lhs MINUSMINUS
              | PLUSPLUS lhs
              | MINUSMINUS lhs'''
    if len(p) == 4:
      p[0] = Assign(p[1], p[3],  p.lineno(2))
    else:
      if p[1] == '++':
        p[0] = Assign(p[2], 'prefix++', p.lineno(2))
      elif p[1] == '--':
        p[0] = Assign(p[2], 'prefix--',p.lineno(2))
      elif p[2] == '++':
        p[0] = Assign(p[1], 'postfix++', p.lineno(1))
      elif p[2] == '--':
        p[0] = Assign(p[1], 'postfix--', p.lineno(1))

def p_arith_op(p):
    '''arith_op : PLUS
                | MINUS
                | TIMES 
                | DIVIDE'''
    p[0] = p[1]

def p_bool_op(p):
    '''bool_op : GREATER
               | LESS
               | GREATEREQ
               | LESSEQ
               | EQUAL
               | NOTEQUAL
               | AND
               | OR'''
    p[0] = p[1]

def p_unary_op(p):
    '''unary_op : PLUS
                | MINUS
                | NOT'''
    p[0] = p[1]

def p_stmt_expr(p):
    '''stmt_expression : assign
                       | method_invocation'''
    p[0] = p[1]

def p_empty(p):
    'empty :'
    p[0] = []
    pass

RED = '\033[91m'
CLEAR_FORMAT = '\033[0m'

def p_error(p):
    if p:
        print(f"{RED}ERROR: Syntax error at line {p.lineno}, column {find_column(p)}, token: {p.value}'{CLEAR_FORMAT}", file=sys.stderr)
    else:
        print(f"{RED}ERROR: Syntax error: unexpected end of input{CLEAR_FORMAT}",file=sys.stderr)
    raise SyntaxError();     

def find_column(token):
    input_str = token.lexer.lexdata
    last = input_str.rfind('\n', 0, token.lexpos)
    column = (token.lexpos - last)
    return column
