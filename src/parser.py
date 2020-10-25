import sys
import re
sys.path.insert(0, "../..")
import os
import ply.lex as lexer
import ply.yacc as yacc

ifile = ""
ofile = ""
flag = 0
dic={}
dic["error"] = ""
helpstring = "Please fllow the below instructions in order to get the AST:\n\n1. Type in the command \"python3 parser.py\" followed by one or more options as described further.\n\n2. -input: Type in \"-input=inputfile\" to give inputflie as input file. This option is necessary to get the output.\n\n3. -out: Type in \"-out=outputfile\" to get the final AST in the file named outputfile. If this option is not specified then a file with name inputfile.ps contains the output AST.\n\n4. -help: Typing \"-help\" prints this helper content.\n\n5. -verbose: Typing \"-verbose\" prints the errors (if any) on standard output."

for k in sys.argv:
    if "-input=" in k:
        ifile = k.split("=")[1]
    if "-out=" in k:
        ofile = k.split("=")[1]
    if k == "-help":
        print(helpstring)
    if k == "-verbose":
        flag = 1

if ifile == "":
    print("No input file provided. Please provide an input file or type \"python3 parser.py -help\" for help.")
    exit()

if ofile == "":
    ofile = ifile.split('/')[-1].split('.')[0]+".ps"

class Node:
    def __init__(self, label=None,typ=None):
        self.label = label
        self.children = []
        self.typ = typ

def clean_ast(root):
    if root == None:
        return None      
    for k in root.children:
        k=clean_ast(k)
    for k in range(len(root.children)):
        temp= root.children[k]
        if temp!=None and len(temp.children)==1 and temp.typ=='M':
            root.children = root.children[0:k] + [temp.children[0]] + root.children[k+1:len(root.children)]
    return root

def printdot(root):
    f = open('graph.dot',"w+")
    f.write("digraph D{\n\tnode [shape=circle fontname=Arial];\n")
    st = []
    st.append((root,0))
    i = 1
    while(st!=[]):
        if st[0][0]!=None and len(st[0][0].children)!=0:
            if st[0][0].label[0] == '"' or st[0][0].label[0] == "'":
                f.write('\tnode'+str(st[0][1])+' [label = '+st[0][0].label+']'+"\n")
            else:
                f.write('\tnode'+str(st[0][1])+' [label = "'+st[0][0].label+'"]'+"\n")
            for k in st[0][0].children:
                if(k!=None):
                    st.append((k,i))
                    if k.label[0] == '"' or k.label[0] == "'":
                        f.write('\tnode'+str(i)+' [label = '+k.label+']'+"\n")
                    else:
                        f.write('\tnode'+str(i)+' [label = "'+k.label+'"]'+"\n")
                    f.write("\tnode"+str(st[0][1])+" -> ")
                    f.write('node'+str(i)+"\n")
                    i = i+1
        st = st[1:]
    f.write("}")
    f.close()

def make_leaf(a):
    if(a==None):
        return None
    elif a in Seperators:
        temp = "Sep ( "+ a + " )"
    elif a in Operators:
        temp = "Op ( "+ a + " )"
    elif a in forbidden:
        temp = "KeyWord ( "+ a + " )"             
    elif a[0] == "'":
        temp = "Literal ( " + "\\'" + "".join(a[1:len(a)-1]) + "\\'  )"
    elif a[0] == '"':
        temp = "Literal (" + '\\"' + "".join(a[1:len(a)-1]) + '\\"' + " )"
    elif (a[0] >'0' and a[0] < '9') or a[0]=='.':
        temp = "Literal (" + a + " )"
    else:
        temp = "Id ( " + a + " )"
    return Node(temp,'L')

def make_node_hierachy(a,b):
    if(b!=None):
        a.children.append(b)
    return a

def make_node_hierachy_deep(a,b):
    if(b!=None):
        t=a
        while(len(t.children)>0):
            t=t.children[0]
        t.children.append(b)
    return a

def make_node_hierachy_1(a,b):
    if(a==None):
        return b
    if(b!=None):
        a.children=[b]+a.children
    return a 

def merge_node(a,b,label):
    node = Node(label,'M')
    for k in a:
        if k!=None:
            node.children.append(k)
    if(b != None):
        for k in b.children:
            if(k!=None):
                node.children.append(k)
    return node

def make_node(a,label):		
    node = Node(label,'M')
    for k in a:
        if(k!=None):
            node.children.append(k)
    return node

