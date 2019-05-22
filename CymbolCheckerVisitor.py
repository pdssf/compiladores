from antlr4 import *
from autogen.CymbolParser import CymbolParser 
from autogen.CymbolVisitor import CymbolVisitor
import struct


#dicionário de numero e tipo das variáveis --- (%i, tyype)
variaveis = {}
#dicionário de parâmetros
parametros = {}
#dicionario de variaveis globais
globais = {}


def float_to_hex(f):
	return hex(struct.unpack('<I', struct.pack('<f', f))[0])
	
class Type:
	INT = "int"
	FLOAT = "float"
	BOOL = "boolean"

class CymbolCheckerVisitor(CymbolVisitor):
	def __init__(self):
		self.estouDentro_daFuncao = 0
		self.count = 0
		self.nome_func_atual = None
		self.nome_variavel_atual = None
		self.tipo_atual = None
		self.assign_que_ira_receber_valor_expr = None
	
	def count_add(self):
		self.count += 1
	
	def visitIntExpr(self, ctx:CymbolParser.IntExprContext):
		return int(ctx.INT().getText())

	def visitFloatExpr(self, ctx:CymbolParser.FloatExprContext):
		return float(ctx.FLOAT().getText())

	def visitFormTypeBoolean(self, ctx:CymbolParser.BooleanExprContext):
		return Type.BOOL

	def visitAssignStat(self, ctx:CymbolParser.AssignStatContext):
		#A variável que recebera o valor de uma expressão
		self.assign_que_ira_receber_valor_expr = ctx.ID().getText()
		return self.visitChildren(ctx)

	def visitVarDecl(self, ctx:CymbolParser.VarDeclContext):
		var_name = ctx.ID().getText()
		tyype = ctx.tyype().getText()
		expr = ctx.expr()
		func_name = self.nome_func_atual

		#GLOBAL
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
				print('global float '+ str(float_to_hex(float(expr))), end = ', ')
			elif(tyype == 'boolean'):
				print('global i1 '+ expr, end = ', ')
			print('align 4')
		else:
			self.count += 1
			if(tyype == 'int'):
				print('%' + str(self.count) +  '= alloca i32, align 4')
				variaveis[func_name,var_name] = (self.count,tyype)
				self.nome_variavel_atual = var_name
			elif(tyype == 'float'):
				print('%' + str(self.count) +  '= alloca float, align 4')
				variaveis[func_name,var_name] = (self.count,tyype)
				self.nome_variavel_atual = var_name
			else:
				print('%' + str(self.count) + '= alloca i1, align 4')
				variaveis[func_name,var_name] = (self.count,tyype)
				self.nome_variavel_atual = var_name
			if (expr != None):
				if(tyype == 'int'):
					if(('+' in expr.getText()) or ('-' in expr.getText())):
						self.visitChildren(ctx)
					elif(('*' in expr.getText()) or ('/' in expr.getText())):
						self.visitChildren(ctx)
					else:	
						print('store i32 ' + expr.getText() + ', i32* %'+ str(self.count) + ', align 4')
				elif(tyype == 'float'):
					if(('+' in expr.getText()) or ('-' in expr.getText())):
						self.visitChildren(ctx)
					elif(('*' in expr.getText()) or ('/' in expr.getText())):
						self.visitChildren(ctx)
					else:
						expr = expr.getText()
						print('store float ' + str(float_to_hex(float(expr))), ', float* %'+str(self.count) + ', align 4')
				else:
					if(('true' in expr.getText()) or ('false' in expr.getText())):
						print('store i1 '+ expr.getText(), ', i1* %'+str(self.count) + ', align 4')
					else:
						self.visitChildren(ctx)
			  		
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
				parametros[func_name,p.ID().getText()] = self.count
				if ('int' in p.getText()):
					print('%' + str(self.count) + ' = alloca i32, align 4')
				elif('float' in p.getText()):
					print('%' + str(self.count) + ' = alloca float, align 4')
				else:
					print('%' + str(self.count) + ' = alloca i1, align 4')
			j = 0

			for p in listaParam:
				i += 1
				if ('int' in p.getText()):
					print('store i32 %' + str(j) + ', i32* %'+ str(i) + ', align 4')
				elif('float' in p.getText()):
					print('store float %' + str(j) + ', float* %'+ str(i) + ', align 4')
				else:
					print('store i1 %' + str(j) + ', i1* %'+ str(i) + ', align 4')
				j += 1
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
		exprOperador = ctx.op.text
		
		if(self.assign_que_ira_receber_valor_expr == None):
			nome_var = self.nome_variavel_atual			
		else:
			nome_var = self.assign_que_ira_receber_valor_expr
			self.assign_que_ira_receber_valor_expr = None

		if((nome_func, nome_var) in variaveis):
			nro_variavel_resp = variaveis[nome_func, nome_var][0]
			tipo = variaveis[nome_func, nome_var][1]
		else:
			nro_variavel_resp = '@' + str(nome_var)
			tipo = globais[nome_var]

		#Procuro em variaveis locais
		#elif: procuro em parametros
		#elif: procuro em globais
		#else: assumo que é um numero
		if(left == None):
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = variaveis[nome_func,varLeft][0]
			elif((nome_func,varLeft) in parametros):
				nVarLeft = parametros[nome_func,varLeft]
			else:
				nVarLeft = '@' + str(varLeft)
		else:
			nVarLeft = left

		if(right == None):
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = variaveis[nome_func,varRight][0]
			elif((nome_func,varRight) in parametros):
				nVarRight = parametros[nome_func,varRight]
			else:
				nVarRight = '@' + str(varRight)
		else:
			nvarRight = right

		#print(varLeft,varRight)
		#print(nVarLeft,nVarRight)
		# SE for inteiro
		if(tipo == 'int'):
			if ('+' == exprOperador):
				#Se for uma soma
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left + right
					print('store i32 ' + str(result) + ', i32* %'+ str(nro_variavel_resp)+ ', align 4')
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
					self.count_add() #Igual a self.count += 1
					print('%' + str(self.count) + '= load i32, i32* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= add nsw i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')					
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):					
					if(left == None):
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= add nsw i32 %' + str(self.count - 1) + ',' + str(right))
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
					else:
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= add nsw i32 ' + str(left) + ', %' + str(self.count - 1) )
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
					
			# SE FOR UMA SUBTRACAO		
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left - right					
					print('store i32 ' + str(result) + ', i32* %'+ str(nro_variavel_resp)+ ', align 4')
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= sub nsw i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					if(left == None):
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sub nsw i32 %' + str(self.count - 1) + ',' + str(right))
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
					else:
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sub nsw i32 ' + str(left) + ', %' + str(self.count - 1) )
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
		
		# Se for Float
		else:
			# SOMA FLOAT
			if('+' in exprOperador):
				#Se for uma soma
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left + right
					print('store float ' + str(result) + ', float* %'+ str(nro_variavel_resp)+ ', align 4')
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
					self.count_add() #Igual a self.count += 1
					print('%' + str(self.count) + '= load float, float* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fadd float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
					
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					if(left == None):
						print('Variavel na esquerda')
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fadd double %' + str(self.count - 1) + ' ,' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
					else:
						print('Variavel na direita')
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fadd double ' + str(left) + ', %' + str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
			# Subtração floatt
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left - right
					print('store float ' + str(result) + ', float* %'+ str(nro_variavel_resp)+ ', align 4')
					
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
					self.count_add() #Igual a self.count += 1
					print('%' + str(self.count) + '= load float, float* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fsub float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')					
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):					
					if(left == None):
						print('Variavel na esquerda')
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fsub double %' + str(self.count - 1) + ' ,' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
					else:
						print('Variavel na direita')
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fsub double ' + str(left) + ', %' + str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
		return self.visitChildren(ctx)

	def visitMulDivExpr(self, ctx:CymbolParser.MulDivExprContext):
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)
		nome_func = self.nome_func_atual
		exprOperador = ctx.op.text
		
		if(self.assign_que_ira_receber_valor_expr == None):
			nome_var = self.nome_variavel_atual			
		else:
			nome_var = self.assign_que_ira_receber_valor_expr
			self.assign_que_ira_receber_valor_expr = None

		if((nome_func, nome_var) in variaveis):
			nro_variavel_resp = variaveis[nome_func, nome_var][0]
			tipo = variaveis[nome_func, nome_var][1]
		else:
			nro_variavel_resp = '@' + str(nome_var)
			tipo = globais[nome_var]

		print(left,right)
		#Procuro em variaveis locais
		#elif: procuro em parametros
		#elif: procuro em globais
		#else: assumo que é um numero
		if(left == None):
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = variaveis[nome_func,varLeft][0]
			elif((nome_func,varLeft) in parametros):
				nVarLeft = parametros[nome_func,varLeft]
			else:
				nVarLeft = '@' + str(varLeft)
		else:
			nVarLeft = left

		if(right == None):
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = variaveis[nome_func,varRight][0]
			elif((nome_func,varRight) in parametros):
				nVarRight = parametros[nome_func,varRight]
			else:
				nVarRight = '@' + str(varRight)
		else:
			nvarRight = right
		# Se um dos operandos for uma variável,left ou right estara com seu valor NONE
		# Se os dois operandos forem variáveis os dois campos left e right teram valor NONE
		# Se nenhum dos dois tiver valores NONE os dois são constantes

		exprOperador = ctx.op.text
		# SE FOR UMA Multiplicação
			#SE FOR INT
		if(tipo == 'int'):			
			if ('*' == exprOperador):
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left * right
					print('store i32 ' + str(result) + ', i32* %'+ str(nro_variavel_resp)+ ', align 4')
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= mul nsw i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):					
					if(left == None):
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= mul nsw i32 %' + str(self.count - 1) + ',' + str(right))
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
					else:
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= mul nsw i32 '+ str(left) + ', %' + str(self.count - 1))
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')					
			# SE FOR UMA Divisão		
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left / right
					print('store i32 ' + str(result) + ', i32* %'+ str(nro_variavel_resp)+ ', align 4')
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= sdiv i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))	
					print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):					
					if(left == None):
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sdiv i32 %' + str(self.count - 1) + ',' + str(right))
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
					else:
						self.count += 1
						print('%' + str(self.count) + '= load i32, i32* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sdiv i32 ' + str(left) + ', %' + str(self.count - 1) )
						print('store i32 %' + str(self.count) + ', i32* %' + str(nro_variavel_resp) + ', align 4')
		
		else:
			  #SE FOR FLOAT
			if ('*' == exprOperador):
    				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left * right
					print('store float ' + str(result) + ', float* %'+ str(nro_variavel_resp)+ ', align 4')				
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load float, float* ' + str(nVarLeft) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load float, float* '  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fmul float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fmul double %' + str(self.count - 1) + ',' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')						
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
					else:
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fmul double ' + str(left) + ',' + ' %' +str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
					
			# SE FOR UMA Divisão FLOAT		
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left / right
					print('store float ' + str(result) + ', float* %'+ str(nro_variavel_resp)+ ', align 4')
					
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load float, float* %'  + str(nVarRight) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fdiv float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fdiv double %' + str(self.count - 1) + ',' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
					else:
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fdiv double ' + str(left) + ',' + ' %' +str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')     
		return self.visitChildren(ctx)
    

	def visitNotExpr(self, ctx:CymbolParser.NotExprContext):
  #%5 = icmp ne i32 %4, 0
  #%6 = xor i1 %5, true
  #%7 = zext i1 %6 to i32
		expressao = ctx.expr().accept(self)
		print('not ',expressao)
		return self.visitChildren(ctx)

	# Visit a parse tree produced by CymbolParser#AndOrExpr.
	def visitAndOrExpr(self, ctx:CymbolParser.AndOrExprContext):
		#coletando operadores e operação
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)
		nome_func = self.nome_func_atual
		exprOperador = ctx.op.text
		if('&&' == exprOperador):
			print('Annnd')
		else: 
			print('oooorr')
		return self.visitChildren(ctx)
