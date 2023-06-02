
GREEN = '\033[92m'
RED = '\033[91m'
CLEAR_FORMAT = '\033[0m'

output = []


fieldNum = 1
constructorNum = 1
methodNum = 1
fieldOutput = []
constructerOutput = []
methOuput = []
blockOut = []
variables = []
inherit = {}
# storing block record variable
# count variable id
varcount = 1
# flag for method call node
methodcall = 0
classMethod = {}
# store class table
record = {}
recordOfUsedVar = set()
predefinedClass = {'In': {"scan_int", "scan_Float"}, 'Out': {"print"}}
primarytype = {'boolean', 'int', 'float', 'string'}
#formatted as classname -> methodname/constrcutor -> typing of the args since there no overloading and modifiers and return type as format (return type, argstype, modifier)
recordType = {}
recordFieldtype = {}
literalClass = False
thisFlag = False
superFlag = False

typeOutput = set ()
def subtypeCheck(left, right):
    while (inherit[right] != None):
        if inherit[right] == left:
            return True
    while (inherit[left] != None):
        if inherit[left] == right:
            return True
    return False
class Node(object):
    """Base class of AST nodes."""

    # For each class of nodes, store names of the fields for children nodes.
    fields = []
    scope = {}
    parentPointer = None
    def __init__(self, *args):
        """Populate fields named in "fields" with values in *args."""
        assert (len(self.fields) == len(args))
        for f, a in zip(self.fields, args):
            setattr(self, f, a)

    def anlz_procs(self, record, className, methodName, parent):
        """Collect procedure definitions, called on statements."""
        raise Exception("Not implemented.")
    #recursive travese up the tree check for nearest delcared variable
    def scopeChecker(self, variableName):
        if variableName in self.scope:
            global output
            return self.scope[variableName]
        if self.parentPointer == None:
            return -1
        return self.parentPointer.scopeChecker(variableName)
    
    def lineCheck(self):
        if self.linenum != 0:
            return self.linenum
        elif self.parentPointer == None:
            return 0
        else:
            return self.lineCheck(self.parentPointer)
    
    # second check
    def anlz(self, className ):
        pass
    '''for typeChecking expression such as constant, assign would return the typing, while other 
    such as if and while will return true or false, an block statement will return true when all stmt inside is true
    everything will be type correct if classes node typeChecking return true'''
    
    '''scan and store method'''
    def methodScanner(self,  className):
        pass


    def typeChecking(self, className, methodName, parent):
        pass
    

# subclasses of Node for expressions\
class Constructor(Node):
    fields = ['modifiers', 'name', 'params', 'body', 'linenum']
    def anlz_procs(self, record, className, methodName, parent):
        #traverse and append print out
        #call global variable
        self.parentPointer = parent
        self.scope = {}
        global blockOut, constructorNum, variables, varcount, output
        if self.modifiers == None:
            self.modifiers = ['private']
        elif len(self.modifiers) == 0:
            self.modifiers = ['private']
        constructerOutput.append("CONSTRUCTOR: {}, {}".format(constructorNum, " ".join(self.modifiers)))
        methodName = "constructor" + str(constructorNum)
        constructorNum += 1
        # set the dictionary for constructor/method
        record[className][methodName] = {}
        if self.params != None: 
            for i in self.params:
                #i.anlz_proc should be returning tuple (type, name) from argvar object
                parm = i.anlz_procs(record, className, methodName, self)
                #store in dictionary and store it as (type, id)
                record[className][methodName][str(varcount)] = (parm[0], "formal", parm[1])
                varcount += 1
        #ids = [id[1] for id in parm]
        constructerOutput.append("Constructor Parameters: {}".format(", ".join([k for k in record[className][methodName].keys()])))
        self.body.anlz_procs(record, className, methodName, self)
        constructerOutput.append("Variable Table:")
        for k, v in record[className][methodName].items():
            methOuput.append("VARIABLE: {}, {}, {}, {}".format(k, v[2], v[1], v[0]))
        constructerOutput.append("Constructor Body:")
        constructerOutput.append("".join(blockOut))
        #reset block variables
        varcount = 1
        blockOut = []
    def anlz(self, className ):
        self.body.anlz(className)

    def methodScanner(self,  className):
        #record type of params
        recordType[className][self.name] = (None, [], self.modifiers)
        if self.params != None:
            for p in self.params:
                recordType[className][className][1].append(p.typeChecking(className, self.name, self))


    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = {}
        if self.params != None: 
            for p in self.params:
                p.typeChecking(className, self.name, self)
        self.body.typeChecking(className, self.name, self)
    