Seperators = ['[',']', '(',')','::',',',';',"...",'.','@','{','}']
Operators =[" ++","+=","+","--","-=","->","-","=","","/=","/","&=","&&","&","%=","%","^=","^","","=","","","","","","<=","<<=","<<","<",">>>=",">>=",">=",">",">>>",">>","==","=","!=","!","~","?",":"]
tokens = ("IDENTIFIER","abstract","continue","for","new","switch","default","if","package","synchronized",
"boolean","do","private","this",
"break","double","implements","protected","throw",
"byte","else","import","public","throws","case","enum","instanceof","return","transient","catch",
"extends","int","short","try","char","String","final","interface","static","void","class","finally","long","volatile",
"float","native","super","while", "equals", "gt", "lt", "not", "tilda", "question", "colon", "equalsequals",
"gtequals", "ltequals", "notequals", "andand", "oror", "plusplus", "minusminus", "plus", "minus", "multiply", "divide",
"and", "or", "exor", "mod", "leftshift", "rightshift", "doubleright", "plusequals", "minusequals", "multiplyequals",
"divideequals", "andequals", "orequals", "exorequals", "modequals", "leftshiftequals", "rightshiftequals", "triplerightequals",
"lb", "rb", "lp", "rp", "ls", "rs", "semicolon", "comma", "dot",
"FloatingPointLiteral","NullLiteral","IntegerLiteral","StringLiteral","CharacterLiteral","BooleanLiteral")
forbidden = ("abstract","continue","for","new","switch",
"default","if","package","synchronized",
"boolean","do","private","this",
"break","double","implements","protected","throw",
"byte","else","import","public","throws","case","enum","instanceof","return","transient","catch",
"extends","int","short","try","char","String","final","interface","static","void","class","finally","long","volatile"
"float","native","super","while")
bol_lit = ("true","false")
nulit =("null")
fl=("Float.NaN","Double.NaN","POSITIVE_INFINITY","NEGATIVE_INFINITY")
t_equals = r'='
t_gt = r'>'
t_lt = r'<'
t_not = r'!'
t_tilda = r'~'
t_question = r'\?'
t_colon = r':'
t_equalsequals = r'=='
t_gtequals = r'>='
t_ltequals = r'<='
t_notequals = r'!='
t_andand = r'&&'
t_oror = r'\|\|'
t_plusplus = r'\+\+'
t_minusminus = r'--'
t_plus = r'\+'
t_minus = r'-'
t_multiply = r'\*'
t_divide = r'/'
t_and = r'&'
t_or = r'\|'
t_exor = r'\^'
t_mod = r'%'
t_leftshift = r'<<'
t_rightshift = r'>>'
t_doubleright = r'>>>'
t_plusequals = r'\+='
t_minusequals = r'-='
t_multiplyequals = r'\*='
t_divideequals = r'/='
t_andequals = r'&='
t_orequals = r'\|='
t_exorequals = r'\^='
t_modequals = r'%='
t_leftshiftequals = r'<<='
t_rightshiftequals = r'>>='
t_triplerightequals = r'>>>='
t_lb = r'\('
t_rb = r'\)'
t_lp = r'\{'
t_rp = r'\}'
t_ls = r'\['
t_rs = r'\]'
t_semicolon = r';'
t_comma = r','
t_dot = r'\.'
t_ignore = ' \t\f\r\v'
# t_CharacterLiteral = r'[\'][^\'\\\n]|[\\][btnfr\"\'\\]|[\\][0-3]?[0-7][0-7]?[\']'
t_CharacterLiteral = r'\'([^\\\n]|(\\.))*?\''
# t_StringLiteral= r'[\"]([^\"\\\n]|[\\][btfr\"\'\\]|([\\][0-3]?[0-7][0-7]?))*[\"]'
t_StringLiteral = r'\"([^\\\n]|(\\.))*?\"'
t_FloatingPointLiteral = r'([0-9]([_]*[0-9])*)?[\.]([0-9]([_]*[0-9])*)([eE][\+\-]?[0-9]([_]*[0-9])*)?[fFdD]?| ([0-9]([_]*[0-9])*)[\.]?([0-9]([_]*[0-9])*)?([eE][\+\-]?[0-9]([_]*[0-9])*)[fFdD]?  |  ([0-9]([_]*[0-9])*)[\.]?([0-9]([_]*[0-9])*)?([eE][\+\-]?[0-9]([_]*[0-9])*)?[fFdD]  |  [0][xX]([0-9a-fA-F]([_]*[0-9a-fA-F])*)[\.]?([0-9a-fA-F]([_]*[0-9a-fA-F])*)?[pP][\+\-]?[0-9]([_]*[0-9])*[fFdD]?|[0][xX]([0-9a-fA-F]([_]*[0-9a-fA-F])*)?[\.]([0-9a-fA-F]([_]*[0-9a-fA-F])*)[pP][\+\-]?[0-9]([_]*[0-9])*[fFdD]? | [1][fFdD][\/][0][fFdD]'     
t_IntegerLiteral = r' 0[0-7_]*[0-7][lL]?| 0[bB]([01][01_]*[01]|[01])[lL]?  | 0[xX]([0-9a-fA-F][0-9a-fA-F_]*[0-9a-fA-F]|[0-9a-fA-F])[lL]?  |  ([1-9][0-9_]*[0-9]|[0-9])[lL]?'

def t_line(t):
    r'\n'
    t.lexer.lineno+=1

def t_comment(t):
    r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)|//[^\n]*'
    t.lexer.lineno += t.value.count('\n')

def t_IDENTIFIER(t):
    r'[A-Za-z_$][A-Za-z0-9_$]*'
    if t.value in forbidden:
        t.type=t.value
    elif(t.value in bol_lit):
        t.type="BooleanLiteral" 
    elif(t.value =="null"):
        t.type="NullLiteral"
    elif(t.value in fl):
        t.type="FloatingPointLiteral"            
    return t

def t_error(t):
	print(t.value)
	print("Illegal character %s at line number %d" % (repr(t.value[0])))
	t.lexer.skip(1)
lexer.lex()

def p_Goal(p):
    '''Goal : CompilationUnit'''
    p[0] = p[1]


def p_error(p):
    t=parser.token()
    if t != None:
        dic["error"]="Error on symbol "+ t.value+ " in line number "+str(p.lineno)
def p_Literal(p):
    '''Literal : IntegerLiteral
	| FloatingPointLiteral
	| BooleanLiteral
	| CharacterLiteral
	| StringLiteral
	| NullLiteral'''
    p[0] = make_leaf(p[1])

def p_Type(p):
    '''Type : PrimitiveType
	| ReferenceType'''
    p[0] = p[1]

def p_PrimitiveType(p):
    '''PrimitiveType : NumericType
	| boolean'''
    if p[1] == "boolean":
        p[0] = make_leaf(p[1])
    else:
        p[0] = p[1]

def p_NumericType(p):
    '''NumericType : IntegralType
	| FloatingPointType'''
    p[0] = p[1]

def p_IntegralType(p):
    '''IntegralType : byte
	| short
	| int
	| long
	| char
    | String'''
    p[0] = make_leaf(p[1])

def p_FloatingPointType(p):
    '''FloatingPointType : float
	| double'''
    p[0] = make_leaf(p[1])

def p_ReferenceType(p):
    '''ReferenceType : ClassOrInterfaceType
	| ArrayType'''
    p[0] = p[1]

def p_ClassOrInterfaceType(p):
    '''ClassOrInterfaceType : Name1'''
    p[0] = p[1]

def p_ClassType(p):
    '''ClassType : ClassOrInterfaceType'''
    p[0] = p[1]

def p_InterfaceType(p):
    '''InterfaceType : ClassOrInterfaceType'''
    p[0] = p[1]

def p_ArrayType(p):
    '''ArrayType : PrimitiveType ls rs
	| Name1 ls rs
	| ArrayType ls rs'''
    p[0] = make_node([p[1], make_leaf(p[2]), make_leaf(p[3])], "ArrayType")

