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
		self.nome_variavel_atual = None
		self.tipo_atual = None
		self.assign_que_ira_receber_valor_expr= None
	
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
		self.assign_que_ira_receber_valor_expr= ctx.ID().getText()
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
				print('global float '+ expr, end = ', ')
			elif(tyype == 'boolean'):
				print('global i1 '+ expr, end = ', ')
			print('align 4')
		else:
			# LOCAL
			#self.estouDentro_daFuncao = 1
			self.count += 1
			if(tyype == 'int'):
				self.tipo_atual = 'int'
				print('%' + str(self.count) +  '= alloca i32, align 4')
				variaveis[func_name,var_name] = self.count
				self.nome_variavel_atual = var_name
			elif(tyype == 'float'):
				self.tipo_atual = 'float'
				print('%' + str(self.count) +  '= alloca float, align 4')
				#print('Var name : ' + str(var_name) + 'nro var : ' + str(self.count))
				variaveis[func_name,var_name] = self.count
				self.nome_variavel_atual = var_name
			else:
				self.tipo_atual = 'boolean'
				print('%' + str(self.count) + '= alloca i1, align 4')
				variaveis[func_name,var_name] = self.count

			if (expr != None):
				if(tyype == 'int'):
					self.tipo_atual = 'int'
					if(('+' in expr.getText()) or ('-' in expr.getText())):
						self.visitChildren(ctx)
					elif(('*' in expr.getText()) or ('/' in expr.getText())):
						self.visitChildren(ctx)
					else:	
						print('store i32 ' + expr.getText() + ', i32* %'+ str(self.count) + ', align 4')
						valores_variaveis[func_name,var_name] = int(expr.getText())
						variaveis[func_name,var_name] = self.count
				elif(tyype == 'float'):
					self.tipo_atual = 'float'
					if(('+' in expr.getText()) or ('-' in expr.getText())):
    						self.visitChildren(ctx)
					elif(('*' in expr.getText()) or ('/' in expr.getText())):
						self.visitChildren(ctx)
					else:
						variaveis[func_name,var_name] = self.count
						#print('VAR NAME E SEU VALOR : ' + var_name + '  ' + str(expr.getText()))
						print('store float ' + expr.getText(), ', float* %'+str(self.count) + ', align 4')
						valores_variaveis[func_name,var_name] = float(expr.getText())
				else:
					self.tipo_atual = 'boolean'
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
		exprOperador = ctx.op.text
		# Se um dos operandos for uma variável,left ou right estara com seu valor NONE
		# Se os dois operandos forem variáveis os dois campos left e right teram valor NONE
		# Se nenhum dos dois tiver valores NONE os dois são constantes
		
		# SE for inteiro
		if(self.tipo_atual == 'int'):
			if ('+' == exprOperador):
				#Se for uma soma
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left + right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store i32 ' + str(result) + ', i32* %'+ str(Nro_variavel_resp)+ ', align 4')
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]

					print('%' + str(self.count) + '= load i32, i32* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add() #Igual a self.count += 1
					print('%' + str(self.count) + '= load i32, i32* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= add nsw i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
					print('store i32 %' + str(self.count) + ', i32* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] + valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
					
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] + right
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= add nsw i32 %' + str(self.count - 1) + ',' + str(right))
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr= None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] + left
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= add nsw i32 ' + str(left) + ', %' + str(self.count - 1) )
						if(self.assign_que_ira_receber_valor_expr != None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					
			# SE FOR UMA SUBTRACAO		
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left - right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store i32 ' + str(result) + ', i32* %'+ str(Nro_variavel_resp)+ ', align 4')
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]
					print('%' + str(self.count) + '= load i32, i32* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= sub nsw i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
     
					print('store i32 %' + str(self.count) + ', i32* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] - valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] - right
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sub nsw i32 %' + str(self.count - 1) + ',' + str(right))
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr= None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] - left
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sub nsw i32 ' + str(left) + ', %' + str(self.count - 1) )
						if(self.assign_que_ira_receber_valor_expr != None):
    							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
		# Se for Float
		else:
			# SOMA FLOAT
			if('+' in exprOperador):
				#Se for uma soma
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left + right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store float ' + str(result) + ', float* %'+ str(Nro_variavel_resp)+ ', align 4')
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
					variaveis[nome_func,self.nome_variavel_atual] = self.count
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]

					print('%' + str(self.count) + '= load float, float* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add() #Igual a self.count += 1
					print('%' + str(self.count) + '= load float, float* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fadd float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
					print('store float %' + str(self.count) + ', float* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] + valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
					
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						print('Variavel na esquerda')
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] + right
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fadd double %' + str(self.count - 1) + ' ,' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr= None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						print('Variavel na direita')
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] + left
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fadd double ' + str(left) + ', %' + str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr != None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr= None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
			# Subtração floatt
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left - right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store float ' + str(result) + ', float* %'+ str(Nro_variavel_resp)+ ', align 4')
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
					variaveis[nome_func,self.nome_variavel_atual] = self.count
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]

					print('%' + str(self.count) + '= load float, float* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add() #Igual a self.count += 1
					print('%' + str(self.count) + '= load float, float* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fsub float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
					print('store float %' + str(self.count) + ', float* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] - valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
					
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						print('Variavel na esquerda')
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] - right
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fsub double %' + str(self.count - 1) + ' ,' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr= None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						print('Variavel na direita')
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] - left
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + ' = fsub double ' + str(left) + ', %' + str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count-1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr != None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr= None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
		return self.visitChildren(ctx)

	def visitMulDivExpr(self, ctx:CymbolParser.MulDivExprContext):
		left = ctx.expr()[0].accept(self)
		right = ctx.expr()[1].accept(self)
		nome_func = self.nome_func_atual
		# Se um dos operandos for uma variável,left ou right estara com seu valor NONE
		# Se os dois operandos forem variáveis os dois campos left e right teram valor NONE
		# Se nenhum dos dois tiver valores NONE os dois são constantes

		exprOperador = ctx.op.text
		# SE FOR UMA Multiplicação
			#SE FOR INT
		if(self.tipo_atual == 'int'):
			
			if ('*' == exprOperador):
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left * right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store i32 ' + str(result) + ', i32* %'+ str(Nro_variavel_resp)+ ', align 4')
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]
					print('%' + str(self.count) + '= load i32, i32* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= mul nsw i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
					print('store i32 %' + str(self.count) + ', i32* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] * valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] * right
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= mul nsw i32 %' + str(self.count - 1) + ',' + str(right))
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] * left
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= mul nsw i32 '+ str(left) + ', %' + str(self.count - 1))
						if(self.assign_que_ira_receber_valor_expr != None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					
			# SE FOR UMA Divisão		
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left / right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store i32 ' + str(result) + ', i32* %'+ str(Nro_variavel_resp)+ ', align 4')
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]
					print('%' + str(self.count) + '= load i32, i32* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load i32, i32* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= sdiv i32 %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr = None
					print('store i32 %' + str(self.count) + ', i32* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] / valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] / right
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sdiv i32 %' + str(self.count - 1) + ',' + str(right))
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] / left
						print('%' + str(self.count) + '= load i32, i32* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + '= sdiv i32 ' + str(left) + ', %' + str(self.count - 1) )
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None

						print('store i32 %' + str(self.count) + ', i32* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
		
		else:
			  #SE FOR FLOAT
			if ('*' == exprOperador):
    				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left * right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					#print(' nmro ' + str(Nro_variavel_resp))
					print('store float ' + str(result) + ', float* %'+ str(Nro_variavel_resp)+ ', align 4')
					self.assign_que_ira_receber_valor_expr = None
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]
					print('%' + str(self.count) + '= load float, float* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load float, float* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fmul float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
					print('store float %' + str(self.count) + ', float* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] * valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] * right
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fmul double %' + str(self.count - 1) + ',' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] * left
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fmul double %' + str(left) + ',' + ' %' +str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					
			# SE FOR UMA Divisão FLOAT		
			else:
				#Caso 1 : Duas constantes
				if((left != None) and (right != None)):
					result = left / right
					if(self.assign_que_ira_receber_valor_expr!= None):
    						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					print('store float ' + str(result) + ', float* %'+ str(Nro_variavel_resp)+ ', align 4')
					self.assign_que_ira_receber_valor_expr = None
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso2 : Dois valores são variáveis
				elif((left == None) and (right == None)):
					self.count_add()
					Nome_Variavel_A = exprIDLEFT = str(ctx.expr()[0].ID())
					Nome_Variavel_B = exprIDLEFT = str(ctx.expr()[1].ID())
					Nro_variavel_A = variaveis[nome_func,Nome_Variavel_A]
					Nro_variavel_B = variaveis[nome_func,Nome_Variavel_B]
					print('%' + str(self.count) + '= load float, float* %' + str(Nro_variavel_A) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= load float, float* %'  + str(Nro_variavel_B) + ', align 4')
					self.count_add()
					print('%' + str(self.count) + '= fdiv float %'+ str(self.count - 2) + ' %' + str(self.count - 1))
					if(self.assign_que_ira_receber_valor_expr!= None):
						Nro_variavel_resp = variaveis[nome_func,self.assign_que_ira_receber_valor_expr]
					else:
						Nro_variavel_resp = variaveis[nome_func,self.nome_variavel_atual]
					self.assign_que_ira_receber_valor_expr= None
					print('store float %' + str(self.count) + ', float* %' + str(Nro_variavel_resp) + ', align 4')
					result = valores_variaveis[nome_func,Nome_Variavel_A] / valores_variaveis[nome_func,Nome_Variavel_B]
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
		
				#Caso 3 : Um dos valores é constante o outro é de uma variável
				elif((left == None) or (right == None)):
					
					if(left == None):
						self.count += 1
						exprIDLEFT = str(ctx.expr()[0].ID())
						nro_variavel = variaveis[nome_func,exprIDLEFT]
						result = valores_variaveis[str(nome_func),str(exprIDLEFT)] / right
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fdiv double %' + str(self.count - 1) + ',' + str(right))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
					else:
						self.count += 1
						exprIDRIGHT = str(ctx.expr()[1].ID())
						nro_variavel = variaveis[nome_func,exprIDRIGHT]
						result = valores_variaveis[str(nome_func),str(exprIDRIGHT)] / left
						print('%' + str(self.count) + '= load float, float* %' + str(nro_variavel) + ', align 4')
						self.count += 1
						print('%' + str(self.count) + ' = fpext float %' + str(self.count - 1) + ' to double')
						self.count += 1
						print('%' + str(self.count) + '= fdiv double %' + str(left) + ',' + ' %' +str(self.count - 1))
						self.count += 1
						print('%' + str(self.count) + ' = fptrunc double %' + str(self.count - 1) + ' to float')
						if(self.assign_que_ira_receber_valor_expr!= None):
							valor_registrador_atual = variaveis[str(nome_func),str(self.assign_que_ira_receber_valor_expr)]
						else:
							valor_registrador_atual = variaveis[str(nome_func),str(self.nome_variavel_atual)]
						self.assign_que_ira_receber_valor_expr = None
						print('store float %' + str(self.count) + ', float* %' + str(valor_registrador_atual) + ', align 4')
						valores_variaveis[nome_func,self.nome_variavel_atual] = result
     
		return self.visitChildren(ctx)
    

	def visitNotExpr(self, ctx:CymbolParser.NotExprContext):
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

	# Visit a parse tree produced by CymbolParser#EqExpr.
	def visitEqExpr(self, ctx:CymbolParser.EqExprContext):
		#coletando operadores e operação
		left = ctx.expr()[0].accept(self)
		print(left)
		right = ctx.expr()[1].accept(self)
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
				valores_variaveis[nome_func,self.nome_variavel_atual] = result
		if('!=' == exprOperador):
			if((left != None) and (right != None)):
				result = (left != right)
				print('store i1 ' + str(result) + ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????
				valores_variaveis[nome_func,self.nome_variavel_atual] = result
		'''elif(self.tipo_atual == 'float'):
			if('==' == exprOperador):
				if((left != None) and (right != None)):
					result = (left == right)
					print('store i1 ' + result + ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
			if('!=' == exprOperador):
		else:
			if('==' == exprOperador):
				if((left != None) and (right != None)):
					result = (left == right)
					print('store i1 ' + result + ', i1* %'+ str(self.count)+ ', align 4') #sera que tem esse align?????
					valores_variaveis[nome_func,self.nome_variavel_atual] = result
			if('!=' == exprOperador):'''
		return self.visitChildren(ctx)

	# Visit a parse tree produced by CymbolParser#ComparisonExpr.
	# http://llvm.org/docs/LangRef.html#icmp-instruction
	'''def visitComparisonExpr(self, ctx:CymbolParser.ComparisonExprContext):
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
		
		return self.visitChildren(ctx)'''

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
	#clang -S -emit-llvm teste.c
 
 #not
 #and e or
 #igual e diferente
 #Maior e menor
 #>= <=