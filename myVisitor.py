from antlr4 import *
from CymbolVisitor import CymbolVisitor
from CymbolParser import CymbolParser

class MyVisitor(CymbolVisitor):
    #dicionario pra guardar funções
    funcoes = {}

    #dicionário de variáveis
    variaveis = {}

    #dicionário de parâmetros
    parametros = {}

# Visit a parse tree produced by CymbolParser#funcDecl.
def visitFuncDecl(self, ctx:CymbolParser.FuncDeclContext):
    #elementos iniciais: nome da funcao, tipo, e lista de parametros
    func_name = ctx.ID().getText() 
    tyype = ctx.tyype().getText()
    parametrslist = ctx.paramTypeList()

    if(tyype == 'int'):
        print('define i32 @' + func_name, end = '(')
    elif (tyype == 'float'):
        print('define float @' + func_name, end = '(')
    elif (tyype == 'boolean'):
        print('define i1 @' + func_name, end = '(')
    else:
        print('erou')
        exit(1)

    i = 0
    if(parametrslist != None):
        listaParam = parametrslist.paramType()
        for parametro in listaParam:
            if(i!=0):
                print(' ,')
            if(parametro.tyype() == 'int'):
                dicionarioParam[func_name].append('i32')
                print('i32', end = '')
            elif(parametro.tyype() == 'float'):
                dicionarioParam[func_name].append('float')
                print('float', end = '')
            elif(parametro.tyype() == 'boolean'):
                dicionarioParam[func_name].append('boolean')
                print('boolean', end = '')
            else:
                print('erou')
                exit(1)

    print(') #0 {')

    print('}') #fim da funçao
        
            