def p_Name(p):
    '''Name : Name1
    | PrimitiveType lb Name1 rb'''
    if len(p) > 2:
        p[0] = make_node_hierachy(p[1], p[3])
    else:
        p[0] = p[1]

def p_Name1(p):
    '''Name1 : SimpleName
	| QualifiedName'''
    p[0] = p[1]

def p_SimpleName(p):
    '''SimpleName : Identifier'''
    p[0] = p[1]

def p_QualifiedName(p):
    '''QualifiedName : Name1 dot Identifier'''
    p[0] = make_node_hierachy_deep(p[1], p[3])

def p_CompilationUnit(p):
    '''CompilationUnit : PackageDeclarationopt ImportDeclarationsopt TypeDeclarationsopt'''
    p[0] = make_node([p[1], p[2], p[3]], "CompUnit")

def p_ImportDeclarations(p):
    '''ImportDeclarations : ImportDeclaration
	| ImportDeclarations ImportDeclaration'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "ImportDecl")
        p[0] = merge_node(p[1].children, p[0], "ImportDecls")
    else:
        p[0] = p[1]

def p_TypeDeclarations(p):
    '''TypeDeclarations : TypeDeclaration
	| TypeDeclarations TypeDeclaration'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "TypeDecl")
        p[0] = merge_node(p[1].children, p[0], "TypeDecls")
    else:
        p[0] = p[1]

def p_PackageDeclaration(p):
    '''PackageDeclaration : package Name1 semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "PackageDecl")

def p_ImportDeclaration(p):
    '''ImportDeclaration : SingleTypeImportDeclaration
	| TypeImportOnDemandDeclaration'''
    p[0] = p[1]
def p_c4(p):
	''' c4 : static
	| empty '''
	p[0] = make_leaf(p[1])
def p_SingleTypeImportDeclaration(p):
    '''SingleTypeImportDeclaration : import c4 Name1 semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2],p[3], make_leaf(p[4])], "SingleTypeImportDecl")

def p_TypeImportOnDemandDeclaration(p):
	'''TypeImportOnDemandDeclaration : import c4 Name1 dot multiply semicolon'''
	p[0] = make_node([make_leaf(p[1]),p[2], make_node_hierachy_deep(p[3], make_leaf(p[5])), make_leaf(p[6])], "TypeImportOnDemandDecl")

def p_TypeDeclaration(p):
	'''TypeDeclaration : ClassDeclaration
	| InterfaceDeclaration
	| semicolon'''
	if p[1] == ';':
		p[0] = make_leaf(p[1])
	else:
		p[0] = p[1]

def p_Modifiers(p):
    '''Modifiers : Modifier
	| Modifiers Modifier'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "Modifier")
        p[0] = merge_node(p[1].children, p[0], "Modifiers")
    else:
        p[0] = p[1]

def p_Modifier(p):
    '''Modifier : public
	| protected
	| private
	| static
	| abstract
	| final
	| native
	| synchronized
	| transient
	| volatile'''
    p[0] = make_leaf(p[1])

def p_ClassDeclaration(p):
    '''ClassDeclaration : Modifiersopt class Identifier Superopt Interfacesopt ClassBody'''
    p[0] = make_node([p[1], make_leaf(p[2]), p[3], p[4], p[5], p[6]], "ClassDecl")

def p_Super(p):
    '''Super : extends ClassType'''
    p[0] = make_node([make_leaf(p[1]), p[2]], "Super")

def p_Interfaces(p):
    '''Interfaces : implements InterfaceTypeList'''
    p[0] = make_node([make_leaf(p[1]), p[2]], "Interfaces")

def p_InterfaceTypeList(p):
    '''InterfaceTypeList : InterfaceType
	| InterfaceTypeList comma InterfaceType'''
    if len(p) > 2:
        p[0] = make_node([p[3]], "InterfaceType")
        p[0] = merge_node(p[1].children, p[0], "InterfaceTypeList")
    else:
        p[0] = p[1]

def p_ClassBody(p):
    '''ClassBody : lp ClassBodyDeclarationsopt rp'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ClassBody")

def p_ClassBodyDeclarations(p):
    '''ClassBodyDeclarations : ClassBodyDeclaration
	| ClassBodyDeclarations ClassBodyDeclaration'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "ClassBodyDecl")
        p[0] = merge_node(p[1].children, p[0], "ClassBodyDecls")
    else:
        p[0] = p[1]

def p_ClassBodyDeclaration(p):
    '''ClassBodyDeclaration : ClassMemberDeclaration
	| StaticInitializer
	| ConstructorDeclaration
    | ClassDeclaration
    | EnumDeclaration'''
    p[0] = p[1]

def p_EnumDeclaration(p):
	'''EnumDeclaration : Modifiersopt enum Identifier SuperInterfacesopt EnumBody'''
	p[0] = make_node([p[1], make_leaf(p[2]), p[3], p[4], p[5]], "EnumDeclaration")

def p_SuperInterfacesopt(p):
	'''SuperInterfacesopt : implements InterfaceTypeList
	| empty'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node([make_leaf(p[1]), p[2]], "SuperInterfacesopt")

def p_EnumBody(p):
	'''EnumBody : lp EnumConstantList commaopt EnumBodyDeclarationsopt rp
	| lp commaopt EnumBodyDeclarationsopt rp'''
	if len(p)==5:
		p[0] = make_node([make_leaf(p[1]), p[3], make_leaf(p[4])], "EnumBody")
	else:
		p[0] = make_node([make_leaf(p[1]), p[2], p[4], make_leaf(p[5])], "EnumBody")


def p_EnumConstantList(p):
	'''EnumConstantList : EnumConstantList comma EnumConstant
	| EnumConstant'''
	if len(p) > 2:
		p[0] = make_node([p[3]], "EnumConstantList")
		p[0] = merge_node(p[1].children, p[0], "EnumConstantList")
	else:
		p[0] = p[1]


def p_EnumConstant(p):
	'''EnumConstant : Identifier ArgListopt ClassBodyopt'''
	p[0] = make_node([p[1], p[2], p[3]], "EnumConstant")

