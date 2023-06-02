from decaf_ast import *
import os
#store size of each class
fieldVariable = {}

register = []
tempRegister = []

addtionalTemp = []
offset = 0
fieldaccess = False
staticaccess = False
listOfConstructor = []
listOfMethod = []
tempOff =0
lastFieldAddress = ""
ifCounter = 0
whileCounter = 0
forCounter = 0
nearestExit = []
lastname = ""
#idea the expression nodes such as binopexp, lhs and primary will return registers  
file = ""
def setfile(inFile):
    global file
    file_name_without_ext, ext = os.path.splitext(inFile)
    file = open(file_name_without_ext + ".ami", "w")
def codeGenManager(node, classname):
    if isinstance(node, Classes):
        for c in node.classes:
            codeGenManager(c, classname)
    elif isinstance(node, Class):
        codeGenClass(node, classname)
    elif isinstance(node, FieldDecl):
        codeGenFieldDecl(node, classname)
    elif isinstance(node, Constructor):
        codeGenConstructor(node, classname)
    elif isinstance(node, Block):
        for stmt in node.stmts:
            codeGenManager(stmt, classname)
    elif isinstance(node, Variables):
        for var in node.variables:
            tempRegister.append((node.type.name, CodeGenlocalVar(var, classname)))
    elif isinstance(node, Assign):
        codeGenAssign(node, classname)
    elif isinstance(node, BinOpExp):
        return codeGenBinOp(node, classname)
    elif isinstance(node, Lhs):
        return codeGenManager(node.field_access, classname)
    elif isinstance(node, Primary):
        return codeGenPrim(node, classname)
    elif isinstance(node, Literal):
        if node.value[1] == True:
            return ('int', 1)
        if node.value[1] == False:
            return  ('int', 0)
        return node.value
    elif isinstance(node, Field):
        return codeGenFieldAccess(node, classname)
    elif isinstance(node, Method):
        codeGenMethod(node, classname)
    elif isinstance(node, If):
        codeGenIf(node, classname)
    elif isinstance(node, While):
        codeGenWhile(node, classname)
    elif isinstance(node, UniOpExp):
        return codeGenUniOp(node, classname)
    elif isinstance(node, Return):
        codeGenReturn(node, classname)
    elif isinstance(node, New):
        return codeGenNew(node, classname)
    elif isinstance(node, StmtWord):
        codeGenStmtWord(node, classname)
    elif isinstance(node, For):
        codeGenFor(node, classname)
    elif isinstance(node, MethInvo):
        return codeGenMethInvo(node, classname)
    else:
        file.write("missing Node\n")

def codeGenMethInvo(node, classname):
    global lastname
    lastname = ""
    codeGenManager(node.fieldAccess, classname)
    temp = lastname
    lastname = ""
    file.write(f"save a0\n")
    for i in range(len(register)):
        file.write(f"save a{i + 1}\n")
    for i in range(len(tempRegister)):
        file.write(f"save t{i}\n")
    count = 1
    for i in node.args:
        reg = codeGenManager(i, classname)
        file.write(f"move a{count}, {reg[1]}\n")
        count +=1
    index = listOfMethod.index(temp)
    file.write(f"call M_{temp}_{index}\n")
    reg = "t" + str(len(tempRegister) + len(addtionalTemp))
    addtionalTemp.append(reg)
    file.write(f"move {reg}, a0\n")
    for i in range(len(register)):
        file.write(f"load a{i + 1}\n")
    for i in range(len(tempRegister)):
        file.write(f"load t{i}\n")
    
    return ('int', reg)
def codeGenFor(node, classname):
    global forCounter
    if node.lStmt_expression != None:
        codeGenManager(node.lStmt_expression, classname)
    file.write(f"for_{forCounter}:\n")
    if node.expression != None:
        nearestExit.append(f"for_end{forCounter}\n")
        reg = codeGenManager(node.expression, classname)
        file.write(f"bz {reg[1]}, for_end{forCounter}\n")
    codeGenManager(node.stmt, classname)
    if node.rStmt_expression != None:
        codeGenManager(node.rStmt_expression, classname)
    nearestExit.pop()
    file.write(f"jmp for_{forCounter}\n")
    file.write(f"for_end{forCounter}:\n")
    forCounter +=1