class Primary(Node):
    fields = ['type', 'others', 'linenum']
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if self.type == 'single':
            return self.others.anlz_procs(record, className, methodName, self)
        elif self.type == 'expression':
            return self.others.anlz_procs(record, className, methodName, self)
        else:
             #other is this or super string
            return self.type
    def anlz(self, className ):
        if self.type == 'single':
            return self.others.anlz(className)
        elif self.type == 'expression':
                return self.others.anlz(className)
        else:
             #other is this or super string
            return self.type
    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        global thisFlag, superFlag
        if self.type == 'single':
            return self.others.typeChecking(className, methodName, self)
        elif self.type == 'expression':
            return self.others.typeChecking(className, methodName, self)
        else:
            if self.type == 'this':
                thisFlag = True
                return className
            else:
                if inherit[className] != None:
                    superFlag = True
                    return inherit[className]
                
                print("Class does not have super class")
                raise TypeError
            
class New(Node):
    fields = ['type', 'arguments', 'linenum']
    def __init__(self, *args):
        super().__init__(*args)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if self.arguments != None:
            for arg in self.arguments:
                arg.anlz_procs(record, className, methodName, self)
            blockOut.append(f"New-object({self.type}, {self.arguments})")
        
    def anlz(self, className ):
        if self.arguments != None:
            for arg in self.arguments:
                arg.anlz(className)

    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        args = []
        for arg in self.arguments:
            args.append(arg.typeChecking(className, methodName, self))
        if self.type in recordType:
            if self.type in recordType[self.type]:
                if "private" in recordType[self.type][self.type][1]:
                    print(f"Unaccessible contructor at line {self.linenum}")
                    raise TypeError
                if len(self.arguments) != len(recordType[self.type][self.type][1]):
                    print("argument amount does not match with constructor")
                    raise SyntaxError
                for i in range(len(args)):
                    if args[i] != recordType[self.type][self.type][1][i]:
                        print(F"wrong typing in argument in line {self.linenum}")
                        raise TypeError
                return self.type
            print("undefined constructor")
            raise SyntaxError


class FieldDecl(Node):
    fields = ['modifier', 'variables', 'linenum']

    def __init__(self, *args):
        super().__init__(*args)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        var = self.variables.anlz_procs(record, className, methodName, self)
        record[className]['fieldVar'].add(var)
        global variables, output
        stat = "instance"
        if self.modifier == None:
            self.modifier = ['private']
        elif len(self.modifier) == 0:
            self.modifier = ['private']
        elif self.modifier[0] == 'static':
            self.modifier = ['private', 'static']
            stat = "static"
        elif len(self.modifier) == 2:
            if self.modifier[1] =='static':
                stat = "static"
        global fieldNum
        recordFieldtype[className].append((var[2], var[1], self.modifier))
        fieldOutput.append("FIELD {}, {}, {}, {}, {}, {}".format(fieldNum, var[1], className, self.modifier[0], stat, var[0]))
        fieldNum += 1

        variables = []

    def typeChecking(self, className, methodName, parent):
        pass
    


class Classes(Node):
    """Class of nodes representing body of classes declaration"""
    fields = ['classes', 'linenum']


    def anlz_procs(self, record, className, methodName, parent):
        for c in self.classes:
            c.anlz_procs(record, className, methodName, self)
    def anlz(self, className ):
        for c in self.classes:
            c.anlz(className)
    def methodScanner(self,  className):
        for c in self.classes:
            c.methodScanner(className)
    def typeChecking(self, className, methodName, parent):
        for c in self.classes:
            c.typeChecking(className, methodName, self)


