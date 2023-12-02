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
            ";"
        ]
        self.tokens = self._get_tokens(source_code)

    def _get_tokens(self, source_code):
        index = 0
        tokens = []

        token = ""
        while index < len(source_code):
            char = source_code[index]
            if char in self.special_symbols:
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
        return f"{self.__class__.__name__} ({name}) " + str(self.child_nodes)

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
    
class File(Nodes):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        self.functions = {}

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

        assert self.tokens_index.index == len(self.tokens), self.tokens_index.index
        return file

    def get_root_symbols(self):
        # grammar: [return type] [function name] [parameter start] .... [parameter end] [scope start]
        checkpoint = self.tokens_index.index
        function_scope = self.get_function_definition()
        # If nothing is found
        if function_scope is None:
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
                body = self.parse_function_body()
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
            if self.tokens_index.get_token() == "return":
                value = self.tokens_index.get_token()
                if value.isnumeric():
                    if self.tokens_index.get_token() == ";":
                        if self.tokens_index.get_token() == "}":
                            return ReturnDefinition(value)
        return None

