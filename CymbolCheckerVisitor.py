from antlr4 import *
from autogen.CymbolParser import CymbolParser 
from autogen.CymbolVisitor import CymbolVisitor

funcoes = {}
#dicionário de variáveis
variaveis = {}
#dicionário de parâmetros
parametros = {}
#dicionario de variaveis globais
globais = {}



class Type:
	INT = "int"
	FLOAT = "float"
	BOOL = "boolean"

class CymbolCheckerVisitor(CymbolVisitor):
	def __init__(self):
		self.estouDentro_daFuncao = 0
		self.count = 0

	def visitIntExpr(self, ctx:CymbolParser.IntExprContext):
		print("visting "+Type.INT)
		return Type.INT

	def visitFloatExpr(self, ctx:CymbolParser.FloatExprContext):
		return Type.FLOAT

	def visitFormTypeBoolean(self, ctx:CymbolParser.BooleanExprContext):
		return Type.BOOL

	def visitVarDecl(self, ctx:CymbolParser.VarDeclContext):#desafio: pegar de forma correta dentro das func
		var_name = ctx.ID().getText()
		tyype = ctx.tyype().getText()
		expr = ctx.expr()

		if(self.estouDentro_daFuncao == 0):
			globais[var_name] = tyype #salvo a variavel e seu tipo
			print('@'+var_name, end = '= ')
   
			if (expr == None):
				print('commom', end = ' ')
				if(tyype == 'int'):
					expr = '0'
				elif(tyype == 'float'):
					expr = '0.000000e+00'
				else:
					expr = 'false'
			else:
				expr = expr.getText()

			if(tyype == 'int'):
				print('global i32 '+ expr, end = ', ')
			elif(tyype == 'float'):
				print('global float '+ expr, end = ', ')
			elif(tyype == 'boolean'):
				print('global i1 '+ expr, end = ', ')
			print('align 4')
		else:
			self.estouDentro_daFuncao = 0
			self.count += 1
			if(tyype == 'int'):
				print('%' + str(self.count) +  '= alloca i32, align 4')
			elif(tyype == 'float'):
				print('%' + str(self.count) +  '= alloca float, align 4')
			else:
				print('%' + str(self.count) + '= alloca i1, align 4')
  		
	def visitFuncDecl(self, ctx:CymbolParser.FuncDeclContext):
		#elementos iniciais: nome da funcao, tipo, e lista de parametros
		func_name = ctx.ID().getText() 
		tyype = ctx.tyype().getText()
		parametrslist = ctx.paramTypeList()
		self.count = 0

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
			parametros[func_name]= listaParam
			tamanho = len(listaParam)
			for cursor in listaParam:
				self.count += 1;
				if(i!=0):
					print(',', end = ' ')
				if(i < tamanho):
					if ('int' in cursor.getText()):
						print('i32', end = '')
					elif('float' in cursor.getText()):
						print('float', end = '')
					else:
						print('i1', end = '')
				i = i+1;	
  
		print(') #0 {')
		self.estouDentro_daFuncao= 999;
		self.visitChildren(ctx)
		print('}') #fim da funçao



	def visitAddSubExpr(self, ctx:CymbolParser.AddSubExprContext):
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)

		if left == Type.INT and right == Type.INT:
			result = Type.INT
		else:
			reult = Type.VOID
			print("Mensagem de erro 3...")
			exit()
		
		print("addition or subtraction of " + left + " " + right + " that results in a " + result)
		return result



	def aggregateResult(self, aggregate:Type, next_result:Type):
		return next_result if next_result != None else aggregate


	#clang -S -emit-llvm test_clang.c