def p_ArgListopt(p):
	'''ArgListopt : lb ArgumentListopt rb
	| empty'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ArgListopt")

def p_ClassBodyopt(p):
	'''ClassBodyopt : ClassBody
	| empty'''
	p[0] = p[1]

def p_EnumBodyDeclarations(p):
	'''EnumBodyDeclarations : semicolon ClassBodyDeclarationsopt'''
	p[0] = make_node([make_leaf(p[1]), p[2]], "EnumBodyDeclarations")

def p_EnumBodyDeclarationsopt(p):
	'''EnumBodyDeclarationsopt : EnumBodyDeclarations
	| empty'''
	p[0] = p[1]

def p_ClassMemberDeclaration(p):
    '''ClassMemberDeclaration : FieldDeclaration
	| MethodDeclaration'''
    p[0] = p[1]

def p_FieldDeclaration(p):
    '''FieldDeclaration : Modifiersopt Type VariableDeclarators semicolon'''
    p[0] = make_node([p[1], p[2], p[3], make_leaf(p[4])], "FieldDecl")

def p_VariableDeclarators(p):
	'''VariableDeclarators : VariableDeclarator
	| VariableDeclarators comma VariableDeclarator'''
	if len(p) > 2:
		p[0] = make_node(p[1].children+[p[3]], "VarDecls")
	else:
		p[0] = make_node([p[1]],"VarDecls")

def p_VariableDeclarator(p):
	'''VariableDeclarator : VariableDeclaratorId
	| VariableDeclaratorId equals VariableInitializer'''
	if len(p) > 2:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])
	else:
		p[0] = p[1]

def p_VariableDeclaratorId(p):
    '''VariableDeclaratorId : Identifier
	| VariableDeclaratorId ls rs'''
    if len(p) > 2:
        if p[1].children == []:
            p[0] = make_node([p[1], make_leaf(p[2]), make_leaf(p[3])], "VarDeclId")
        else:
            p[0] = make_node([make_leaf(p[2]), make_leaf(p[3])], "VarDeclId")
            p[0] = merge_node(p[1].children, p[0], "VarDeclId")
    else:
        p[0] = p[1]

def p_VariableInitializer(p):
    '''VariableInitializer : Expression
	| ArrayInitializer'''
    p[0] = p[1]

def p_MethodDeclaration(p):
    '''MethodDeclaration : MethodHeader MethodBody'''
    p[0] = make_node([p[1], p[2]], "MethodDecl")

def p_MethodHeader(p):
    '''MethodHeader : Modifiersopt Type MethodDeclarator Throwsopt
	| Modifiersopt void MethodDeclarator Throwsopt'''
    if p[2] == 'void':
        p[0] = make_node([p[1], make_leaf(p[2]), p[3], p[4]], "MethodHeader")
    else:
        p[0] = make_node([p[1], p[2], p[3], p[4]], "MethodHeader")

def p_MethodDeclarator(p):
    '''MethodDeclarator : Identifier lb FormalParameterListopt rb
	| MethodDeclarator ls rs'''
    if len(p) > 4:
        p[0] = make_node([p[1], make_leaf(p[2]), p[3], make_leaf(p[4])], "MethodDecl")
    else:
        p[0] = make_node([make_leaf(p[2]), make_leaf(p[3])], "SquareBraces")
        p[0] = merge_node(p[1].children, p[0], "MethodDecl")

def p_FormalParameterList(p):
    '''FormalParameterList : FormalParameter
	| FormalParameterList comma FormalParameter'''
    if len(p) > 2:
        p[0] = make_node([p[3]], "FormalParam")
        p[0] = merge_node(p[1].children, p[0], "FormalParamList")
    else:
        p[0] = p[1]

def p_FormalParameter(p):
	'''FormalParameter : Type VariableDeclaratorId'''
	if len(p[2].children)==0:
		p[0] = make_node([p[1], p[2]], "FormalParam")
	else:
		p[0] = merge_node([p[1]],p[2],"FormalParam")
	p[0] = make_node([p[0]], "FormalParam")	

def p_Throws(p):
    '''Throws : throws ClassTypeList'''
    p[0] = make_node([make_leaf(p[1]), p[2]], "Throws")

def p_ClassTypeList(p):
    '''ClassTypeList : ClassType
	| ClassTypeList comma ClassType'''
    if len(p) > 2:
        p[0] = make_node([p[3]], "ClassType")
        p[0] = merge_node(p[1].children, p[0], "ClassTypeList")
    else:
        p[0] = p[1]

def p_MethodBody(p):
    '''MethodBody : Block
	| semicolon'''
    if p[1] == ';':
        p[0] = make_leaf(p[1])
    else:
        p[0] = p[1]
    
def p_StaticInitializer(p):
    '''StaticInitializer : static Block'''
    p[0] = make_node([make_leaf(p[1]), p[2]], "StaticInit")

def p_ConstructorDeclaration(p):
    '''ConstructorDeclaration : Modifiersopt ConstructorDeclarator Throwsopt ConstructorBody'''
    p[0] = make_node([p[1], p[2], p[3], p[4]], "ConstDecl")

def p_ConstructorDeclarator(p):
    '''ConstructorDeclarator : SimpleName lb FormalParameterListopt rb'''
    p[0] = make_node([p[1], make_leaf(p[2]), p[3], make_leaf(p[4])], "ConstDecl")

def p_ConstructorBody(p):
    '''ConstructorBody : lp ExplicitConstructorInvocation BlockStatementsopt rp
	| lp BlockStatementsopt rp'''
    if len(p) > 4:
        p[0] = make_node([make_leaf(p[1]), p[2], p[3], make_leaf(p[4])], "ConstBody")
    else:
        p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ConstBody")

def p_ExplicitConstructorInvocation(p):
    '''ExplicitConstructorInvocation : this lb ArgumentListopt rb semicolon
	| super lb ArgumentListopt rb semicolon'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), make_leaf(p[5])], "ExplConstInvoc")

def p_InterfaceDeclaration(p):
    '''InterfaceDeclaration : Modifiersopt interface Identifier ExtendsInterfacesopt InterfaceBody'''
    p[0] = make_node([p[1], make_leaf(p[2]), p[3], p[4], p[5]], "InterfaceDecl")

def p_ExtendsInterfaces(p):
    '''ExtendsInterfaces : extends InterfaceType
	| ExtendsInterfaces comma InterfaceType'''
    if len(p) > 3:
        p[0] = make_node([p[3]], "InterfaceType")
        p[0] = merge_node(p[1].children, p[0], "ExtendsInterfaces")
    else:
        p[0] = make_node([make_leaf(p[1]), p[2]], "ExtendsInterfaces")