class Class(Node):
    """Class of nodes representingof classes declaration"""
    fields = ['name', 'superclass', 'body', 'linenum']


    def anlz_procs(self, record, className, methodName, parent):
        if self.name in record:
            print(f"{RED}ERROR:{CLEAR_FORMAT} Duplicate classname detected: repeated {self.name} at line {self.linenum}")
            raise SyntaxError
        #create class record should be disctionary in dicitionary type structure eg classname -> methods/constructor -> localrecord 
        # name would be defined (method/constructor note not that name it just method/constructor)+unique id ties to it  eg constructor1, method1
        record[self.name]= {}
        recordFieldtype[self.name] = []
        classMethod[self.name] = set()
        record[self.name]['fieldVar'] = set()
        global fieldOutput, constructerOutput, methOuput, output
        output .append( f"Class Name: {self.name}")
        output.append(f"Superclass Name: {self.superclass if self.superclass!=None else ''}")
        
        inherit[self.name] = self.superclass
        record[self.name]['superclass'] = self.superclass
        for b in self.body:
            b.anlz_procs(record, self.name, methodName, self)
        
        # output
        output.append("Fields:")
        if len(fieldOutput) != 0:
            output.append("\n".join(fieldOutput))

        fieldOutput = []

        # output
        output.append("Constructors:")
        if len(constructerOutput) != 0:
            output.append( "\n".join(constructerOutput))
        constructerOutput = []
        output.append("Methods:")
        if len(methOuput) != 0:
            output.append("\n".join(methOuput))
        methOuput = []

    def anlz(self, className ):
        for b in self.body:
            b.anlz(self.name)

    def methodScanner(self, className):
        recordType[self.name] = {}
        for b in self.body:
            b. methodScanner(self.name)

    def typeChecking(self, className, methodName, parent):
        self.scope = {}
        for stmt in self.body:
            if stmt.typeChecking(self.name, methodName, parent) == False:
                print(f"incorrect typing occured in {self.name}")
                raise TypeError
        


class Type(Node):
    """Class of nodes representing type"""
    fields = ['name', 'linenum']


    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if self.name in ('int', 'float', 'boolean', 'string'):
            return self.name
        return "user({})".format(self.name)

    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        return self.name


## note to self gotta fix global variables parameter for an global record
class Variables(Node):
    """Class of nodes representing of variables"""
    fields = ['type', 'variables', 'linenum']

    def __init__(self, type, variables, linenum):
        super().__init__(type, variables, linenum)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        global varcount, output
        type = self.type.anlz_procs(record, className, methodName, self)
        for var in self.variables:
            # should return (type, varName)
            vars = (type, var.anlz_procs(record, className, methodName, self), self.type.typeChecking(className, methodName, parent) )
            if methodName == None:
                return vars
            if methodName != None:
                #format to key as id value as (type, local/formal, name)
                record[className][methodName][str(varcount)] = (vars[0], "local", vars[1])
                varcount += 1


    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        type = self.type.typeChecking(className, methodName, self)
        #store the var with the type assoicated with in this scope
        if not type in primarytype and not type in classMethod:
            print(f"undefined type at line {self.linenum}")
            raise TypeError
        for var in self.variables:
            name = var.typeChecking(className, methodName, self)
            self.scope[name] = type
        return type
            

class ArgVar(Node):
    fields = ['type', 'name', 'linenum']

    def __init__(self, type, name, linenum):
        super().__init__(type, name, linenum)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        # check if var is already declared in the local scope
        # copied from var class
        if self.name in self.scope:
            print(f"{RED}ERROR:{CLEAR_FORMAT} Variable {self.name} already declared in the local scope at line {self.linenum}")
            raise SyntaxError
        type = self.type.anlz_procs(record, className, methodName, self)
        return (type, self.name.anlz_procs(record, className, methodName, self))
    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        type = self.type.typeChecking(className, methodName, self)
        name = self.name.typeChecking(className, methodName, self)
        self.scope[name] = type
        return type


class Var(Node):
    """Class of nodes representing of variables"""
    fields = ['name', 'linenum']

    def __init__(self, name, linenum):
        super().__init__(name, linenum)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope

        if self.name in self.scope:
            print(f"{RED}ERROR: {CLEAR_FORMAT}Variable {self.name} already declared in the local scope at line {self.linenum}")
            raise SyntaxError
        self.scope[self.name] = str(varcount)
        return self.name
    
    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        return self.name



class Literal(Node):
    """Class of nodes representing integer literals."""
    fields = ['value', 'linenum']

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if self.value[0] == 'Null' or self.value[0] == 'True' or self.value[0] == 'False':
            blockOut.append(f"{self.value[0]}")
            return self.value[1]
        blockOut.append("Constant({}-constant({}))".format(self.value[0],self.value[1]))
        return self.value[1]
    
    
    def typeChecking(self, className, methodName, parent):
        if self.value[0] == 'Null':
            return 'null'
        if self.value[0] == 'True' or self.value[0] == 'False':
            return 'boolean'
        
        if self.value[0] == 'Integer':
            return 'int'
        if self.value[0] == 'String' or self.value[0] == 'string':
            return 'string'
        if self.value[0] == 'Float':
            return 'float'
        if self.value[0] == 'Boolean':
            return 'boolean'
        return self.value[0]

