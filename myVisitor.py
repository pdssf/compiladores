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
    func_name = ctx.ID().getText()
    tyype = ctx.tyype().getText()

    if(tyype == 'int'):
        print('define i32 @' + func_name, end = '(')
    elif (tyype == 'float'):
        print('define float @' + func_name, end = '(')
    elif (tyype == 'boolean'):
        print('define i1 @' + func_name, end = '(')
    else:
        print('erou')
        exit(1)

    