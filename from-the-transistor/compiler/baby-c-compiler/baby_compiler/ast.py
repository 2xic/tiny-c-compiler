"""
The AST has the ast logic.
"""
from typing import Optional
from .exceptions import InvalidSyntax
from typing import Dict

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
            "-",
            "~",
            "&",
            "|",
            ",",
            '"',
            ".",
            "-",
            ">",
            "=",
            "!"
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
        return tokens
    

"""
So based on tokens I create outputs. 
"""

class Nodes:
    def __init__(self) -> None:
        self.child_nodes = []
        # Filled in automatically later
        self.id: int = None
        self.parent: Optional[Nodes] = None

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

class Parameters(Nodes):
    def __init__(self, parameters) -> None:
        super().__init__()

        self.child_nodes = parameters

class FunctionDefinition(Nodes):
    def __init__(self, name, parameters: Parameters, body, return_parameters) -> None:
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

class ExternalFunctionDefinition(Nodes):
    def __init__(self, name, parameters: Parameters) -> None:
        super().__init__()
        self.name = name
        self.parameters = parameters

class FunctionCall(Nodes):
    def __init__(self, function_name, parameters: Parameters) -> None:
        super().__init__()
        self.function_name = function_name
        self.parameters = parameters

class FunctionBody(Nodes):
    def __init__(self) -> None:
        super().__init__()


class TokenConsumer:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.index = 0

    def get_token(self):
        if self.index > len(self.tokens):
            return None
        token = self.tokens[self.index]
        self.index += 1
        return token

    def is_peek_token(self, value):
        if type(value) == str:
            if self.get_token() == value:
                return True
            self.index -= 1
            return False
        elif type(value) == list:
            index = 0
            for i in range(len(value)):
                index += 1
                if self.get_token() != value[i]:
                    break
            if index == len(value):
                return True
            self.index -= index
            return False
        else:
            raise Exception("Unexpected token value")
    
    def peek_token(self, peek=0):
        if self.index + peek < len(self.tokens):
            return self.tokens[self.index + peek]
        
    def context(self):
        return self.tokens[self.index:self.index+5]


class File(Nodes):
    def __init__(self, name) -> None:
        super().__init__()
        self.name = name
        self.functions: Dict[str, FunctionDefinition] = {}
        self.external_functions: Dict[str, ExternalFunctionDefinition] = {}
        self.global_variables = {}
        self.global_types = {}

class VariableDeclaration(Nodes):
    def __init__(self, type: TypeDefinition, name, value) -> None:
        super().__init__()
        self.type = type
        self.is_pointer = "*" in str(self.type)#.name
        self.name = name
        self.value = value
        self.child_nodes = [type, value]

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

class BinaryOperation(Nodes):
    def __init__(self, op, expr_1) -> None:
        super().__init__()
        self.op = op
        self.expr_1 = expr_1
        self.child_nodes = [
            expr_1,
        ]

class VariableAssignment(Nodes):
    def __init__(self, v_reference, v_value) -> None:
        super().__init__()
        self.left_side = v_reference
        self.right_side = v_value
        self.child_nodes = [
            v_reference,
            v_value
        ]

class VariableReference(Nodes):
    def __init__(self, variable) -> None:
        super().__init__()
        self.variable = variable
        self.child_nodes = [
            variable
        ]

class NumericValue(Nodes):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.child_nodes = [
            value
        ]

class StringValue(Nodes):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.child_nodes = [
            value
        ]

class Conditionals(Nodes):
    def __init__(self, if_condition, else_condition, else_if_conditions) -> None:
        super().__init__()
        self.if_condition =  if_condition
        self.else_condition = else_condition
        self.else_if_conditions = else_if_conditions
        self.child_nodes = [
            if_condition,] + else_if_conditions + [
            else_condition,
        ]

class WhileConditional(Nodes):
    def __init__(self, conditional, body) -> None:
        super().__init__()
        self.conditional = conditional 
        self.body =  body
        self.child_nodes = [
            self.conditional,
            self.body
        ]

class IfCondition(Nodes):
    def __init__(self, condition, body) -> None:
        super().__init__()
        self.condition = condition
        self.body = body
        self.child_nodes = [
            condition,
            body
        ]
class ElseIfCondition(Nodes):
    def __init__(self, condition, body) -> None:
        super().__init__()
        self.condition = condition
        self.body = body
        self.child_nodes = [
            body
        ]

class ElseCondition(Nodes):
    def __init__(self, body) -> None:
        super().__init__()
        self.body = body
        self.child_nodes = [
            body
        ]