class BinOpExp(Node):
    """Class of nodes representing binary-operation expressions."""
    fields = ['left', 'op', 'right', 'linenum']

    def __init__(self, left, op, right, linenum):
        super().__init__(left, op, right, linenum)
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        blockOut.append("Binary(")
        if self.op == "+":
            blockOut.append("add, ")
        elif self.op == "-":
            blockOut.append("sub, ")
        elif self.op == "*":
            blockOut.append("mul, ")
        elif self.op == "/":
            blockOut.append("div, ")
        elif self.op == "&&":
            blockOut.append("and, ")
        elif self.op == "||":
            blockOut.append("or, ")
        elif self.op == "==":
            blockOut.append("eq, ")
        elif self.op == "!=":
            blockOut.append("neq, ")
        elif self.op == "<":
            blockOut.append("lt, ")
        elif self.op == "<=":
            blockOut.append("leq, ")
        elif self.op == ">":
            blockOut.append("gt, ")
        elif self.op == ">=":
            blockOut.append("geq, ")
        self.left.anlz_procs(record, className, methodName, self)
        blockOut.append(", ")
        self.right.anlz_procs(record, className, methodName, self)
        blockOut.append(")")
        pass
    def anlz(self, className):
        self.left.anlz(className)
        self.right.anlz(className)


    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        left = self.left.typeChecking(className, methodName, self)
        right = self.right.typeChecking(className, methodName, self)
        if self.op == "+":
            if (left == 'int' or left == 'float') and (right == 'int' or right == 'float'):
                if left == 'float' or right == 'float':
                    return 'float'
                return 'int'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at + line {self.linenum}")
            raise TypeError
        elif self.op == "-":
            if (left == 'int' or left == 'float') and (right == 'int' or right == 'float'):
                if left == 'float' or right == 'float':
                    return 'float'
                return 'int'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at - line {self.linenum}")
            raise TypeError
        elif self.op == "*":
            if (left == 'int' or left == 'float') and (right == 'int' or right == 'float'):
                if left == 'float' or right == 'float':
                    return 'float'
                return 'int'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at * line {self.linenum}")
            raise TypeError
        elif self.op == "/":
            if (left == 'int' or left == 'float') and (right == 'int' or right == 'float'):
                if left == 'float' or right == 'float':
                    return 'float'
                return 'int'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at / line {self.linenum}")
            raise TypeError
        elif self.op == "&&":
            if left == 'boolean' and right == 'boolean':
                return 'boolean'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at && line {self.linenum}")
            raise TypeError
        elif self.op == "||":
            if left == 'boolean' and right == 'boolean':
                return 'boolean'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at && line {self.linenum}")
            raise TypeError
        elif self.op == "==":
            if left in primarytype and right in primarytype:
                if left == right:
                    return 'boolean'
                print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at == ")
                raise TypeError
                
            if left in primarytype or right in primarytype:
                print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at == ")
                raise TypeError
            if right == 'null' or left == 'null':
                return 'boolean'
            if left != right:
                if subtypeCheck(left, right) == False:
                    print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at == ")
                    raise TypeError
            return 'boolean'
        elif self.op == "!=":
            if left != right:
                if left in primarytype or right in primarytype:
                    print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at ==")
                    raise TypeError
                if subtypeCheck(left, right) == False:
                    print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at != line {self.linenum}")
                    raise TypeError
            return 'boolean'
        elif self.op == "<" or  self.op == "<=" or self.op == ">" or self.op == ">=":
            if (left == 'int' or left == 'float') and (right == 'int' or left == 'float'):
                return 'boolean'
            print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at + line {self.linenum}")
            raise TypeError



class UniOpExp(Node):
    """Class of nodes representing unary-operation expressions."""
    fields = ['op', 'arg', 'linenum']

    def __init__(self, op, arg, linenum):
        super().__init__(op, arg, linenum)
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        blockOut.append("Unary(")
        if self.op == '-':
            blockOut.append("uminus, ")
        elif self.op == '!':
            blockOut.append("neg, ")
        self.arg.anlz_procs(record, className, methodName, parent)
        blockOut.append(")")
        
        pass
    def anlz(self, className):
        self.arg.anlz(className)

    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        type = self.arg.typeChecking(className, methodName, self)
        if self.op == '-' or self.op == '+':
            if (type != 'int' and type != 'float'):
                print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at UniOp - line {self.linenum}")
                raise TypeError
            return type
        elif self.op == '!':
            if (type != 'boolean'):
                print(f"{RED}ERROR: {CLEAR_FORMAT} wrong typing at UniOp ! line {self.linenum}")
                raise TypeError
            return 'boolean'