def p_InterfaceBody(p):
    '''InterfaceBody : lp InterfaceMemberDeclarationsopt rp'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "InterfaceBody")

def p_InterfaceMemberDeclarations(p):
    '''InterfaceMemberDeclarations : InterfaceMemberDeclaration
	| InterfaceMemberDeclarations InterfaceMemberDeclaration'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "InterfaceMemberDecl")
        p[0] = merge_node(p[1].children, p[0], "InterfaceMemberDecls")
    else:
        p[0] = p[1]

def p_InterfaceMemberDeclaration(p):
    '''InterfaceMemberDeclaration : ConstantDeclaration
	| AbstractMethodDeclaration'''
    p[0] = p[1]

def p_ConstantDeclaration(p):
    '''ConstantDeclaration : FieldDeclaration'''
    p[0] = p[1]

def p_AbstractMethodDeclaration(p):
    '''AbstractMethodDeclaration : MethodHeader semicolon'''
    p[0] = make_node([p[1], make_leaf(p[2])], "AbsMethodDecl")

def p_ArrayInitializer(p):
	'''ArrayInitializer : lp VariableInitializers commaopt rp
	| lp commaopt rp'''
	if len(p) > 4:
		p[0] = make_node([make_leaf(p[1]), p[2], p[3], make_leaf(p[4])], "ArrayInit")
	else:
		p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ArrayInit")

def p_VariableInitializers(p):
    '''VariableInitializers : VariableInitializer
	| VariableInitializers comma VariableInitializer'''
    if len(p) > 2:
        p[0] = make_node([p[3]], "VarInit")
        p[0] = merge_node(p[1].children, p[0], "VarInits")
    else:
        p[0] = p[1]

def p_Block(p):
    '''Block : lp BlockStatementsopt rp'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "Block")

def p_BlockStatements(p):
    '''BlockStatements : BlockStatement
	| BlockStatements BlockStatement'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "BlockStmt")
        p[0] = merge_node(p[1].children, p[0], "BlockStmts")
    else:
        p[0] = p[1]

def p_BlockStatement(p):
    '''BlockStatement : LocalVariableDeclarationStatement
	| Statement'''
    p[0] = p[1]

def p_LocalVariableDeclarationStatement(p):
    '''LocalVariableDeclarationStatement : LocalVariableDeclaration semicolon'''
    p[0] = make_node([p[1], make_leaf(p[2])], "LocalVarDeclStmt")

def p_LocalVariableDeclaration(p):
    '''LocalVariableDeclaration : Type VariableDeclarators'''
    p[0] = make_node([p[1], p[2]], "LocalVarDecl")

def p_Statement(p):
    '''Statement : StatementWithoutTrailingSubstatement
	| LabeledStatement
	| IfThenStatement
	| IfThenElseStatement
	| WhileStatement
	| ForStatement'''
    p[0] = p[1]

def p_StatementNoShortIf(p):
    '''StatementNoShortIf : StatementWithoutTrailingSubstatement
	| LabeledStatementNoShortIf
	| IfThenElseStatementNoShortIf
	| WhileStatementNoShortIf
	| ForStatementNoShortIf'''
    p[0] = p[1]

def p_StatementWithoutTrailingSubstatement(p):
    '''StatementWithoutTrailingSubstatement : Block
	| EmptyStatement
	| ExpressionStatement
	| SwitchStatement
	| DoStatement
	| BreakStatement
	| ContinueStatement
	| ReturnStatement
	| SynchronizedStatement
	| ThrowStatement
	| TryStatement'''
    p[0] = p[1]

def p_EmptyStatement(p):
    '''EmptyStatement : semicolon'''
    p[0] = make_leaf(p[1])

def p_LabeledStatement(p):
    '''LabeledStatement : Identifier colon Statement'''
    p[0] = make_node([p[1], make_leaf(p[2]), p[3]], "LabeledStmt")

def p_LabeledStatementNoShortIf(p):
    '''LabeledStatementNoShortIf : Identifier colon StatementNoShortIf'''
    p[0] = make_node([p[1], make_leaf(p[2]), p[3]], "LabeledStmtNoShortIf")

def p_ExpressionStatement(p):
    '''ExpressionStatement : StatementExpression semicolon'''
    p[0] = make_node([p[1], make_leaf(p[2])], "ExpStmt")

def p_StatementExpression(p):
    '''StatementExpression : Assignment
	| PreIncrementExpression
	| PreDecrementExpression
	| PostIncrementExpression
	| PostDecrementExpression
	| MethodInvocation
	| ClassInstanceCreationExpression'''
    p[0] = p[1]

def p_IfThenStatement(p):
    '''IfThenStatement : if lb Expression rb Statement'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5]], "IfThenStmt")

def p_IfThenElseStatement(p):
    '''IfThenElseStatement : if lb Expression rb StatementNoShortIf else Statement'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5], make_leaf(p[6]), p[7]], "IfThenElseStmt")

def p_IfThenElseStatementNoShortIf(p):
    '''IfThenElseStatementNoShortIf : if lb Expression rb StatementNoShortIf else StatementNoShortIf'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5], make_leaf(p[6]), p[7]], "IfThenElseStmtNoShortIf")

def p_SwitchStatement(p):
    '''SwitchStatement : switch lb Expression rb SwitchBlock'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5]], "SwitchStmt")

def p_SwitchBlock(p):
    '''SwitchBlock : lp SwitchBlockStatementGroups SwitchLabelsopt rp
	| lp SwitchLabelsopt rp'''
    if len(p) > 4:
        p[0] = make_node([make_leaf(p[1]), p[2], p[3], make_leaf(p[4])], "SwitchBlock")
    else:
        p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "SwitchBlock")

