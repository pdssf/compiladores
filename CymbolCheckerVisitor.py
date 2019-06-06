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

def converte(num):
	if(num == 'true'):
		return True
	elif(num == 'false'):
		return False
	else:
		try:
			ret = int(num)
		except:
			try:
				ret = float(num)
			except:
				ret = None
		return ret

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
		if(self.assign_que_ira_receber_valor_expr == None):
			print('store i32 ' + ctx.getText() + ', i32* %'+ str(self.count) + ', align 4')
		else:
			nome_func = self.nome_func_atual
			nome_var = self.assign_que_ira_receber_valor_expr
			if((nome_func, nome_var) in variaveis):
				nro_variavel_resp = '%'+str(variaveis[nome_func, nome_var][0])
			else:
				nro_variavel_resp = '@' + str(nome_var)
			print('store i32 ' + ctx.getText() + ', i32* '+ nro_variavel_resp + ', align 4')
			self.assign_que_ira_receber_valor_expr = None
		return int(ctx.INT().getText())

	def visitFloatExpr(self, ctx:CymbolParser.FloatExprContext):
		if(self.assign_que_ira_receber_valor_expr == None):
			print('store float ' + str(float_to_hex(float(ctx.getText()))), ', float* %'+str(self.count) + ', align 4')
		else:
			nome_func = self.nome_func_atual
			nome_var = self.assign_que_ira_receber_valor_expr
			if((nome_func, nome_var) in variaveis):
				nro_variavel_resp = '%'+str(variaveis[nome_func, nome_var][0])
			else:
				nro_variavel_resp = '@' + str(nome_var)
			print('store float ' + str(float_to_hex(float(ctx.getText()))), ', float* '+str(nro_variavel_resp) + ', align 4')
			self.assign_que_ira_receber_valor_expr = None
		return float(ctx.FLOAT().getText())

	def visitBooleanExpr(self, ctx:CymbolParser.BooleanExprContext):
		if(self.assign_que_ira_receber_valor_expr == None):
			print('store i1 '+ ctx.getText(), ', i1* %'+str(self.count) + ', align 4')
		else:
			nome_func = self.nome_func_atual
			nome_var = self.assign_que_ira_receber_valor_expr
			if((nome_func, nome_var) in variaveis):
				nro_variavel_resp = '%'+str(variaveis[nome_func, nome_var][0])
			else:
				nro_variavel_resp = '@' + str(nome_var)
			print('store i1 '+ ctx.getText(), ', i1* %'+ nro_variavel_resp + ', align 4')
			self.assign_que_ira_receber_valor_expr = None
		return self.visitChildren(ctx)

	def visitAssignStat(self, ctx:CymbolParser.AssignStatContext):
		self.assign_que_ira_receber_valor_expr = ctx.ID().getText()
		return self.visitChildren(ctx)
#-----------------------------------------------------------------------------------------------------------------------------
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
			elif(tyype == 'float'):
				print('%' + str(self.count) +  '= alloca float, align 4')
			else:
				print('%' + str(self.count) + '= alloca i1, align 4')
			variaveis[func_name,var_name] = (self.count,tyype)

			self.nome_variavel_atual = var_name
			if (expr != None):
				self.visitChildren(ctx)