def codeGenStmtWord(node, classname):
    if node.word == 'break':
        file.write(f"jmp {nearestExit[len(nearestExit) - 1]}\n")
def codeGenNew(node, classname):
    file.write(f"save a0\n")
    file.write(f"halloc a0, {len(fieldVariable[node.type])}\n")
    for i in range(len(register)):
        file.write(f"save a{i + 1}\n")
    for i in range(len(tempRegister)):
        file.write(f"save t{i}\n")
    count = 1
    for i in node.arguments:
        reg = codeGenManager(i, classname)
        file.write(f"move a{count}, {reg[1]}\n")
        count +=1
    index = listOfConstructor.index(node.type)
    file.write(f"call C_{index}\n")
    reg = "t" + str(len(tempRegister) + len(addtionalTemp))
    addtionalTemp.append(reg)
    file.write(f"move {reg}, a0\n")
    file.write(f"load a0\n")
    for i in range(len(register)):
        file.write(f"load a{i + 1}\n")
    for i in range(len(tempRegister)):
        file.write(f"load t{i}\n")
    return (node.type, reg)
def codeGenReturn(node, classname):
    if node.value != None:
        reg = codeGenManager(node.value, classname)
        file.write(f"move a0, {reg[1]}\n")
def codeGenUniOp(node, classname):
    if node.op == '-':
        reg = codeGenManager(node.arg, classname)
        file.write (f"{reg[0][0]}mul {reg[1]}, {reg[1]}, -1\n")
        return reg
    elif node.op == '!':
        reg = codeGenManager(node.arg, classname)
        file.write(f"isub {reg[1]}, 1, {reg[1]}\n")
        return reg
    else:
        return codeGenManager(node.arg, classname)
def codeGenWhile(node, classname):
    global whileCounter
    file.write(f"while_{whileCounter}:\n")
    nearestExit.append(f"while_end{whileCounter}")
    reg = codeGenManager(node.exp, classname)
    file.write(f"bz {reg[1]}, while_end{whileCounter}\n")
    codeGenManager(node.stmt, classname)
    nearestExit.pop()
    file.write(f"jmp while_{whileCounter}\n")
    file.write(f"while_end{whileCounter}:\n")
    whileCounter += 1

def codeGenIf(node, classname):
    reg = codeGenManager(node.exp, classname)
    global ifCounter
    if node.elseStmt != None:
        file.write(f"bz {reg[1]}, ifelse_{ifCounter}\n")
        codeGenManager(node.stmt, classname)
        file.write(f"jmp ifend_{ifCounter}\n")
        file.write(f"ifelse_{ifCounter}:\n")
        codeGenManager(node.elseStmt, classname)
    else:
        file.write(f"bz {reg[1]}, ifend_{ifCounter}\n")
        codeGenManager(node.stmt, classname)
    file.write(f"ifend_{ifCounter}:\n")
    ifCounter += 1

def removeAdditional(left, right):
    if left in addtionalTemp:
        addtionalTemp.remove(left)
    if right in addtionalTemp:
        addtionalTemp.remove(right)
def getRegister(name, local, classname):
    global offset
    temp = offset
    if local == True:
        for val in reversed(range(len(tempRegister))):
            if tempRegister[val][1] == name:
                return (tempRegister[val][0], val, "local")
        for val in reversed(range(len(register))):
            if register[val][1] == name:
                return (register[val][0], val, "arg")
        raise ValueError
    else:
        for val in reversed(range(len(fieldVariable[classname]))):
            if fieldVariable[classname][val][1] == name:
                if temp == 0:
                    offset = 0
                    return (fieldVariable[classname][val][0], val)
                temp -= 1
        return -1

def codeGenMethod(node, classname):
    listOfMethod.append(node.name)
    file.write(f"M_{node.name}_{len(listOfMethod) - 1}:\n")
    register.clear()
    tempRegister.clear()
    if node.params != None:
        for param in node.params:
            codeGenConstructorParam(param, classname)
    codeGenManager(node.body, classname)
    file.write('ret\n')


def codeGenClass(node, classname):
    if node.superclass != None:
         fieldVariable[node.name] = [] + fieldVariable[node.superclass]
    else:
        fieldVariable[node.name] = []
    
    for b in node.body:
        codeGenManager(b, node.name)