def p_SwitchBlockStatementGroups(p):
    '''SwitchBlockStatementGroups : SwitchBlockStatementGroup
	| SwitchBlockStatementGroups SwitchBlockStatementGroup'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "SwitchBlockStmtGrp")
        p[0] = merge_node(p[1].children, p[0], "SwitchBlockStmtGrps")
    else:
        p[0] = p[1]

def p_SwitchBlockStatementGroup(p):
    '''SwitchBlockStatementGroup : SwitchLabels BlockStatements'''
    p[0] = make_node([p[1], p[2]], "SwitchBlockStmtGrp")

def p_SwitchLabels(p):
    '''SwitchLabels : SwitchLabel
	| SwitchLabels SwitchLabel'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "SwitchLabel")
        p[0] = merge_node(p[1].children, p[0], "SwitchLabels")
    else:
        p[0] = p[1]

def p_SwitchLabel(p):
    '''SwitchLabel : case ConstantExpression colon
	| default colon'''
    if len(p) > 3:
        p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "SwitchLabel")
    else:
        p[0] = make_node([make_leaf(p[1]), make_leaf(p[2])], "SwitchLabel")

def p_WhileStatement(p):
    '''WhileStatement : while lb Expression rb Statement'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5]], "WhileStmt")

def p_WhileStatementNoShortIf(p):
    '''WhileStatementNoShortIf : while lb Expression rb StatementNoShortIf'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5]], "WhileStmtNoShortIf")

def p_DoStatement(p):
    '''DoStatement : do Statement while lb Expression rb semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3]), make_leaf(p[4]), p[5], make_leaf(p[6]), make_leaf(p[7])], "DoStmt")

def p_finals(p):
    '''finals : finals final
    | final'''
    if len(p) > 2:
        p[0] = make_node([p[1], make_leaf(p[2])], "Finals")
    else:
        p[0] = make_leaf(p[1])

def p_ForStatement(p):
    '''ForStatement : for lb Type VariableDeclaratorId colon Expression rb Statement
    | for lb finals Type VariableDeclaratorId colon Expression rb Statement
    | for lb ForInitopt semicolon Expressionopt semicolon ForUpdateopt rb Statement'''
    if p[5] == ':':
        p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], p[4], make_leaf(p[5]), p[6], make_leaf(p[7]), p[8]], "ForStmt")
    elif p[6] == ':':
        if p[3].children != []:
            p[0] = make_node([make_leaf(p[1]), make_leaf(p[2])], "ForStmt")
            p[0] = merge_node(p[0].children, p[3], "ForStmt")
            p[0] = make_node(p[0].children+[p[4], p[5], make_leaf(p[6]), p[7], make_leaf(p[8]), p[9]], "ForStmt")
        else:
            p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], p[4], p[5], make_leaf(p[6]), p[7], make_leaf(p[8]), p[9]], "ForStmt")
    else:
        p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5], make_leaf(p[6]), p[7], make_leaf(p[8]), p[9]], "ForStmt")

def p_ForStatementNoShortIf(p):
    '''ForStatementNoShortIf : for lb Type VariableDeclaratorId colon Expression rb StatementNoShortIf
    | for lb finals Type VariableDeclaratorId colon Expression rb StatementNoShortIf
    | for lb ForInitopt semicolon Expressionopt semicolon ForUpdateopt rb StatementNoShortIf'''
    if p[5] == ':':
        p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], p[4], make_leaf(p[5]), p[6], make_leaf(p[7]), p[8]], "ForStmtNoShortIf")
    elif p[6] == ':':
        if p[3].children != []:
            p[0] = make_node([make_leaf(p[1]), make_leaf(p[2])], "ForStmtNoShortIf")
            p[0] = merge_node(p[0].children, p[3], "ForStmtNoShortIf")
            p[0] = make_node(p[0].children+[p[4], p[5], make_leaf(p[6]), p[7], make_leaf(p[8]), p[9]], "ForStmtNoShortIf")
        else:
            p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], p[4], p[5], make_leaf(p[6]), p[7], make_leaf(p[8]), p[9]], "ForStmtNoShortIf")
    else:
        p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5], make_leaf(p[6]), p[7], make_leaf(p[8]), p[9]], "ForStmtNoShortIf")

def p_ForInit(p):
    '''ForInit : StatementExpressionList
	| LocalVariableDeclaration'''
    p[0] = p[1]

def p_ForUpdate(p):
    '''ForUpdate : StatementExpressionList'''
    p[0] = p[1]

def p_StatementExpressionList(p):
    '''StatementExpressionList : StatementExpression
	| StatementExpressionList comma StatementExpression'''
    if len(p) > 2:
        p[0] = make_node([p[3]], "StmtExp")
        p[0] = merge_node(p[1].children, p[0], "StmtExpList")
    else:
        p[0] = p[1]

def p_BreakStatement(p):
    '''BreakStatement : break Identifieropt semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "BreakStmt")

def p_ContinueStatement(p):
    '''ContinueStatement : continue Identifieropt semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ContinueStmt")

def p_ReturnStatement(p):
    '''ReturnStatement : return Expressionopt semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ReturnStmt")

def p_ThrowStatement(p):
    '''ThrowStatement : throw Expression semicolon'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "ThrowsStmt")

def p_SynchronizedStatement(p):
    '''SynchronizedStatement : synchronized lb Expression rb Block'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5]], "SynchStmt")

def p_TryStatement(p):
	'''TryStatement : try Block Catches
	| try Block Catchesopt Finally'''
	if len(p) > 4:
		p[0] = make_node([make_leaf(p[1]), p[2], p[3], p[4]], "TryStmt")
	else:
		p[0] = make_node([make_leaf(p[1]), p[2], p[3]], "TryStmt")

def p_Catches(p):
    '''Catches : CatchClause
	| Catches CatchClause'''
    if len(p) > 2:
        p[0] = make_node([p[2]], "CatchClause")
        p[0] = merge_node(p[1].children, p[0], "Catches")
    else:
        p[0] = p[1]

def p_CatchClause(p):
    '''CatchClause : catch lb FormalParameter rb Block'''
    p[0] = make_node([make_leaf(p[1]), make_leaf(p[2]), p[3], make_leaf(p[4]), p[5]], "CatchClause")

def p_Finally(p):
    '''Finally : finally Block'''
    p[0] = make_node([make_leaf([p[1]]), p[2]], "Finally")

def p_Primary(p):
    '''Primary : PrimaryNoNewArray
	| ArrayCreationExpression'''
    p[0] = p[1]