# subclasses of Node for statements

class Assign(Node):
    """Class of nodes representing assignment statements."""
    fields = ['left', 'right', 'linenum']


    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if not isinstance(self.right, str):
            blockOut.append("Assign(")
            self.left.anlz_procs(record, className, methodName, self)
            blockOut.append(", ")
            self.right.anlz_procs(record, className, methodName, self)
            blockOut.append(")")
        else:
            blockOut.append("Auto(")
            self.left.anlz_procs(record, className, methodName, self)
            blockOut.append(", ")
            if "++" in self.right:
                blockOut.append("inc, ")
            else:
                blockOut.append("dec, ")
            if "post" in self.right:
                blockOut.append("post)")
            else:
                blockOut.append("pre)")
    def anlz(self, className):
        self.left.anlz(className)
        if not isinstance(self.right, str):
            self.right.anlz(className)
    
    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        left = self.left.typeChecking(className, methodName, self)
        if left == 'int' or 'float':
            if "postfix++" == self.right or "prefix++" == self.right or "postfix--" == self.right or "prefix--" == self.right:
                typeOutput.add(f"Assign({left}, int) at line {self.linenum}")
                return left
        right = self.right.typeChecking(className, methodName, self)
        if left == right:
            typeOutput.add(f"Assign({left}, {right}) at line {self.linenum}")
            return right
        if right in ('int', 'float', 'boolean', 'string'):
            print("Typing of assignment does not match")
            raise TypeError
        if right == 'null':
            typeOutput.add(f"Assign({left}, {right}) at line {self.linenum}")
            return right
        while (inherit[right] != None):
            if inherit[right] == left:
                typeOutput.add(f"Assign({left}, {right}) at line {self.linenum}")
                return right
            right = inherit[right]
        print("Typing of assignment does not match")
        raise TypeError



class Block(Node):
    """Class of nodes representing block statements."""
    fields = ['stmts', 'linenum']


    
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        if isinstance(parent, Constructor) or isinstance(parent, Method):
            self.scope = parent.scope
        else:
            self.scope = {}
        checker = 0
        blockOut.append("Block([\n")
        for stmt in self.stmts:
            checker = 1
            if type(stmt) in (For, While, If, StmtWord, Block):
                stmt.anlz_procs(record, className, methodName, self)
                blockOut.append("\n, ")
            elif type(stmt) in (Primary, BinOpExp, Assign, UniOpExp, Literal):
                blockOut.append("Expr( ")
                stmt.anlz_procs(record, className, methodName, self)
                blockOut.append(" )")
                blockOut.append("\n, ")
            elif (isinstance(stmt, Return)):
                blockOut.append("Return( ")
                stmt.anlz_procs(record, className, methodName, self)
                blockOut.append(" )")
                blockOut.append("\n, ")
            else:
                stmt.anlz_procs(record, className, methodName, self)
        #pop the , from the list
        blockOut.pop()
        #if there no loop prevent that next line from printing
        if checker == 1:
            blockOut.append("\n])")
    def anlz(self, className):
        for stmt in self.stmts:
            stmt.anlz(className)
    
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        if isinstance(parent, Constructor) or isinstance(parent, Method):
            self.scope = parent.scope
        else:
            self.scope = {}
        for stmt in self.stmts:
            for stmt in self.stmts:
                if (stmt.typeChecking(className, methodName, self) == False):
                    return False
        return True
    


class If(Node):
    """Class of nodes representing if statements."""
    fields = ['exp', 'stmt', 'elseStmt', 'linenum']

    
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        blockOut.append("If(")
        self.exp.anlz_procs(record, className, methodName, self)
        blockOut.append(", ")
        self.stmt.anlz_procs(record, className, methodName, self)
        if self.elseStmt != None:
            blockOut.append(", ")
            self.elseStmt.anlz_procs(record, className, methodName, self)
        else:
            blockOut.append(", Skip()")
        blockOut.append(")")
    def anlz(self, className):
        self.exp.anlz(className)
        self.stmt.anlz(className)
        if (self.elseStmt != None):
            self.elseStmt.anlz(className)

    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        exp = self.exp.typeChecking(className, methodName, self)
        stmt = self.stmt.typeChecking(className, methodName, self)
        if exp != 'boolean':
            print("Typing checking failed in If statement")
            raise TypeError
        if stmt == False:
            print("Typing checking failed in If statement")
            raise TypeError
        if self.elseStmt != None:
            blockOut.append(", ")
            elseSt = self.elseStmt.typeChecking(className, methodName, self)
            if  elseSt == False:
                print("Typing checking failed in If statement else")
                raise TypeError
        return True