class ConditionCheck(Nodes):
    def __init__(self, value) -> None:
        super().__init__()
        self.value = value
        self.child_nodes = [
            value
        ]


class Equal(Nodes):
    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a 
        self.b = b
        self.child_nodes = [
            a, b
        ]

class NotEqual(Nodes):
    def __init__(self, a, b) -> None:
        super().__init__()
        self.a = a 
        self.b = b
        self.child_nodes = [
            a, b
        ]

class VariableAddressReference(Nodes):
    def __init__(self, variable) -> None:
        super().__init__()
        self.child_nodes = [variable]
        self.variable = variable

class VariableAddressDereference(Nodes):
    def __init__(self, value: VariableReference) -> None:
        super().__init__()
        self.value = value
        self.child_nodes = [value]

class AssignGlobalValues:
    def __init__(self) -> None:
        self.id = 0

    def assign_scope(self, node: Nodes):
        for i in node.child_nodes:
            # TODO: All nodes should use nodes
            if isinstance(i, Nodes):
                setattr(i, "id", self.id)
                setattr(i, "parent", node)
                self.id += 1
                self.assign_scope(i)
        return node

class Struct(Nodes):
    def __init__(self, name, members) -> None:
        super().__init__()
        self.name = name
        self.members = members

class StructMemberAccess(Nodes):
    def __init__(self, variable_reference: VariableReference, member_name: str) -> None:
        super().__init__()
        self.child_nodes = [
            variable_reference,
            member_name,
        ]
        self.variable_reference = variable_reference
        self.value = member_name 

    def get_path(self):
        return self.variable_reference + "."+ self.value

class StructMemberDereferenceAccess(Nodes):
    def __init__(self, variable_reference: VariableReference, member_name: str) -> None:
        super().__init__()
        self.child_nodes = [
            variable_reference,
            member_name,
        ]
        self.variable_reference = variable_reference
        self.value = member_name 

    def get_path(self):
        return self.variable_reference + "->"+ self.value

class ForLoop(Nodes):
    def __init__(self, initialization_statement, test_expression_statement, update_statement, body) -> None:
        super().__init__()
        self.initialization_statement = initialization_statement 
        self.test_expression_statement = test_expression_statement
        self.update_statement = update_statement
        self.body =  body
        self.child_nodes = [
            self.initialization_statement,
            self.test_expression_statement,
            self.update_statement,
            self.body
        ]