def p_PrimaryNoNewArray(p):
    '''PrimaryNoNewArray : Literal
	| this
	| lb Expression rb
	| ClassInstanceCreationExpression
	| FieldAccess
	| MethodInvocation
	| ArrayAccess'''
    if len(p) == 2:
        if p[1] == 'this':
            p[0] = make_leaf(p[1])
        else:
            p[0] = p[1]
    else:
        p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "PrimaryNoNewArr")

def p_ClassInstanceCreationExpression(p):
    '''ClassInstanceCreationExpression : new ClassType lb ArgumentListopt rb'''
    p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3]), p[4], make_leaf(p[5])], "ClassInstCreationExp")

def p_ArgumentList(p):
    '''ArgumentList : Expression
	| ArgumentList comma Expression'''
    if len(p) > 2:
        p[0] = make_node([p[3]], "Expression")
        p[0] = merge_node(p[1].children, p[0], "ArgList")
    else:
        p[0] = p[1]

def p_ArrayCreationExpression(p):
	'''ArrayCreationExpression : new PrimitiveType DimExprs Dimsopt
	| new ClassOrInterfaceType DimExprs Dimsopt'''
	p[0] = make_node([make_leaf(p[1]), p[2], p[3], p[4]], "ArrayCreationExp")

def p_DimExprs(p):
	'''DimExprs : DimExpr
	| DimExprs DimExpr'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node([p[2]], "DimExpr")
		p[0] = merge_node(p[1].children, p[0], "DimExprs")

def p_DimExpr(p):
	'''DimExpr : ls Expression rs'''
	p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3])], "DimExpr")

def p_Dims(p):
	'''Dims : ls rs
	| Dims ls rs'''
	if len(p)==3:
		p[0] = make_node([make_leaf(p[1]), make_leaf(p[2])], "Dims")
	else:
		p[0] = make_node([make_leaf(p[2]), make_leaf(p[3])], "SquareBraces")
		p[0] = merge_node(p[1].children, p[0], "SquareBraces")

def p_FieldAccess(p):
	'''FieldAccess : Primary dot Identifier
	| super dot Identifier'''
	if p[1]=="super":
		p[0] = make_node_hierachy_deep(make_leaf(p[1]), p[3])
	else:
		p[0] = make_node_hierachy_deep(p[1], p[3])

def p_MethodInvocation(p):
	'''MethodInvocation : Name1 lb ArgumentListopt rb
	| Primary dot Identifier lb ArgumentListopt rb
	| super dot Identifier lb ArgumentListopt rb'''
	if len(p)==5:
		p[0] = make_node([p[1], make_leaf(p[2]), p[3], make_leaf(p[4])], "MethodInvoc")
	elif p[1]=="super":
		p[0] = make_node_hierachy_deep(make_leaf(p[1]), p[3])
		p[0] = make_node([p[0], make_leaf(p[4]), p[5], make_leaf(p[6])], "MethodInvoc")
	else:
		p[0] = make_node_hierachy_deep(p[1], p[3])
		p[0] = make_node([p[0], make_leaf(p[4]), p[5], make_leaf(p[6])], "MethodInvoc")

def p_ArrayAccess(p):
    '''ArrayAccess : Name1 ls Expression rs
    | PrimitiveType lb Name1 ls Expression rs rb
	| PrimaryNoNewArray ls Expression rs'''
    if len(p) >5:
        p[0]= make_node_hierachy(make_node_hierachy(make_node_hierachy(make_node_hierachy(p[1],p[3]),make_leaf(p[4])),p[5]),make_leaf(p[6]))
    else:
        p[0] = make_node([p[1], make_leaf(p[2]), p[3], make_leaf(p[4])], "ArrayAccess")

def p_PostfixExpression(p):
	'''PostfixExpression : Primary
	| Name
	| PostIncrementExpression
	| PostDecrementExpression'''
	p[0] = p[1]

def p_PostIncrementExpression(p):
	'''PostIncrementExpression : PostfixExpression plusplus'''
	p[0] = make_node_hierachy(p[1], make_leaf(p[2]))

def p_PostDecrementExpression(p):
	'''PostDecrementExpression : PostfixExpression minusminus'''
	p[0] = make_node_hierachy(p[1], make_leaf(p[2]))

def p_UnaryExpression(p):
	'''UnaryExpression : PreIncrementExpression
	| PreDecrementExpression
	| plus UnaryExpression
	| minus UnaryExpression
	| UnaryExpressionNotPlusMinus'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_leaf(p[1]), p[2])

def p_PreIncrementExpression(p):
	'''PreIncrementExpression : plusplus UnaryExpression'''
	p[0] = make_node_hierachy(make_leaf(p[1]), p[2])

def p_PreDecrementExpression(p):
	'''PreDecrementExpression : minusminus UnaryExpression'''
	p[0] = make_node_hierachy(make_leaf(p[1]), p[2])

