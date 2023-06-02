
import sys
import ply.lex as lex
import ply.yacc as yacc
GREEN = '\033[92m'
CLEAR_FORMAT = '\033[0m'

import decaf_lexer
import decaf_parser
import decaf_ast
from decaf_codegen import codeGenManager
from decaf_codegen import setfile
def just_scan(fn=""):
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    lexer = lex.lex(module = decaf_lexer)

    fh = open(fn, 'r')
    source = fh.read()
    fh.close()
    lexer.input(source)
    next_token = lexer.token()
    while next_token != None:
        next_token = lexer.token()
# end def just_scan()


def just_parse(fn=""):
    if fn == "":
        print("Missing file name for source program.")
        print("USAGE: python3 decaf_checker.py <decaf_source_file_name>")
        sys.exit()
    lexer = lex.lex(module = decaf_lexer)
    parser = yacc.yacc(module = decaf_parser)

    fh = open(fn, 'r')
    source = fh.read()
    fh.close()
    try:
        result = parser.parse(source, lexer = lexer)
        decaf_ast.writeAST(result)
        setfile(sys.argv[1])
        codeGenManager(result, None)
    except SyntaxError:
        sys.exit(1)
    except TypeError:
        sys.exit(1)
    else:
        # Parsing Successful
        #print()
        print(GREEN+ "YES" + CLEAR_FORMAT)
        #print()

def main():
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    just_scan(fn) # lexer
    fn = sys.argv[1] if len(sys.argv) > 1 else ""
    just_parse(fn) # parser

def compile(fn=""):
    just_scan(fn) # lexer
    just_parse(fn) # parser

if __name__ == "__main__":
  main()