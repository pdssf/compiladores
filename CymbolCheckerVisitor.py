from antlr4 import *
from autogen.CymbolParser import CymbolParser 
from autogen.CymbolVisitor import CymbolVisitor

funcoes = {}
#dicionário de nro variáveis --- %i
variaveis = {}
#dicionário de parâmetros
parametros = {}
#dicionario de variaveis globais
globais = {}
#dicionario de valores variaveis
valores_variaveis = {}

class Type:
	INT = "int"
	FLOAT = "float"
	BOOL = "boolean"

class CymbolCheckerVisitor(CymbolVisitor):
	def __init__(self):
		self.estouDentro_daFuncao = 0
		self.count = 0
		self.nome_func_atual = None
		
	def visitIntExpr(self, ctx:CymbolParser.IntExprContext):
		return int(ctx.INT().getText())

	def visitNotExpr(self, ctx:CymbolParser.NotExprContext):
		return self.visitChildren(ctx)

	def visitFloatExpr(self, ctx:CymbolParser.FloatExprContext):
		return float(ctx.FLOAT().getText())

	def visitFormTypeBoolean(self, ctx:CymbolParser.BooleanExprContext):
		return Type.BOOL

	def visitVarDecl(self, ctx:CymbolParser.VarDeclContext):#desafio: pegar de forma correta dentro das func
		var_name = ctx.ID().getText()
		tyype = ctx.tyype().getText()
		expr = ctx.expr()
		func_name = self.nome_func_atual

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
			#self.estouDentro_daFuncao = 0
			self.count += 1
			if(tyype == 'int'):
				print('%' + str(self.count) +  '= alloca i32, align 4')
				variaveis[func_name,var_name] = self.count
			elif(tyype == 'float'):
				print('%' + str(self.count) +  '= alloca float, align 4')
				variaveis[func_name,var_name] = self.count
			else:
				print('%' + str(self.count) + '= alloca i1, align 4')
				variaveis[func_name,var_name] = self.count

			if (expr != None):
				if(tyype == 'int'):
					if(('+' in expr.getText()) or ('-' in expr.getText())):
						self.visitChildren(ctx)
					else:	
						print('store i32 ' + expr.getText() + ', i32* %'+ str(self.count) + ', align 4')
						valores_variaveis[func_name,var_name] = int(expr.getText())
						#print('Nome da func :' + str(func_name) + 'ID da Variavel :' + var_name + 'Valor :', int(expr.getText()))
				elif(tyype == 'float'):
					if(('+' in expr.getText()) or ('-' in expr.getText())):
    						self.visitChildren(ctx)
					else:
						valores_variaveis[func_name,var_name] = float(expr.getText())
						print('store float ' + expr.getText(), ', float* %'+str(self.count) + ', align 4')
				else:
					valores_variaveis[func_name,var_name] = str(expr.getText())
					print('store i1 '+ expr.getText(), ', i1* %'+str(self.count) + ', align 4')
				
			  		
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
				self.count += 1
				if(i!=0):
					print(',', end = ' ')
				if(i < tamanho):
					if ('int' in cursor.getText()):
						print('i32', end = '')
					elif('float' in cursor.getText()):
						print('float', end = '')
					else:
						print('i1', end = '')
				i = i+1  
			print(') #0 {')
			for p in listaParam:
				self.count += 1
				if ('int' in p.getText()):
					print('%' + str(self.count) + ' = alloca i32, align 4')
					variaveis[func_name,p.ID().getText()] = self.count
					#print('Nome func :' + func_name + 'ID :' + p.ID().getText())
				elif('float' in p.getText()):
					print('%' + str(self.count) + ' = alloca float, align 4')
					variaveis[func_name,p.ID().getText()] = self.count
				else:
					print('%' + str(self.count) + ' = alloca i1, align 4')
					variaveis[func_name,p.ID().getText()] = self.count
				
			#store i32 %1, i32* %5, align 4
			j =0

			for p in listaParam:
				if ('int' in p.getText()):
					print('store i32 %' + str(j) + ', i32* %'+ str(i) + ', align 4')
				elif('float' in p.getText()):
					print('store float %' + str(j) + ', float* %'+ str(i) + ', align 4')
				else:
					print('store i1 %' + str(j) + ', i1* %'+ str(i) + ', align 4')

				j += 1
				i += 1
		else:
			print(') #0 {')

		self.estouDentro_daFuncao= 999
		self.nome_func_atual = func_name
		self.visitChildren(ctx)
		print('}') #fim da funçao

	def visitAddSubExpr(self, ctx:CymbolParser.AddSubExprContext):
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)
		nome_func = self.nome_func_atual
		#print('nome func ' + str(nome_func))
		exprOperador = ctx.op.text
		if ('+' == exprOperador):
			#Caso 1 : Duas constantes
			if((left != None) and (right != None)):
				result = left + right
				print('store i32 ' + str(result) + ', i32* %'+ str(self.count)+ ', align 4')
			
			#Caso 2 : Um dos valores é constante o outro é de uma variavel
			#define i32 @soma() #0
 			# %1 = alloca i32, align 4
  			#%2 = alloca i32, align 4
  			#store i32 10, i32* %1, align 4
 			#%3 = load i32, i32* %1, align 4
  			#%4 = add nsw i32 %3, 150
 			#store i32 %4, i32* %2, align 4 --- Falta esse
			#ret i32 1500

			elif((left == None) or (right == None)):
				# se um dos operandos for uma variável,left ou right estara com seu valor NONE
				# Logo é preciso saber o nome da variável para buscar o seu valor na estrutura de 
				# dicionario ja criada valores_variaveis[ctx.expr().getText(),str(ctx.expr())]
				if(left == None):
					self.count += 1
					exprIDLEFT = str(ctx.expr()[0].ID())
					nro_variavel = variaveis[nome_func,exprIDLEFT]
					result = valores_variaveis[str(nome_func),str(exprIDLEFT)] + right
					print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
					#print('nome variable  :' + str(nro_variavel))
					self.count += 1
					print('%' + str(self.count) + '= add nsw i32 %' + str(self.count - 1) + ',' + str(result))
					#print('store i32 %' +str(self.))
				else:
					self.count += 1
					exprIDRIGHT = str(ctx.expr()[1].ID())
					nro_variavel = variaveis[nome_func,exprIDRIGHT]
					result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] + left
					print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
					#print('nome variable  :' + str(nro_variavel))
					self.count += 1
					print('%' + str(self.count) + '= add nsw i32 %' + str(self.count - 1) + ',' + str(result))
					#print('store i32 %' +str(self.))
				#Caso 3 : Os dois valores são variáveis
				#else:
		else:
			result = left - right
			print('store i32 ' + str(result) + ', i32* %'+ str(self.count)+ ', align 4')

		#print('toma aqui teu resultado', result)
		return self.visitChildren(ctx)

	def aggregateResult(self, aggregate:Type, next_result:Type):
		return next_result if next_result != None else aggregate

#%13 = load i32, i32* %7, align 4
#  ret i32 %13
    # Visit a parse tree produced by CymbolParser#returnStat.
	'''def visitReturnStat(self, ctx:CymbolParser.ReturnStatContext):
		retorno = variaveis[ctx.expr().getText(),str(ctx.expr())]
		print('%' + str(self.count) + '= load i32, i32* %'+ str(retorno) + ', align 4')
		print('ret i32' + str(self.count))
		#return self.visitChildren(ctx)'''
	#clang -S -emit-llvm test_clang.c
 
 #not
 #and e or
 #igual e diferente
 #Maior e menor
 #>= <=