def p_UnaryExpressionNotPlusMinus(p):
	'''UnaryExpressionNotPlusMinus : PostfixExpression
	| tilda UnaryExpression
	| not UnaryExpression
	| CastExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_leaf(p[1]), p[2])

def p_CastExpression(p):
	'''CastExpression : lb PrimitiveType Dimsopt rb UnaryExpression
	| lb Expression rb UnaryExpressionNotPlusMinus
	| lb Name1 Dims rb UnaryExpressionNotPlusMinus'''
	if len(p)==5:
		p[0] = make_node([make_leaf(p[1]), p[2], make_leaf(p[3]), p[4]], "CastExp")
	else:
		p[0] = make_node([make_leaf(p[1]), p[2], p[3], make_leaf(p[4]), p[5]], "CastExp")

def p_MultiplicativeExpression(p):
	'''MultiplicativeExpression : UnaryExpression
	| MultiplicativeExpression multiply UnaryExpression
	| MultiplicativeExpression divide UnaryExpression
	| MultiplicativeExpression mod UnaryExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_AdditiveExpression(p):
	'''AdditiveExpression : MultiplicativeExpression
	| AdditiveExpression plus MultiplicativeExpression
	| AdditiveExpression minus MultiplicativeExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_ShiftExpression(p):
	'''ShiftExpression : AdditiveExpression
	| ShiftExpression leftshift AdditiveExpression
	| ShiftExpression rightshift AdditiveExpression
	| ShiftExpression doubleright AdditiveExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_RelationalExpression(p):
	'''RelationalExpression : ShiftExpression
	| RelationalExpression lt ShiftExpression
	| RelationalExpression gt ShiftExpression
	| RelationalExpression ltequals ShiftExpression
	| RelationalExpression gtequals ShiftExpression
	| RelationalExpression instanceof ReferenceType'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_EqualityExpression(p):
	'''EqualityExpression : RelationalExpression
	| EqualityExpression equalsequals RelationalExpression
	| EqualityExpression notequals RelationalExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_AndExpression(p):
	'''AndExpression : EqualityExpression
	| AndExpression and EqualityExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_ExclusiveOrExpression(p):
	'''ExclusiveOrExpression : AndExpression
	| ExclusiveOrExpression exor AndExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_InclusiveOrExpression(p):
	'''InclusiveOrExpression : ExclusiveOrExpression
	| InclusiveOrExpression or ExclusiveOrExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_ConditionalAndExpression(p):
	'''ConditionalAndExpression : InclusiveOrExpression
	| ConditionalAndExpression andand InclusiveOrExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_ConditionalOrExpression(p):
	'''ConditionalOrExpression : ConditionalAndExpression
	| ConditionalOrExpression oror ConditionalAndExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3])

def p_ConditionalExpression(p):
	'''ConditionalExpression : ConditionalOrExpression
	| ConditionalOrExpression question Expression colon ConditionalExpression'''
	if len(p)==2:
		p[0] = p[1]
	else:
		p[0] = make_node_hierachy(make_node_hierachy(make_node_hierachy(make_leaf(p[2]), p[1]), p[3]), p[5])

def p_AssignmentExpression(p):
	'''AssignmentExpression : ConditionalExpression
	| Assignment'''
	p[0] = p[1]

def p_Assignment(p):
	'''Assignment : LeftHandSide AssignmentOperator AssignmentExpression'''
	p[0] = make_node_hierachy(make_node_hierachy(p[2], p[1]), p[3])

def p_LeftHandSide(p):
	'''LeftHandSide : Name
	| FieldAccess
	| ArrayAccess'''
	p[0] = p[1]

def p_AssignmentOperator(p):
	'''AssignmentOperator : equals
	| multiplyequals
	| divideequals
	| modequals
	| plusequals
	| minusequals
	| leftshiftequals
	| rightshiftequals
	| triplerightequals
	| andequals
	| exorequals
	| orequals'''
	p[0] = make_leaf(p[1])

def p_Expression(p):
	'''Expression : AssignmentExpression'''
	p[0] = p[1]

def p_ConstantExpression(p):
	'''ConstantExpression : Expression'''
	p[0] = p[1]

def p_ArgumentListopt(p):
	'''ArgumentListopt : ArgumentList
	| empty'''
	p[0] = p[1]

def p_BlockStatementsopt(p):
	'''BlockStatementsopt : BlockStatements
	| empty'''
	p[0] = p[1]

def p_Catchesopt(p):
	'''Catchesopt : Catches
	| empty'''
	p[0] = p[1]

def p_ClassBodyDeclarationsopt(p):
	'''ClassBodyDeclarationsopt : ClassBodyDeclarations
	| empty'''
	p[0] = p[1]

def p_Dimsopt(p):
	'''Dimsopt : Dims
	| empty'''
	p[0] = p[1]

def p_Expressionopt(p):
	'''Expressionopt : Expression
	| empty'''
	p[0] = p[1]

def p_ExtendsInterfacesopt(p):
	'''ExtendsInterfacesopt : ExtendsInterfaces
	| empty'''
	p[0] = p[1]

def p_ForInitopt(p):
	'''ForInitopt : ForInit
	| empty'''
	p[0] = p[1]

def p_FormalParameterListopt(p):
	'''FormalParameterListopt : FormalParameterList
	| empty'''
	p[0] = p[1]

def p_ForUpdateopt(p):
	'''ForUpdateopt : ForUpdate
	| empty'''
	p[0] = p[1]

def p_Identifieropt(p):
	'''Identifieropt : Identifier
	| empty'''
	p[0] = p[1]

def p_ImportDeclarationsopt(p):
	'''ImportDeclarationsopt : ImportDeclarations
	| empty'''
	p[0] = p[1]

def p_InterfaceMemberDeclarationsopt(p):
	'''InterfaceMemberDeclarationsopt : InterfaceMemberDeclarations
	| empty'''
	p[0] = p[1]

def p_Interfacesopt(p):
	'''Interfacesopt : Interfaces
	| empty'''
	p[0] = p[1]

def p_Modifiersopt(p):
	'''Modifiersopt : Modifiers
	| empty'''
	p[0] = p[1]

def p_commaopt(p):
	'''commaopt : comma
	| empty'''
	if p[1] == ',':
		p[0] = make_leaf(p[1])
	else:
		p[0] = p[1]

def p_PackageDeclarationopt(p):
	'''PackageDeclarationopt : PackageDeclaration
	| empty'''
	p[0] = p[1]

def p_Superopt(p):
	'''Superopt : Super
	| empty'''
	p[0] = p[1]

def p_SwitchLabelsopt(p):
	'''SwitchLabelsopt : SwitchLabels
	| empty'''
	p[0] = p[1]

def p_Throwsopt(p):
	'''Throwsopt : Throws
	| empty'''
	p[0] = p[1]

def p_TypeDeclarationsopt(p):
	'''TypeDeclarationsopt : TypeDeclarations
	| empty'''
	p[0] = p[1]

def p_Identifier(p):
    """Identifier : IDENTIFIER"""
    p[0] = make_leaf(p[1])  

def p_empty(p):
    '''empty : '''
    p[0] = None 

parser = yacc.yacc()
f = open(ifile,'r')
string = f.read()
f.close()
op = parser.parse(string)
# def pt(op):
#     if(op==None):
#         return
#     try:
#         print(op.label)
#     except:
#         pass
#     try:        
#         for k in op.children:
#             pt(k)
#     except:
#         pass
if flag==1:
    print(dic["error"],end="")
if dic["error"]=="":
    clean_ast(op)
    printdot(op)
    cmd="dot -Tps graph.dot -o " + str(ofile)
    os.system(cmd)