def codeGenFieldDecl(node, classname):
    codeGenFieldVars(node.variables, classname)

def codeGenFieldVars(node, classname):
    for var in node.variables:
        fieldVariable[classname].append((node.type.name, var.name))

def codeGenConstructor(node, classname):
    listOfConstructor.append(node.name)
    file.write(f"C_{len(listOfConstructor) - 1}:\n")
    register.clear()
    tempRegister.clear()
    if node.params != None:
        for param in node.params:
            codeGenConstructorParam(param, classname)
    codeGenManager(node.body, classname)
    file.write("ret\n")


def codeGenConstructorParam(node, classname):
    register.append((node.type.name, node.name.name))

def CodeGenlocalVar(node, classname):
    return node.name

def codeGenAssign(node, classname):
    global tempOff, lastFieldAddress, fieldaccess
    left = codeGenManager(node.left, classname)
    outStr = ""
    if left == 'this' or left == 'super':
        left = ('int', 'a0')
    if lastFieldAddress != "":
        outStr += f'hstore {lastFieldAddress}, {tempOff}, '
        lastFieldAddress = ""
        tempOff = 0
        fieldaccess = True
    else:
        outStr += f"move {left[1]}, " 
    if "postfix++" == node.right or "prefix++" == node.right:
        if fieldaccess:
            leftR = getRegister(left, False, classname)
            left = (leftR[0], "t" + str(len(tempRegister) + len(addtionalTemp)))
            file.write(f"hload {left[1]}, a0, {leftR[1]}\n")
            file.write(f"{leftR[0][0]}add {left[1]}, {left[1]}, 1\n")
            fieldaccess = False
            outStr += f"{left[1]}"
        else:
            staticaccess = False
            right = "t" + str(len(tempRegister) + len(addtionalTemp))
            file.write(f"iadd {right}, 0, 1\n")
            outStr += right
    elif "postfix--" == node.right or "prefix--" == node.right:
        if fieldaccess:
            leftR = getRegister(left, False, classname)
            left = (leftR[0], "t" + str(len(tempRegister) + len(addtionalTemp)))
            file.write(f"hload {left[1]}, a0, {leftR[1]}\n")
            file.write(f"{leftR[0][0]}sub {left[1]}, {left[1]}, 1\n")
            fieldaccess = False
            outStr += f"{left[1]}"
        else:
            staticaccess = False
            right = "t" + str(len(tempRegister) + len(addtionalTemp))
            file.write(f"isub {right}, 0, 1\n")
            outStr += right
    else:
        fieldaccess = False
        staticaccess = False
        right = codeGenManager(node.right, classname)
        if not isinstance(right, str):
            right = str(right[1])
        outStr += right
        fieldaccess = False
        staticaccess = False
    file.write(outStr + "\n")

