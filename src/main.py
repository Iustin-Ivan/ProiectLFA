from sys import argv
from src.Lexer import Lexer

def main():
	if len(argv) != 2:
		return

	filename = argv[1]
	# TODO implementarea interpretor L (bonus)
	spec = [("LAMBDA", "lambda"), ("TWOPOINTS", ":"), ("NUMBER", "[0-9]+"), ("SPACE", "\\ "), ("NEWLINE", "\n"), ("OPENPAR", "\("), ("CLOSEPAR", "\)"),
			("DOUBLEPLUS", "\+\+"), ("PLUS", "\+"), ("NAME", "[a-z]+"), ("TAB", "\t")]
	with open(filename, 'r') as f:
		s = f.read()
		lexer = Lexer(spec)
		lexems = lexer.lex(s)
		lista = lexem_parse(lexems)
		single_list = lista[0]
		res = reduce_list(single_list)
		res = printing(res)
		if isinstance(res, str):
			res = res.replace(")(", ") (")
			res = res.replace("))", ") )")
		print(res)


def recursive_replace(function_body, parameter, value):
	for i in range(len(function_body)):
		if function_body[i] == parameter and function_body[i-1] != "lambda":
			function_body[i] = value
		elif function_body[i] == parameter and function_body[i-1] == "lambda":
			break
		elif isinstance(function_body[i], list):
			function_body[i] = recursive_replace(function_body[i], parameter, value)
	return function_body


def parse_expression(lista, values):
	parameter_list, operator_list = [], []
	while True:
		parameter_list.append(lista[1])
		if lista[3] != "lambda":
			function_body = lista[3]
			if len(lista) == 5:
				values.append(lista[4])
			elif len(lista) > 5:
				values.append(lista[4:])
			break
		lista = lista[3:]
	typeofbody = type(function_body)
	if typeofbody == list:
		while function_body[0] == "+" or function_body[0] == "++":
			operator_list.append(function_body[0])
			function_body = function_body[1]
	return parameter_list, operator_list, function_body, typeofbody


def recursive_reduce(lista, values):
	if isinstance(lista[0], list):
		if len(lista) == 1:
			while values:
				lista.append(values.pop())
				lista = [lista]
			lista = lista[0]
		if isinstance(lista[1], list) or isinstance(lista[1], int):
			values.append(lista[1])
		else:
			values.append(lista[1:])
		reduced = recursive_reduce(lista[0], values)
		return reduced
	else:
		parameter_list, operator_list, function_body, typeofbody = parse_expression(lista, values)
		while parameter_list:
			parameter = parameter_list[0]
			parameter_list = parameter_list[1:]
			value = values.pop()
			if parameter not in parameter_list:
				if typeofbody == list:
					function_body = recursive_replace(function_body, parameter, value)
				else:
					if function_body == parameter:
						function_body = [value]
		flat_form = flatten_list(function_body)
		common_elements_exist = any(isinstance(elem, str) for elem in flat_form)
		if common_elements_exist:
			function_body = recursive_reduce(function_body, values)
		while operator_list:
			new_list = [operator_list.pop(), function_body]
			return reduce_list(new_list)
		if typeofbody != list and isinstance(function_body, list):
			return function_body[0]
		return function_body




def reduce_list(lista):
	op_list = []
	while lista[0] == "++" or lista[0] == "+":
		op_list.append(lista[0])
		lista = lista[1]
	res = flatten_list(lista)
	if 'lambda' in res:
		res = recursive_reduce(lista, [])
	else:
		res = lista
	while op_list:
		op = op_list.pop()
		if op == "+":
			res = flatten_list(res)
			res = sum(res)
		elif op == "++":
			res = concat_list(res)
	return res


def printing(res):
	if isinstance(res, list):
		stringbuild = "( "
		for item in res:
			if not item:
				stringbuild += "() "
			elif isinstance(item, list):
				stringbuild += printing(item)
			else:
				stringbuild += str(item) + " "
		stringbuild += ")"
		return stringbuild
	elif isinstance(res, int):
		return res

def flatten_list(nested_list):
	flat_list = []
	for item in nested_list:
		if isinstance(item, list):
			flat_list.extend(flatten_list(item))
		else:
			flat_list.append(item)
	return flat_list

def concat_list(lista):
	res = []
	for item in lista:
		if isinstance(item, list):
			res.extend(item)
		else:
			res.append(item)
	return res


def lexem_parse(lexems):
	curr_list = []
	stack = []
	for lex in lexems:
		if lex[0] == 'NUMBER':
			curr_list.append(int(lex[1]))
		elif lex[0] == 'OPENPAR':
			stack.append(curr_list)
			curr_list = []
		elif lex[0] == 'CLOSEPAR':
			last_list = stack.pop()
			last_list.append(curr_list)
			curr_list = last_list
		elif lex[0] == 'PLUS':
			curr_list.append('+')
		elif lex[0] == 'DOUBLEPLUS':
			curr_list.append('++')
		elif lex[0] == 'LAMBDA':
			curr_list.append('lambda')
		elif lex[0] == 'TWOPOINTS':
			curr_list.append(':')
		elif lex[0] == 'NAME':
			curr_list.append(lex[1])
	return curr_list

if __name__ == '__main__':
    main()