'''
	# Visit a parse tree produced by CymbolParser#EqExpr.
	def visitEqExpr(self, ctx:CymbolParser.EqExprContext):
		#coletando operadores e operação
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)
		print(left,right)
		nome_func = self.nome_func_atual
		exprOperador = ctx.op.text
		#icmp eq i32 4, 5          ; yields: result=false
		#<result> = icmp ne float* %X, %X     ; yields: result=false
		# SE for inteiro (verificar com @Adriano) junto com esses 'None'
		# caso 1: constantes
		if('==' == exprOperador):
			if((left != None) and (right != None)):
				result = (left == right)
				print('store i1 '+ str(result)+ ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????

		if('!=' == exprOperador):
			if((left != None) and (right != None)):
				result = (left != right)
				print('store i1 ' + str(result) + ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????

		elif(self.tipo_atual == 'float'):
			if('==' == exprOperador):
				if((left != None) and (right != None)):
					result = (left == right)
					print('store i1 ' + result + ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????

			if('!=' == exprOperador):
		else:
			if('==' == exprOperador):
				if((left != None) and (right != None)):
					result = (left == right)
					print('store i1 ' + result + ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????
			if('!=' == exprOperador)
		return self.visitChildren(ctx)
'''
'''
	# Visit a parse tree produced by CymbolParser#ComparisonExpr.
	# http://llvm.org/docs/LangRef.html#icmp-instruction
def visitComparisonExpr(self, ctx:CymbolParser.ComparisonExprContext):
		#coletando operadores e operação
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)
		nome_func = self.nome_func_atual
		exprOperador = ctx.op.text

		#se tipo inteiro usamos icmp
		if(self.tipo_atual == 'int'):
			if('<' == exprOperador):
			elif('<=' == exprOperador):
			elif('>' == exprOperador):
			elif('>=' == exprOperador):
		#se tipo float usamos fcmp
		else:
			if('<' == exprOperador):
			elif('<=' == exprOperador):
			elif('>' == exprOperador):
			elif('>=' == exprOperador):
		
		return self.visitChildren(ctx)
		
		''
	def aggregateResult(self, aggregate:Type, next_result:Type):
		return next_result if next_result != None else aggregate
'''
#%13 = load i32, i32* %7, align 4
#  ret i32 %13
    # Visit a parse tree produced by CymbolParser#returnStat.
'''
	def visitReturnStat(self, ctx:CymbolParser.ReturnStatContext):
		retorno = variaveis[ctx.expr().getText(),str(ctx.expr())]
		print('%' + str(self.count) + '= load i32, i32* %'+ str(retorno) + ', align 4')
		print('ret i32' + str(self.count))
		#return self.visitChildren(ctx)
 '''
 #not
 #and e or
 #igual e diferente
 #Maior e menor
 #>= <=