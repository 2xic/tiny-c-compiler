"""
The AST has the ast logic.
"""

class Token:
    def __init__(self, value) -> None:
        self.value = value

class ReturnToken(Token):
    def __init__(self, value) -> None:
        super().__init__(value)

class Tokenizer:
    def __init__(self, source_code) -> None:
        self.break_tokens = [
            "\n",
            " ",
        ]
        self.special_symbols = [
            "(",
            ")",
            "{",
            "}",
            ";",
            "/",
            "*",
            "+",
        ]
        self.tokens = self._get_tokens(source_code)

    def _get_tokens(self, source_code):
        index = 0
        tokens = []

        token = ""
        is_waiting_for_new_line = False
        while index < len(source_code):
            char = source_code[index]
            if is_waiting_for_new_line and char != "\n":
                index += 1
                continue
            elif is_waiting_for_new_line:
                is_waiting_for_new_line = False
            # Find symbols
            if char == "/" and source_code[index + 1] == "/":
                # read until \n
                if len(token):
                    tokens.append(token)
                    token = ""
                is_waiting_for_new_line = True
                index += 1
                print("www")
            elif char == "/" and source_code[index + 1] == "*":
                # read until \n
                if len(token):
                    tokens.append(token)
                    token = ""
                while index < len(source_code):
                    if source_code[index] == "*" and source_code[index + 1] == "/":
                        index += 1
                        break
                    index += 1
            elif char in self.special_symbols:
                if len(token):
                    tokens.append(token)
                tokens.append(char)
                token = ""
            elif char in self.break_tokens:
                if len(token):
                    tokens.append(token)
                token = ""
            else:
                token += char
            index += 1
        if len(token):
            tokens.append(token)
        print("??")
        return tokens
    

"""
So based on tokens I create outputs. 
"""

class Nodes:
    def __init__(self) -> None:
        self.child_nodes = []

    def __str__(self) -> str:
        # lol
        name = getattr(self, "name") if "name" in dir(self) else ""
        if len(name):
            return f"{self.__class__.__name__} ({name}) " + str(self.child_nodes)
        else:
            return f"{self.__class__.__name__} " + str(self.child_nodes)

    def __repr__(self) -> str:
        return self.__str__()

class ReturnDefinition(Nodes):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.child_nodes = [value]

class TypeDefinition(Nodes):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

class FunctionDefinition(Nodes):
    def __init__(self, name, parameters, body, return_parameters) -> None:
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.body = body
        self.return_parameters = return_parameters
        self.child_nodes = [
            self.parameters,
            self.body,
            self.return_parameters
        ]

class FunctionBody(Nodes):
    def __init__(self) -> None:
        super().__init__()

class Parameters(Nodes):
    def __init__(self) -> None:
        super().__init__()

class TokenConsumer:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.index = 0

    def get_token(self):
        token = self.tokens[self.index]
        self.index += 1
        return token

    def is_peek_token(self, value):
        if self.get_token() == value:
            return True
        self.index -= 1
        return False
    
class File(Nodes):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        self.functions = {}

class VariableDeclaration(Nodes):
    def __init__(self, type, name, value) -> None:
        super().__init__()
        self.type = type
        self.name = name
        self.value = value
        self.child_nodes = [value]

class MathOp(Nodes):
    def __init__(self, op, expr_1, expr_2) -> None:
        super().__init__()
        self.op = op
        self.expr_1 = expr_1
        self.expr_2 = expr_2
        self.child_nodes = [
            expr_1,
            expr_2
        ]

class NumericValue(Nodes):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return super().__repr__()

class AST:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.types = {
            "int": TypeDefinition("int")
        }
        self.tokens_index = TokenConsumer(self.tokens)

    def build_ast(self):
        # Statements currently supported are only tokens
        file = File("example.c")
        file_nodes = self.get_root_symbols()
        file.child_nodes.append(file_nodes)

        if isinstance(file_nodes, FunctionDefinition):
            file.functions[file_nodes.name] = file_nodes

        assert self.tokens_index.index == len(self.tokens),  "Failed to parse source code..."
        return file

    def get_root_symbols(self):
        # grammar: [return type] [function name] [parameter start] .... [parameter end] [scope start]
        checkpoint = self.tokens_index.index
        function_scope = self.get_function_definition()
        # If nothing is found
        if function_scope is None:
            print("Failed at ", self.tokens_index.tokens[self.tokens_index.index:self.tokens_index.index+5])
            self.tokens_index.index = checkpoint

        if self.tokens_index == checkpoint:
            raise Exception("Failed to create AST :(")

        return function_scope

    def get_function_definition(self):
        return_parameter = self.tokens_index.get_token()
        if return_parameter in self.types:
            name = self.tokens_index.get_token()
            if name.isalnum():
                parameters = self.get_function_arguments()
                if parameters is None:
                    return None
                body = self.parse_function_body()
                if body is None:
                    return None
                
                return FunctionDefinition(
                    name,
                    parameters,
                    body,
                    TypeDefinition(return_parameter)
                )
        return None

    def get_function_arguments(self):
        if self.tokens_index.get_token() == "(":
            if self.tokens_index.get_token() == ")":
                return Parameters()
        return None
    
    def parse_function_body(self):
        if self.tokens_index.get_token() == "{":
            found_token = True
            body = FunctionBody()
            while found_token:
                for create_node in [
                    self.get_return_definition,
                    self.get_variable_assignment
                ]:                    
                    local_check_point = self.tokens_index.index
                    node_definition = create_node()
                    if node_definition is None:
                        found_token = False
                        self.tokens_index.index = local_check_point
                    else:
                        body.child_nodes.append(node_definition)
                        found_token = True
                        break
            # if it all failed
            if self.tokens_index.get_token() == "}":
                return body                
        return None
    
    def get_variable_assignment(self):
        type_value = self.tokens_index.get_token()
        if type_value in self.types:
            name = self.tokens_index.get_token()
            if name.isalnum():
                if self.tokens_index.get_token() == "=":
                    math_expression = self.get_math_expression()
                    if self.tokens_index.get_token() == ";" and math_expression is not None:
                        # variable initiation
                        return VariableDeclaration(
                            TypeDefinition(type_value),
                            name,
                            math_expression
                        )
        return None

    def get_return_definition(self):
        if self.tokens_index.get_token() == "return":
            value = self.tokens_index.get_token()
            if value.isnumeric():
                # Move back from the ;
                self.tokens_index.index -= 1
                math_expression = self.get_math_expression()
                if math_expression is None:
                    return None
                if self.tokens_index.get_token() == ";":
                    return ReturnDefinition(math_expression)
            elif value.isalnum():
                # TODO: Should check if this is a variable assignment
                if self.tokens_index.get_token() == ";":
                    return ReturnDefinition(value)
        return None
    
    def get_expression(self):
        pass

    def get_math_expression(self):
        # How do we best evaluate this ? 
        value_1 = self.tokens_index.get_token()
        if self.tokens_index.is_peek_token("+"):
            expr_2 = self.get_math_expression()
            if expr_2 is None:
                return None
            return MathOp(
                "+",
                NumericValue(value_1),
                expr_2
            )
        elif value_1.isnumeric():
            return NumericValue(value_1)