#-----------------------------------------------------------------------------------------------------------------------------
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
				if ('int' in p.getText()):
					print('%' + str(self.count) + ' = alloca i32, align 4')
					tipo = 'int'
				elif('float' in p.getText()):
					print('%' + str(self.count) + ' = alloca float, align 4')
					tipo = 'float'
				else:
					print('%' + str(self.count) + ' = alloca i1, align 4')
					tipo = 'boolean'
				parametros[func_name,p.ID().getText()] = (self.count, tipo)
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
#-----------------------------------------------------------------------------------------------------------------------------
	def visitAddSubExpr(self, ctx:CymbolParser.AddSubExprContext):
		left = ctx.expr()[0].getText()
		right = ctx.expr()[1].getText()
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
		left = converte(left)
		if(left!= None):
			nVarLeft = left
		else:
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = variaveis[nome_func,varLeft][0]
			elif((nome_func,varLeft) in parametros):
				nVarLeft = parametros[nome_func,varLeft][0]
			else:
				nVarLeft = '@' + str(varLeft)

		right = converte(right)
		if(right!= None):
			nVarRight = right
		else:
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = variaveis[nome_func,varRight][0]
			elif((nome_func,varRight) in parametros):
				nVarRight = parametros[nome_func,varRight][0]
			else:
				nVarRight = '@' + str(varRight)

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
						self.count += 1
						print('%' + str(self.count) + '= load float, float* %' + str(nVarRight) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fsub double ' + str(left) + ', %' + str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						print('store float %' + str(self.count) + ', float* %' + str(nro_variavel_resp) + ', align 4')
#-----------------------------------------------------------------------------------------------------------------------------
	def visitMulDivExpr(self, ctx:CymbolParser.MulDivExprContext):
		left = ctx.expr()[0].getText()
		right = ctx.expr()[1].getText()
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
		left = converte(left)
		if(left!= None):
			nVarLeft = left
		else:
			left = None
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = variaveis[nome_func,varLeft][0]
			elif((nome_func,varLeft) in parametros):
				nVarLeft = parametros[nome_func,varLeft][0]
			else:
				nVarLeft = '@' + str(varLeft)

		right = converte(right)
		if(right!= None):
			nVarRight = right
		else:
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = variaveis[nome_func,varRight][0]
			elif((nome_func,varRight) in parametros):
				nVarRight = parametros[nome_func,varRight][0]
			else:
				nVarRight = '@' + str(varRight)

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
#-----------------------------------------------------------------------------------------------------------------------------
	def visitNotExpr(self, ctx:CymbolParser.NotExprContext):
		# a instrução not deve tomar um literal ou booleano
		nome_func = self.nome_func_atual
		expressao = ctx.expr().getText()
		
		if(self.assign_que_ira_receber_valor_expr == None):
			nome_var = self.nome_variavel_atual			
		else:
			nome_var = self.assign_que_ira_receber_valor_expr
			self.assign_que_ira_receber_valor_expr = None		
		
		if((nome_func, nome_var) in variaveis):
			nro_variavel_resp = '%' + str(variaveis[nome_func, nome_var][0])
		else:
			nro_variavel_resp = '@' + str(nome_var)
		
		#Caso 1: negação de literais
		if(expressao == 'true'):
			print('store i1 false' + ', i1* '+ str(nro_variavel_resp)+ ', align 4')				
		elif(expressao == 'false'):
			print('store i1 true' + ', i1* '+ str(nro_variavel_resp)+ ', align 4')	
		
		#Caso 2: negação de variaveis ou expressões
		else:
			if((nome_func,expressao) in variaveis):
				nexpressao = '%'+str(variaveis[nome_func,expressao][0])
				tipo = variaveis[nome_func,expressao][1]
			elif((nome_func,expressao) in parametros):
				nexpressao = '%'+str(parametros[nome_func,expressao])
			else:
				nexpressao = '@' + str(expressao)
			
			self.count += 1
			print('%'+str(self.count),'= load i1, i1*',nexpressao,', align 4')
			#self.count +=1
			#print('%'+str(self.count),'= cmp ne i1*'+str(self.count-1),',false')
			self.count+=1
			print('%'+str(self.count),'= xor i1*'+str(self.count-1),',true')
			#self.count+=1
			#print('%'+str(self.count),'= zext i1*'+str(self.count-1),',true')
			print('store i1 %'+ str(self.count),' i1*' ,str(nro_variavel_resp)+', align 4')

  		#%5 = load i32, i32* %4, align 4
			#%5 = icmp ne i32 %4, 0
			#%6 = xor i1 %5, true
			#%7 = zext i1 %6 to i32

		return self.visitChildren(ctx)
#-----------------------------------------------------------------------------------------------------------------------------
	def visitAndOrExpr(self, ctx:CymbolParser.AndOrExprContext):
		left = ctx.expr()[0].getText()
		right = ctx.expr()[1].getText()
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

		#apenas para ajudar na checkagem
		varl = False
		varr = False
		
		if(left != 'true' and left != 'false'):
			varl = True
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = variaveis[nome_func,varLeft][0]
			elif((nome_func,varLeft) in parametros):
				nVarLeft = parametros[nome_func,varLeft][0]
			else:
				nVarLeft = '@' + str(varLeft)
		else:
			nVarLeft = left

		if(right != 'true' and right != 'false'):
			varr = True
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = variaveis[nome_func,varRight][0]
			elif((nome_func,varRight) in parametros):
				nVarRight = parametros[nome_func,varRight][0]
			else:
				nVarRight = '@' + str(varRight)
		else:
			nvarRight = right

		if('&&' in exprOperador): #caso uma operação AND
			if(varr == False or varl == False): # se ha alguma constante

				if(left == False or right == False):# se alguma delas é falsa
					result = 'false'
					print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
				elif(varr):
					self.count_add()
					print('%' + str(self.count) + '= load i1, i1* %'  + str(nVarRight) + ', align 4')
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
				elif(varl):
					self.count_add()
					print('%' + str(self.count) + '= load i1, i1* %' + str(nVarLeft) + ', align 4')
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
				else:
					result = 'true'
					print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
			else:#se só existem variáveis
				self.count_add()
				print('%' + str(self.count) + '= load i1, i1* %' + str(nVarLeft) + ', align 4')
				self.count_add()
				print('%' + str(self.count) + '= load i1, i1* %'  + str(nVarRight) + ', align 4')
				self.count_add()
				#<result> = and i32 4, %var
				print('%' + str(self.count) + '= and i1, %'  + str(self.count - 1) +', %' + str(self.count - 2)+ ', align 4')
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')

		else: #caso uma operação OR
			if(varr == False or varl == False): # se constante
				if(left or right):# se alguma delas é vdd
					result = 'true'
					print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
				elif(varr):
					self.count_add()
					print('%' + str(self.count) + '= load i1, i1* %'  + str(nVarRight) + ', align 4')
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
				elif(varl):
					self.count_add()
					print('%' + str(self.count) + '= load i1, i1* %' + str(nVarLeft) + ', align 4')
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
				else:
					result = 'false'
					print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
			else:
				self.count_add()
				print('%' + str(self.count) + '= load i1, i1* %' + str(nVarLeft) + ', align 4')
				self.count_add()
				print('%' + str(self.count) + '= load i1, i1* %'  + str(nVarRight) + ', align 4')
				self.count_add()
				#<result> = and i32 4, %var
				print('%' + str(self.count) + '= or i1, %'  + str(self.count - 1)+', %' + str(self.count - 2)+', align 4')
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
#-----------------------------------------------------------------------------------------------------------------------------
	def visitEqExpr(self, ctx:CymbolParser.EqExprContext):
		left = ctx.expr()[0].getText()
		right = ctx.expr()[1].getText()
		nome_func = self.nome_func_atual
		  
		if(self.assign_que_ira_receber_valor_expr == None):
			nome_var = self.nome_variavel_atual			
		else:
			nome_var = self.assign_que_ira_receber_valor_expr
			self.assign_que_ira_receber_valor_expr = None

		if((nome_func, nome_var) in variaveis):
			nro_variavel_resp = variaveis[nome_func, nome_var][0]
		else:
			nro_variavel_resp = '@' + str(nome_var)

		#Procuro em variaveis locais
		#elif: procuro em parametros
		#elif: procuro em globais
		#else: assumo que é um numero
		left = converte(left)
		if(left!= None):
			nVarLeft = left
			tipo = type(left)
		else:
			left = None
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = variaveis[nome_func,varLeft][0]
				tipo = variaveis[nome_func,varLeft][1]
			elif((nome_func,varLeft) in parametros):
				nVarLeft = parametros[nome_func,varLeft][0]
				tipo = parametros[nome_func,varLeft][1]
			else:
				nVarLeft = '@' + str(varLeft)
				tipo = globais[varLeft]

		right = converte(right)
		if(right!= None):
			tipo = type(right)
			nVarRight = right
		else:
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = variaveis[nome_func,varRight][0]
				tipo = variaveis[nome_func,varRight][1]
			elif((nome_func,varRight) in parametros):
				nVarRight = parametros[nome_func,varRight][0]
				tipo = parametros[nome_func,varRight][1]
			else:
				nVarRight = '@' + str(varRight)
				tipo = globais[varRight]
		#print(exprOperador);
		#icmp eq i32 4, 5          ; yields: result=false
		#<result> = icmp ne float* %X, %X     ; yields: result=false
		#Cmp
		#eq and not eq
		if(tipo =='int' or tipo == int):
			if(ctx.op.text == '=='):
				exprOperador = 'eq'
			else:
				exprOperador = 'ne'
			if((left != None) and (right != None)):# Constantes
				if(exprOperador == 'eq'):
					result = (left == right)
				else:
					result = (left != right)
				print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
			
			elif((left == None) and (right == None)):# 2 Variáveis
				self.count += 1
				print('%' + str(self.count) + '= load i32, i32* %' + str(nVarLeft) + ', align 4')
				self.count += 1
				print('%' + str(self.count) + '= load i32, i32* %' + str(nVarRight) + ', align 4')
				self.count += 1
				print('%' + str(self.count) + '= icmp '+ exprOperador + ' i32 %' + str(self.count - 2) + ', %' + str(self.count -1))
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
			
			else:
				if(left == None):# Variável e cte
					self.count += 1
					print('%' + str(self.count) + ' = load i32, i32* %' + str(nVarLeft) + ', align 4')
					self.count += 1
					print('%' + str(self.count) + ' = icmp '+ exprOperador + ' i32 %' + str(self.count - 1) + ', ' + str(right))
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
				else:
					self.count += 1
					print('%' + str(self.count) + ' = load i32, i32* %' + str(nVarRight) + ', align 4')
					self.count += 1
					print('%' + str(self.count) + ' = icmp '+ exprOperador + ' i32 ' + str(left) + ', %' + str(self.count - 1) )   
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
      
		elif(tipo == 'float' or tipo == float):
			if(ctx.op.text == '=='): #conforme as regras do clang
				exprOperador = 'oeq'
			else:
				exprOperador = 'une'

			if((left != None) and (right != None)):
				if(exprOperador == 'oeq'):
					result = (left == right)
				else:
					result = (left != right)
				print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	

			elif((left == None) and (right == None)):
				self.count += 1
				print('%' + str(self.count) + '= load float, float* %' + str(nVarLeft) + ', align 4')
				self.count += 1
				print('%' + str(self.count) + '= load float, float* %' + str(nVarRight) + ', align 4')
				self.count += 1
				print('%' + str(self.count) + '= fcmp '+ exprOperador + ' float %' + str(self.count - 2) + ', %' + str(self.count -1))
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')

			#Verificar com Paulo , notação 3.003000e+02
			else:
				if(left == None):
					self.count += 1
					print('%' + str(self.count) + ' = load float, float* %' + str(nVarLeft) + ', align 4')
					self.count += 1
					print('%' + str(self.count) + ' = fpext float %' + str(self.count-1) + ' to double')
					self.count += 1
					print('%' + str(self.count) + ' = fcmp '+ exprOperador + ' double %' + str(self.count - 1) + ', ' + str(right))
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
					
				else:
					self.count += 1
					print('%' + str(self.count) + ' = load float, float* %' + str(nVarRight) + ', align 4')
					self.count += 1
					print('%' + str(self.count) + ' = fpext float %' + str(self.count-1) + ' to double')
					self.count += 1
					print('%' + str(self.count) + ' = fcmp '+ exprOperador + ' double '  + str(left) + ', %' + str(self.count - 1))
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')

		else:
			if(ctx.op.text == '=='):
				exprOperador = 'eq'
			else:
				exprOperador = 'ne'

			if((left != None) and (right != None)):# Constantes
				if(exprOperador == 'eq'):
					result = (left == right)
				else:
					result = (left != right)
				print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
			
			elif((left == None) and (right == None)):# 2 Variáveis
				self.count += 1
				print('%' + str(self.count) + '= load i8, i8* %' + str(nVarLeft) + ', align 4')
				self.count += 1
				print('%' + str(self.count) + '= load i8, i8* %' + str(nVarRight) + ', align 4')
				self.count += 1
				print('%' + str(self.count) + '= icmp '+ exprOperador + ' i8 %' + str(self.count - 2) + ', %' + str(self.count -1))
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
			
			else:
				if(left == None):# Variável e cte
					self.count += 1
					print('%' + str(self.count) + ' = load i8, i8* %' + str(nVarLeft) + ', align 4')
					self.count += 1
					print('%' + str(self.count) + ' = icmp '+ exprOperador + ' i8 %' + str(self.count - 1) + ', ' + str(right))
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
				else:
					self.count += 1
					print('%' + str(self.count) + ' = load i8, i8* %' + str(nVarRight) + ', align 4')
					self.count += 1
					print('%' + str(self.count) + ' = icmp '+ exprOperador + ' i8 ' + str(left) + ', %' + str(self.count - 1) )   
					print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
#-----------------------------------------------------------------------------------------------------------------------------
	# Visit a parse tree produced by CymbolParser#ComparisonExpr.
	def visitComparisonExpr(self, ctx:CymbolParser.ComparisonExprContext):
		left = ctx.expr()[0].getText()
		right = ctx.expr()[1].getText()
		nome_func = self.nome_func_atual
			
		if(self.assign_que_ira_receber_valor_expr == None):
			nome_var = self.nome_variavel_atual			
		else:
			nome_var = self.assign_que_ira_receber_valor_expr
			self.assign_que_ira_receber_valor_expr = None

		if((nome_func, nome_var) in variaveis):
			nro_variavel_resp = variaveis[nome_func, nome_var][0]
		else:
			nro_variavel_resp = '@' + str(nome_var)

		#Procuro em variaveis locais
		#elif: procuro em parametros
		#elif: procuro em globais
		#else: assumo que é um numero
		left = converte(left)
		if(left!= None):
			nVarLeft = left
			tipo = type(left)
		else:
			left = None
			varLeft = str(ctx.expr()[0].ID())
			if((nome_func,varLeft) in variaveis):
				nVarLeft = '%' + str(variaveis[nome_func,varLeft][0])
				tipo = retType(variaveis[nome_func,varLeft][1])
			elif((nome_func,varLeft) in parametros):
				nVarLeft = '%' + str(parametros[nome_func,varLeft][0])
				tipo = retType(parametros[nome_func,varLeft][1])
			else:
				nVarLeft = '@' + str(varLeft)
				tipo = retType(globais[varLeft])
			self.count_add()
			print('%{} = load {}, {}* {}, align 4'.format(self.count, tipo,tipo,nVarLeft))

		right = converte(right)
		if(right!= None):
			tipo = type(right)
			nVarRight = right
		else:
			right = None
			varRight = str(ctx.expr()[1].ID())
			if((nome_func,varRight) in variaveis):
				nVarRight = '%' + str(variaveis[nome_func,varRight][0])
				tipo = retType(variaveis[nome_func,varRight][1])
			elif((nome_func,varRight) in parametros):
				nVarRight = '%' + str(parametros[nome_func,varRight][0])
				tipo = retType(parametros[nome_func,varRight][1])
			else:
				nVarRight = '@' + str(varRight)
				tipo = retType(globais[varRight])
			self.count_add()
			print('%{} = load {}, {}* {}, align 4'.format(self.count, tipo,tipo,nVarRight))
		#print(exprOperador);
		#icmp eq i32 4, 5          ; yields: result=false
		#<result> = icmp ne float* %X, %X     ; yields: result=false
		#Cmp
		#eq and not eq
		if(tipo =='int' or tipo == int):
			op = ctx.op.text
			if(op == '>'):
				exprOperador = 'sgt'
			elif(op == '>='):
				exprOperador = 'sge'
			elif(op == '<'):
				exprOperador = 'slt'
			else:
				exprOperador = 'sle'
			if((left != None) and (right != None)):# Constantes
				if(exprOperador == 'sgt'):
					result = (left > right)
				elif(exprOperador == 'sge'):
					result = (left >= right)
				elif(exprOperador == 'slt'):
					result = (left < right)
				else:
					result = (left <= right)
				print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	
			
			elif((left == None) and (right == None)):# 2 Variáveis
				self.count += 1
				print('%' + str(self.count) + '= icmp '+ exprOperador + ' i32 %' + str(self.count - 2) + ', %' + str(self.count -1))
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
			
			else:
				self.count += 1
				if(left == None):# Variável e cte
					print('%' + str(self.count) + ' = icmp '+ exprOperador + ' i32 %' + str(self.count - 1) + ', ' + str(right))
				else:
					print('%' + str(self.count) + ' = icmp '+ exprOperador + ' i32 ' + str(left) + ', %' + str(self.count - 1) )   
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')

		else:
			op = ctx.op.text
			if(op == '>'):
				exprOperador = 'ogt'
			elif(op == '>='):
				exprOperador = 'oge'
			elif(op == '<'):
				exprOperador = 'olt'
			else:
				exprOperador = 'ole'

			if((left != None) and (right != None)):
				if(exprOperador == 'sgt'):
					result = (left > right)
				elif(exprOperador == 'sge'):
					result = (left >= right)
				elif(exprOperador == 'slt'):
					result = (left < right)
				else:
					result = (left <= right)
				print('store i1 ' + str(result)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')	

			elif((left == None) and (right == None)):
				self.count += 1
				print('%' + str(self.count) + '= fcmp '+ exprOperador + ' float %' + str(self.count - 2) + ', %' + str(self.count -1))
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')

			else:
				self.count += 1
				if(left == None):# Variável e cte
					print('%' + str(self.count) + ' = fcmp '+ exprOperador + ' float %' + str(self.count - 1) + ', ' + str(right))
				else:
					print('%' + str(self.count) + ' = fcmp '+ exprOperador + ' float ' + str(left) + ', %' + str(self.count - 1) )   
				print('store i1 %' + str(self.count)+', i1* %'+ str(nro_variavel_resp)+ ', align 4')
#-----------------------------------------------------------------------------------------------------------------------------
	def visitReturnStat(self, ctx:CymbolParser.ReturnStatContext):
		nome_func = self.nome_func_atual
		expr = ctx.expr().getText()
		expr = converte(expr)
		if(expr!= None):
			nVarExpr = expr
			tipo = retType(type(expr))
		else:
			expr = str(ctx.expr().ID())
			if((nome_func,expr) in variaveis):
				nVarExpr = '%' + str(variaveis[nome_func,expr][0])
				tipo = retType(variaveis[nome_func,expr][1])
			elif((nome_func,expr) in parametros):
				nVarExpr = '%' + str(parametros[nome_func,expr][0])
				tipo = retType(parametros[nome_func,expr][1])
			else:
				nVarExpr = '@' + str(expr)
				tipo = retType(globais[expr])
			self.count_add()
			print('%{} = load {}, {}* {}, align 4'.format(self.count, tipo,tipo,nVarExpr))
			nVarExpr = self.count

		print('ret {} %{}'.format(tipo,nVarExpr))

#-----------------------------------------------------------------------------------------------------------------------------
def retType(tipo):
		if(tipo == int or tipo == 'int'):
			return 'i32'
		elif(tipo == float or tipo == 'float'):
			return 'float'
		else:
			return 'i1'