class StmtWord(Node):
    """Class of nodes representing if statements."""
    fields = ['word', 'linenum']

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if self.word == 'break':
            blockOut.append("Break()")
        elif self.word == 'continue':
            blockOut.append("Continue()")
        return self.word
    

    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        return True


          
class Lhs(Node):
    fields = ['field_access', 'linenum']
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        return self.field_access.anlz_procs(record, className, methodName, self)
    def anlz(self, className):
        return self.field_access.anlz(className)


    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope

        #should return the name and type
        return self.field_access.typeChecking(className, methodName, self)

class Return(Node):
    fields = ['value', 'linenum']
    
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        self.value.anlz_procs(record, className, methodName, self)
    def anlz(self, className):
        self.value.anlz(className)


    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        type = self.value.typeChecking(className, methodName, self)
        if type == recordType[className][methodName][0]:
            return True
        print("wrong return type")
        raise TypeError

class While(Node):
    """Class of nodes representing while statements."""
    fields = ['exp', 'stmt', 'linenum']

    def __init__(self, exp, stmt, linenum):
        super().__init__(exp, stmt, linenum)
    
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        blockOut.append("while(")
        self.exp.anlz_procs(record, className, methodName, self)
        blockOut.append(", ")
        self.stmt.anlz_procs(record, className, methodName, self)
        blockOut.append(")")
    def anlz(self, className):
        self.exp.anlz(className)
        self.stmt.anlz(className)



    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        stmt = self.stmt.typeChecking(className, methodName, self)
        if self.exp.typeChecking(className, methodName, self) != 'boolean':
            print("exp is not type boolean in while loop")
            raise TypeError
        if stmt != True:
            print("stmt is not right type in while loop")
            raise TypeError
        return True
                


class For(Node):
    fields = ['lStmt_expression', 'expression', 'rStmt_expression', 'stmt', 'linenum']

    def __init__(self, lStmt_expression, expression, rStmt_expression, stmt, linenum):
        super().__init__(lStmt_expression, expression, rStmt_expression, stmt, linenum)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        blockOut.append("For(")
        if self.lStmt_expression != None:
            blockOut.append(", ")
            self.lStmt_expression.anlz_procs(record, className, methodName, self)
        if self.expression != None: 
            blockOut.append(", ")
            self.expression.anlz_procs(record, className, methodName, self)
        if self.expression != None: 
            blockOut.append(", ")
            self.rStmt_expression.anlz_procs(record, className, methodName, self)
        self.stmt.anlz_procs(record, className, methodName, self)
        blockOut.append(")")

    def anlz(self, className):

        if self.lStmt_expression != None:
            self.lStmt_expression.anlz(className)
        if self.expression != None: 
            self.expression.anlz(className)
        if self.expression != None: 
            self.rStmt_expression.anlz(className)
        self.stmt.anlz( className)


    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        if self.lStmt_expression != None:
            if self.lStmt_expression.typeChecking(className, methodName, self) == False:
                print ("type error in for loop initializer")
                raise TypeError
        if self.expression != None: 
            if self.expression.typeChecking(className, methodName, self) != 'boolean':
                print ("condition in for loop not type boolean")
                return TypeError
        if self.expression != None: 
           if self.rStmt_expression.typeChecking(className, methodName, self) == False:
               print ("type error in for loop in update expression")
               raise TypeError
        if self.stmt.typeChecking(className, methodName, self) == False:
            print("type error in body of for loop")
            raise TypeError
        
        return True