class AST:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.types = {
            "int": TypeDefinition("int"),
            "int*": TypeDefinition("int*"),
        }
        # Need to reconsider this... Is this how we want to create the tree?
        self.variables = {}
        self.id = 0
        self.tokens_index = TokenConsumer(self.tokens)
        # TODO: Make this shared with the ast_2_asm logic
        self.global_functions = [
            "write",
            "brk"
        ]
        self.assign_global_values = AssignGlobalValues()

    def build_ast(self):
        # Statements currently supported are only tokens
        self.file = File("example.c")

        prev_token = -1
        while prev_token !=  self.tokens_index.index and self.tokens_index.index < len(self.tokens):
            # Keep track of global variables only
            old_variables = {
                key:value for key, value in self.variables.items()
            }
            prev_token =  self.tokens_index.index
            file_nodes = self.get_root_symbols()
            self.file.child_nodes.append(file_nodes)
            if isinstance(file_nodes, FunctionDefinition):
                if file_nodes.name in self.file.functions:
                    raise InvalidSyntax(f"Invalid - re-declaration of variable of {file_nodes.name}")
                self.file.functions[file_nodes.name] = self.assign_global_values.assign_scope(file_nodes)
                # Reset the variables between scopes
                self.variables = old_variables
            elif isinstance(file_nodes, ExternalFunctionDefinition):
                self.file.functions[file_nodes.name] = self.assign_global_values.assign_scope(file_nodes)
                self.file.external_functions[file_nodes.name] = self.assign_global_values.assign_scope(file_nodes) # file_nodes.name
            elif isinstance(file_nodes, Struct):
                self.file.global_types[file_nodes.name] = file_nodes
            elif isinstance(file_nodes, VariableDeclaration):
                if file_nodes.name in self.file.global_variables:
                    raise InvalidSyntax(f"Invalid - re-declaration of variable of {file_nodes.name}")
                self.file.global_variables[file_nodes.name] = file_nodes

        assert self.tokens_index.index == len(self.tokens),  "Failed to parse source code..."
        return self.file

    def get_root_symbols(self):
        # grammar: [return type] [function name] [parameter start] .... [parameter end] [scope start]
        checkpoint = self.tokens_index.index
        for scopes in [self.get_function_definition, self.get_variable_declaration_or_assignment, self.get_struct_definition]:
            function_scope = scopes()
            # If nothing is found
            if function_scope is None:
                self.tokens_index.index = checkpoint
            else:
                break
        
        if function_scope is None:
            print("Failed at ", self.tokens_index.tokens[self.tokens_index.index:self.tokens_index.index+5])

        if self.tokens_index == checkpoint:
            raise Exception("Failed to create AST :(")

        return function_scope

    def get_function_definition(self):
        return_type = self.get_type()
        if return_type is not None:
            name = self.tokens_index.get_token()
            if self.is_valid_variable(name):
                parameters = self.get_function_definition_arguments()
                if parameters is None:
                    return None
                if self.tokens_index.peek_token() == ";":
                    assert self.tokens_index.get_token() == ";"
                    return ExternalFunctionDefinition(
                        name,
                        parameters=parameters
                    )
                body = self.parse_function_body()
                if body is None:
                    return None
                
                return FunctionDefinition(
                    name,
                    parameters,
                    body,
                    return_type
                )
        return None

    def get_function_call_arguments(self):
        if self.tokens_index.get_token() == "(":
            parameters = []
            while not self.tokens_index.peek_token() == ")":
                numeric = self.get_numeric()
                # TODO: We could here also in theory do math operations
                if numeric is not None:
                    parameters.append(numeric)
                elif self.tokens_index.peek_token() == ",":
                    self.tokens_index.get_token()
                elif self.tokens_index.peek_token() == '"':
                    _ = self.tokens_index.get_token()
                    value = self.tokens_index.get_token()
                    assert '"' == self.tokens_index.get_token(), "Expected terminator"
                    parameters.append(StringValue(
                        value
                    ))
                elif self.tokens_index.peek_token() in self.variables:
                    parameters.append(VariableReference(
                        self.tokens_index.get_token()
                    ))
                else:
                    raise Exception(f"Unknown call argument {self.tokens_index.peek_token()}")
            assert self.tokens_index.get_token() == ")"
            return Parameters(parameters)
        return None

    def get_function_definition_arguments(self):
        if self.tokens_index.get_token() == "(":
            parameters = []
            while not self.tokens_index.peek_token() == ")":
                type_value = self.get_type()
                if type_value is not None:
                    parameters.append(
                        VariableDeclaration(
                            type=type_value,
                            name=self.tokens_index.get_token(),
                            value=None,
                        )
                    )
                    self.variables[parameters[-1].name] = True
                elif self.tokens_index.peek_token() == ",":
                    self.tokens_index.get_token()
                else:
                    raise Exception(f"Unknown input '{self.tokens_index.peek_token()}'")
            assert self.tokens_index.get_token() == ")"
            return Parameters(parameters)
        return None

    def parse_function_body(self):
        if self.tokens_index.get_token() == "{":
            found_token = True
            body = FunctionBody()
            while found_token:
                for create_node in [
                    self.get_return_definition,
                    self.get_variable_declaration_or_assignment,
                    self.parse_conditional_statements,
                    self.get_inline_function_call,
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
    
    def get_variable_declaration_or_assignment(self):
        type_value = self.get_type()
        if type_value is not None:
            name = self.tokens_index.get_token()
            if self.is_valid_variable(name):
                if self.tokens_index.is_peek_token("="):
                    math_expression = self.get_math_expression()
                    if self.tokens_index.get_token() == ";" and math_expression is not None:
                        # variable initiation
                        value = VariableDeclaration(
                            type_value,
                            name,
                            math_expression
                        )
                        self.variables[name] = value
                        return value
                elif self.tokens_index.is_peek_token(";"):
                    value = VariableDeclaration(
                        type_value,
                        name,
                        None
                    )
                    self.variables[name] = value
                    return value
        else:
            token = self.tokens_index.get_token()
            if token in self.variables:
                if self.tokens_index.is_peek_token("."):
                    field = self.tokens_index.get_token()
                    token = StructMemberAccess(
                        token,
                        field
                    )
                elif self.tokens_index.is_peek_token(["-", ">"]):
                    field = self.tokens_index.get_token()
                    token = StructMemberDereferenceAccess(
                        token,
                        field
                    )
                # This is an assignment ... 
                if self.tokens_index.is_peek_token("="):
                    math_expression = self.get_math_expression()
                    if self.tokens_index.get_token() == ";" and math_expression is not None:
                        return VariableAssignment(
                            token,
                            math_expression,
                        )
                elif self.tokens_index.is_peek_token(["+", "+", ";"]):
                    return BinaryOperation(
                        "++",
                        VariableReference(token)
                    )
            elif token == "*":
                # Dereference
                value = self.tokens_index.get_token()
                if value in self.variables:
                    if self.tokens_index.is_peek_token("="):
                        math_expression = self.get_math_expression()
                        if self.tokens_index.get_token() == ";" and math_expression is not None:
                            return VariableAssignment(
                                VariableAddressDereference(VariableReference(value)),
                                math_expression,                            
                            )
        return None
    
    def get_return_definition(self):
        if self.tokens_index.get_token() == "return":
            math_expression = self.get_math_expression()
            if math_expression is None:
                return None
            if self.tokens_index.get_token() == ";":
                return ReturnDefinition(math_expression)
        return None
    
    def get_math_expression(self):
        # How do we best evaluate this ? 
        value_1 = self.get_expression()
        if self.tokens_index.is_peek_token("+"):
            expr_2 = self.get_math_expression()
            if expr_2 is None:
                return None
            return MathOp(
                "+",
                value_1,
                expr_2
            )
        elif value_1:
            return value_1
        return None

    def get_expression(self):
        token = self.tokens_index.peek_token()
        numeric = self.get_numeric()
        if numeric is not None:
            return numeric
        elif token.isalnum() and self.tokens_index.peek_token(1) == "(":
            return self.get_function_call()
        elif token in self.variables:
            token = self.tokens_index.get_token()
            assert token in self.variables
            if self.tokens_index.is_peek_token("."):
                return VariableReference(
                    StructMemberAccess(
                        token,
                        self.tokens_index.get_token()
                    )
                )            
            elif self.tokens_index.is_peek_token(["-", ">"]):
                return VariableReference(
                    StructMemberDereferenceAccess(
                        token,
                        self.tokens_index.get_token()
                    )
                )    
            else:
                return VariableReference(token)
        elif token == "&":
            # == Memory pointer
            _ = self.tokens_index.get_token()
            name = self.tokens_index.get_token()
            if name in self.variables:
                return VariableAddressReference(VariableReference(name))
            else:
                raise Exception("Unknown expression node {token}")            
        else:
            raise InvalidSyntax(f"Unknown expression node {token} - bad call ?")
        
    def get_inline_function_call(self):
        value = self.get_function_call()        
        if value is not None and self.tokens_index.peek_token() == ";":
            assert self.tokens_index.get_token() == ";"
            return value
    
    def get_function_call(self):
        token = self.tokens_index.get_token()
        if self.tokens_index.peek_token(0) == "(":
            if token in self.file.functions or token in self.global_functions:
                function_arguments = self.get_function_call_arguments()
                return FunctionCall(
                    token,
                    function_arguments,
                )
            else:
                raise InvalidSyntax()

    def parse_conditional_statements(self):
        token = self.tokens_index.get_token()
        # From here we can find and else or else if
        if  self.tokens_index.peek_token(0) == "(" and token == "if":
            assert self.tokens_index.get_token() == "("
            if_condition = self.parse_if_statements(can_be_if=True)
            else_if_conditions = []
            else_condition = None
            while True:
                value = self.parse_if_statements(can_be_if=False)
                if isinstance(value, ElseCondition):
                    else_condition = value
                elif isinstance(value, ElseIfCondition):
                    else_if_conditions.append(value)
                elif value is not None:
                    raise Exception("Unknown condition")
                else:
                    break

            return Conditionals(
                if_condition=if_condition,
                else_condition=else_condition,
                else_if_conditions=else_if_conditions
            )
        elif  self.tokens_index.peek_token(0) == "(" and token == "while":
            assert self.tokens_index.get_token() == "("
            conditional = self.get_conditional_equal()
            assert self.tokens_index.get_token() == ")", "Bad end argument"
            return WhileConditional(
                conditional=conditional,
                body=self.parse_function_body()
            )
        elif  self.tokens_index.peek_token(0) == "(" and token == "for":
            assert self.tokens_index.get_token() == "("
            initialization_statement = self.get_variable_declaration_or_assignment()
            test_expression_statement = self.get_conditional_equal()
            assert self.tokens_index.get_token() == ";", "Expected test statement to be terminated"
            update_statement = self.get_update_statement()
            assert self.tokens_index.get_token() == ")", "Expected update statement to be terminated"

            return ForLoop(
                initialization_statement=initialization_statement,
                test_expression_statement=test_expression_statement,
                update_statement=update_statement,
                body=self.parse_function_body(),
            )

    def parse_if_statements(self, can_be_if=False):
        if can_be_if:
            return self.parse_condition_body()
        else:
            # TODO: Convert into a is_peek_token call
            token = self.tokens_index.peek_token(0)
            if  self.tokens_index.peek_token(1) == "{" and token == "else":
                assert self.tokens_index.get_token() == "else"
                return ElseCondition(
                    body=self.parse_function_body()
                )
            elif token == "else" and self.tokens_index.peek_token(1) == "if" and self.tokens_index.peek_token(2) == "(" :
                assert self.tokens_index.get_token() == "else"
                assert self.tokens_index.get_token() == "if"
                assert self.tokens_index.get_token() == "("
                condition = self.get_conditional_equal()
                assert self.tokens_index.get_token() == ")", "Bad end argument"
                return ElseIfCondition(
                    condition=condition,
                    body=self.parse_function_body()
                )

    def parse_condition_body(self):
        condition = self.get_conditional_equal()
        if condition is not None:
            assert self.tokens_index.get_token() == ")", "Bad end argument"
            return IfCondition(
                condition=condition,
                body=self.parse_function_body()
            )

    def get_conditional_equal(self):
        # TODO: This code can be shared more
        token = self.tokens_index.get_token()
        if self.tokens_index.is_peek_token(["=", "="]):
            if token in self.variables:
                first_expression = VariableReference(token)
                # Get the next token
                numeric = self.get_numeric()
                if not numeric is None:
                    second_expression = numeric
                    return Equal(
                        first_expression,
                        second_expression
                    )
                else:
                    raise Exception("Failed ")
            else:
                raise Exception("Not supported yet ... ")
        elif self.tokens_index.is_peek_token(["!", "="]):
            if token in self.variables:
                first_expression = VariableReference(token)
                # Get the next token
                numeric = self.get_numeric()
                if not numeric is None:
                    second_expression = numeric
                    return NotEqual(
                        first_expression,
                        second_expression
                    )
                else:
                    raise Exception("Failed ")
            else:
                raise Exception("Not supported yet ... ")
        return None
    
    def get_type(self):
        if self.tokens_index.peek_token() in self.types:
            type_name = self.tokens_index.get_token()
            pointer = self.tokens_index.peek_token() == "*"
            if pointer:
                pointer = self.tokens_index.get_token()
                type_name += pointer
            return TypeDefinition(type_name)
        elif self.tokens_index.peek_token() == "struct":
            assert self.tokens_index.get_token() == "struct"
            struct_name = self.tokens_index.get_token() 
            pointer = self.tokens_index.peek_token() == "*"
            if pointer:
                pointer = self.tokens_index.get_token()
                struct_name += pointer
            return TypeDefinition("struct " + struct_name)
        return None

    def get_struct_definition(self):
        if self.tokens_index.peek_token() == "struct":
            assert self.tokens_index.get_token() == "struct"
            name = self.tokens_index.get_token()
            members = self.parse_struct_members()
            assert self.tokens_index.get_token() == ";"
            return Struct(
                name=name, 
                members=members,
            )
        return None

    def parse_struct_members(self):
        if self.tokens_index.get_token() == "{":
            found_token = True
            members = []
            while found_token:
                for create_node in [
                    self.get_variable_declaration_or_assignment,
                ]:                    
                    local_check_point = self.tokens_index.index
                    node_definition = create_node()
                    if node_definition is None:
                        found_token = False
                        self.tokens_index.index = local_check_point
                    else:
                        members.append(node_definition)
                        found_token = True
                        break
            # if it all failed
            if self.tokens_index.get_token() == "}":
                return members 
        return None
        
    def get_numeric(self):
        if self.tokens_index.peek_token() == "-" and self.tokens_index.peek_token(1).isnumeric():
            _ = self.tokens_index.get_token()
            token = self.tokens_index.get_token()
            if token.isnumeric():
                return NumericValue("-" + token)
        elif self.tokens_index.peek_token().isnumeric():
            token = self.tokens_index.get_token()
            if token.isnumeric():
                return NumericValue(token)
        else:
            return None
        
    def get_update_statement(self):
        """
        TODO: Move the update of a variable assignment here
        """
        variable = self.tokens_index.get_token()
        if variable in self.variables:
            if self.tokens_index.is_peek_token(["+", "+"]):
                return BinaryOperation(
                    "++",
                    VariableReference(variable)
                )
    
    def is_valid_variable(self, name):
        return name.isidentifier()