#ig the return would be (type)
def codeGenBinOp(node, classname):
    left = codeGenManager(node.left, classname)
    global fieldaccess, staticaccess
    if staticaccess:   
        left = ('int', 'sap')
        file.write(f"iadd {left[1]}, 0, sap\n")
        staticaccess = False
    right = codeGenManager(node.right, classname)
    if staticaccess:   
        right = ('int', 'sap')
        addtionalTemp.append(right[1])  
        staticaccess = False
    t = 'int'
    if (str.lower(left[0]) == "float" or str.lower(right[0]) == "float"):
        t = 'float'
    if isinstance(left[1], str):
        storingReg = left[1]
        removeAdditional(left, right)
    elif isinstance(right[1], str):
        storingReg = right[1]
        removeAdditional(left[1], right)
    else:
        storingReg = "t" + str(len(tempRegister) + len(addtionalTemp))
        addtionalTemp.append(storingReg)
    
    if node.op == "+":
        file.write(f"{t[0]}add {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == "-":
        file.write(f"{t[0]}sub {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == "*":
        file.write(f"{t[0]}mul {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == '/':
        file.write(f"{t[0]}div {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == "<":
        file.write(f"{t[0]}lt {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == "<=":
        file.write(f"{t[0]}leq {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == ">":
        file.write(f"{t[0]}gt {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == ">=":
        file.write(f"{t[0]}geq {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == "==":
        strn = len(tempRegister) + len(addtionalTemp)
        storingReg1 = "t" + str(strn)
        file.write(f"{t[0]}leq {storingReg1}, {left[1]}, {right[1]}\n")
        strn += 1
        storingReg2 = "t" + str(strn)
        file.write(f"{t[0]}geq {storingReg2}, {left[1]}, {right[1]}\n")
        #1*1 = 1 1*0 =0 0*0 == 0 hence this work for ==
        file.write(f"{t[0]}mul {storingReg}, {storingReg1}, {storingReg2}\n")
    elif node.op == "&&":
        #1*1 = 1 1*0 =0 0*0 == 0
        file.write(f"{t[0]}mul {storingReg}, {left[1]}, {right[1]}\n")
    elif node.op == "||":
        strn = len(tempRegister) + len(addtionalTemp)
        storingReg1 = "t" + str(strn)
        file.write(f"{t[0]}geq {storingReg1}, {left[1]}, {right[1]}\n")
        strn +=1
        storingReg2 = "t" + str(strn)
        file.write(f"{t[0]}geq {storingReg2}, {left[1]}, {right[1]}\n")
        file.write(f"{t[0]}add {storingReg1}, {left[1]}, {right[1]}\n")
        # check if it equal to 1
        file.write(f"{t[0]}leq {storingReg2}, {storingReg1}, 1\n")
        strn +=1
        storingReg3 = "t" + str(strn)
        file.write(f"{t[0]}geq {storingReg3}, {storingReg1}, 1\n")
        file.write(f"{t[0]}mul {storingReg}, {storingReg2}, {storingReg3}\n")  
    
    elif node.op == "!=":
        strn = len(tempRegister) + len(addtionalTemp)
        storingReg1 = "t" + str(strn)
        file.write(f"{t[0]}leq {storingReg1}, {left[1]}, {right[1]}\n")
        strn += 1
        storingReg2 = "t" + str(strn)
        file.write(f"{t[0]}geq {storingReg2}, {left[1]}, {right[1]}\n")
        #1*1 = 1 1*0 =0 0*0 == 0 hence this work for ==
        file.write(f"{t[0]}mul {storingReg}, {storingReg1}, {storingReg2}\n")
        file.write(f"{t[0]}leq {storingReg}, {storingReg}, 0\n")
    return (t, storingReg)

def codeGenPrim(node, classname):
    if node.type == 'single':
        return codeGenManager(node.others, classname)

    elif node.type == 'expression':
        return codeGenManager(node.others, classname)

    else:
        global fieldaccess
        if node.type == 'this':
            fieldaccess = True
            return 'this'
        else:
            global offset
            offset = 1
            fieldaccess = True
            return 'super'
        
def codeGenFieldAccess(node, classname):
    global fieldaccess, staticaccess, tempOff, lastFieldAddress, lastname
    if lastname == "":
        lastname = node.name
    if node.primary == None:
        if node.name in fieldVariable:
            global staticaccess
            staticaccess = True
            return ('int', 'sap')
        else:
            leftR = getRegister(node.name, True, classname)
            left = (leftR[0], "a" + str(leftR[1] + 1))
            if leftR[2] == "local":
                left = (leftR[0], "t" + str(leftR[1]))
                addtionalTemp.append(left[1])
            return left
    else:
        prim = codeGenManager(node.primary, classname)
        if fieldaccess:
            leftR = getRegister(node.name, False, classname)
            if leftR == -1:
                return ('int', 'a0')
            prim = (leftR[0], "t" + str(len(tempRegister) + len(addtionalTemp)))    
            addtionalTemp.append(prim[1])  
            tempOff = leftR[1]
            file.write(f"hload {prim[1]}, a0, {leftR[1]}\n")
            lastFieldAddress = 'a0'
            fieldaccess = False
        elif staticaccess:   
            prim = ('int', 'sap')
        else:
            if prim[0] != 'int' and prim[0] != 'float':
                leftR = getRegister(node.name, False, prim[0])
                if leftR == -1:
                    return ('int', 'a0')
                tempOff = leftR[1]
                temp = prim[1]
                prim = (leftR[0], "t" + str(len(tempRegister) + len(addtionalTemp)))    
                addtionalTemp.append(prim[1])
                lastFieldAddress = temp
                file.write(f"hload {prim[1]}, {temp}, {leftR[1]}\n")
            else:
                return prim
    return prim