class Method(Node):
    """Class of nodes representing procedure definitions."""
    fields = ['modifiers', 'type', 'name', 'params', 'body', 'linenum']

    def __init__(self, *args):
        super().__init__(*args)

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = {}
        global blockOut, methodNum, variables, varcount, output
        stat = "instance"
        classMethod[className].add(self.name)
        # output
        type = 'void'
        if self.modifiers == None:
            self.modifiers = ['private']
        elif len(self.modifiers) == 0:
            self.modifiers = ['private']
        elif self.modifiers[0] == 'static':
            self.modifiers = ['private', 'static']
            stat = "static"
        elif len(self.modifiers) == 2:
            if self.modifiers[1] =='static':
                stat = "static"
        if self.type != 'void':
            type = self.type.anlz_procs(record, className, methodName, self)
        methOuput.append("METHOD: {}, {}, {}, {}, {}, {}".format(methodNum, self.name, className, self.modifiers[0], stat, type))
        methodName = "method" + str(methodNum)
        methodNum += 1

        # set the dictionary for constructor/method
        record[className][methodName] = {}
        if self.params != None: 
            for i in self.params:
                #i.anlz_proc should be returning tuple (type, name) from argvar object
                parm = i.anlz_procs(record, className, methodName, self)
                #store in dictionary and store it as (type, origin, id)
                record[className][methodName][ str(varcount)] = (parm[0], "formal", parm[1])
                varcount += 1
        methOuput.append("Method Parameters: {}".format(", ".join([k for k in record[className][methodName].keys()])))
        self.body.anlz_procs(record, className, methodName, self)
        methOuput.append("Variable Table:")
        for k, v in record[className][methodName].items():
            methOuput.append("VARIABLE: {}, {}, {}, {}".format(k, v[2], v[1], v[0]))
        methOuput.append("Method Body:")
        methOuput.append("".join(blockOut))
        # reset block varaibles
        varcount = 1
        blockOut = []
    def anlz(self, className):
        self.body.anlz(className)
    
    def methodScanner(self, className):
        #record return type and param
        if self.type == 'void':
            recordType[className][self.name] = ('void', [], self.modifiers)
        else:
            recordType[className][self.name] = (self.type.typeChecking(className, self.name, self), [] , self.modifiers)
        if self.params != None: 
            for p in self.params:
                recordType[className][self.name][1].append(p.typeChecking(className, self.name, self))
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = {}
        if self.params != None: 
            for p in self.params:
                p.typeChecking(className, self.name, self)
        self.body.typeChecking(className, self.name, self)

class MethInvo(Node):
    """Class of nodes representing precedure calls."""
    fields = ['fieldAccess', 'args', 'linenum']

    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        blockOut.append("Method-call(")
        global methodcall
        methodcall = 1
        self.fieldAccess.anlz_procs(record, className, methodName, self)
        args=[]
        methodcall = 0
        for arg in self.args:
            args.append(arg.anlz_procs(record, className, methodName, self))
        blockOut.append(", {})".format(args))
    
    def anlz(self, className):
        global methodcall
        methodcall = 1
        self.fieldAccess.anlz(className)
        for arg in self.args:
            arg.anlz(className)
        methodcall = 0

    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = {}
        #should return (classname , methodname) or just classname 
        name = self.fieldAccess.typeChecking(className, methodName, self)
        global literalClass, thisFlag, superFlag
        args = []
        tmp = literalClass
        for arg in self.args:
            args.append(arg.typeChecking(className, methodName, self))
        #method is (return type, list of type for args in order, modifiers)
        if name[0] == "Out" or name[0] == "In":
            if name[1] in predefinedClass[name[0]]:
                if name[0] == "Out":
                    if len(args) != 1:
                        print(f"mismatch arg typing at line {self.linenum}")
                        raise TypeError
                    if args[0] in primarytype:
                        return 'Null'
                    print(f"mismatch arg typing at line {self.linenum}")
                    raise TypeError
                else:
                    if len(args) != 0:
                        print(f"mismatch arg typing at line {self.linenum}")
                        raise TypeError
                    if name[1] == "scan_int":
                        return 'int'
                    else:
                        return 'float'
            print(f"undefined method name at line {self.linenum}")
            raise SyntaxError
        literalClass = tmp
        method = recordType[name[0]][name[1]]
        if literalClass == True:
            if not "static" in method[2] or ("private" in method[2] and className != name[0]):
                print(F"invalid access at line {self.linenum}")
                raise TypeError
            if len(method[1]) != len(args):
                print(F"invalid amount of argument in line {self.linenum}")
                raise TypeError
            for i in range(len(args)):
                if args[i] != method[1][i]:
                    print(F"wrong typing in argument in line {self.linenum}")
                    raise TypeError
            literalClass = False
            return method[0]
        else:
            if "static" in method[2] or (("private" in method[2] and className == name[0]) and (thisFlag != True and superFlag != True)):
                thisFlag, superFlag = False, False
                print(name)
                print(method)
                print(literalClass)
                print(F"invalid access at line1 {self.linenum}")
                raise TypeError
            if len(method[1]) != len(args):
                print(F"invalid amount of argument in line {self.linenum}")
                raise TypeError
            for i in range(len(args)):
                if args[i] != method[1][i]:
                    print(F"wrong tpying in argument in line {self.linenum}")
                    raise TypeError
            thisFlag = False
            superFlag = False
            return method[0]


        


class Field(Node):
    """Class of nodes representing field access."""
    fields = ['primary', 'name', 'linenum']
    def anlz_procs(self, record, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope

        if methodcall == 1:
            out = ""
            if self.primary != None:
                out = self.primary.anlz_procs(record, className, methodName, self)
            if out == 'this':
                out = "This"
            elif out == 'super':
                out = "Super"
            blockOut.append("{}, {}".format(out, self.name))
        elif self.primary != None:
            out = self.primary.anlz_procs(record, className, methodName, self)
            if out == 'this':
                field = list(record[className]['fieldVar'])
                for i in range(len(field)):
                    if field[i][1] == self.name:
                        blockOut.append("Field-access(This, {}, {})".format(self.name, i))
                        break
            elif out == 'super':
                field = list(record[inherit[className]]['fieldVar'])
                for i in range(len(field)):
                    if field[i][1] == self.name:
                        blockOut.append("Field-access(Super, {}, {})".format(self.name), i)
                        break
            else:
                if out in record:
                    field = list(record[out]['fieldVar'])
                    for i in range(len(field)):
                        if field[i][1] == self.name:
                            blockOut.append("Field-access({}, {}, {})".format(out, self.name, i))
                            break
                else:
                    blockOut.append("Field-access({}, {})".format(out, self.name))
        else:
            #check if it in local record
            if methodName != None:
                #find the most recent declared local value in the scope return -1 if none was found otherwise return the, check node implementation 
                varId = self.scopeChecker(self.name)
                if varId == -1:
                    if not self.name in record:
                        print(f"{RED}ERROR: undefined variable {self.name} at line {self.linenum}")
                        raise SyntaxError
                    return self.name
                recordOfUsedVar.add(self.name)
                blockOut.append("Variable({})".format(varId))
    

    def anlz(self, className):
       pass


    #logic for field access if the primary none that mean it the leftmost name.
    # for this would check if name is one of the class if not we check if it defined in the scope and also set and flag call literalClass to tell if it 
    # an literal class or not                
    def typeChecking(self, className, methodName, parent):
        self.parentPointer = parent
        self.scope = parent.scope
        global literalClass,thisFlag, superFlag
        # leftmost of the feild access
        if self.primary == None:
            if self.name == "Out" or self.name == "In":
                return self.name
            if self.name in recordType:
                literalClass = True 
                return self.name
            else:
                #see if variable exist
                v = self.scopeChecker(self.name)
                if v != -1:
                    literalClass = False
                    return v
                else:
                    #that mean it an method name
                    literalClass = True
                    return (className, self.name)
            
        else:
            primary = self.primary.typeChecking(className, methodName, self)
            if isinstance(primary, tuple):
                print(f"{RED}ERROR: invalid access at line {self.linenum}")
                raise TypeError
            if primary == "Out" or primary == "In":
                return (primary, self.name)
            if primary in primarytype:
                print(f"{RED}ERROR: field access on primary type at line {self.linenum}")
                raise TypeError
            if primary in recordType:
                # it an method if the name exist in the method so I would return the type and the method name
                if self.name in recordType[primary]:
                    return (primary, self.name)
                # else it is an field variable
                while primary != None:
                    for type, name, modifier in recordFieldtype[primary]:
                        if name == self.name:
                            if literalClass == False:
                                if not "static" in modifier and (not "private" in modifier or thisFlag == True or superFlag == True or className == primary):
                                    thisFlag, superFlag = False, False
                                    return type
                                else:
                                    print(f"{RED}accessing an static or private variable at line {self.linenum}")
                                    raise TypeError
                            else:
                                if 'static' in modifier and (not "private" in modifier or thisFlag == True or superFlag == True or className == primary):
                                    literalClass = False
                                    return type
                                print(f"{RED}accessing an non static or private variable at line1 {self.linenum}")
                                raise TypeError
                    if (self.name in recordType[primary]):
                        return (primary, self.name)
                    primary = inherit[primary]
            print(f"{RED}ERROR: invalid access at line {self.linenum}")
            raise TypeError



def writeAST(ast_block):
    global output
    ast_block.anlz_procs(record, None, None, None)
    #cehck for super class exist or not
    for superclass in inherit.items():
        if superclass[1] != None:
            if not superclass[1] in record:
                print("extend class {} does not exist".format(superclass[1]))
                raise SyntaxError
    ast_block.anlz(None)
    ast_block.methodScanner(None)
    ast_block.typeChecking(None,None,None)

    #print("\n".join(output))
    #print("Type Assignment:")
    #print("\n".join(typeOutput))

    
