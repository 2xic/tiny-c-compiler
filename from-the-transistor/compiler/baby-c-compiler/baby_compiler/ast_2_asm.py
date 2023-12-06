"""
We got nice AST output, we need nice output :)
"""
from .ast import File, FunctionDefinition, ReturnDefinition, FunctionBody, VariableDeclaration, NumericValue, MathOp, VariableAssignment, FunctionCall, VariableReference, StringValue, Conditionals, IfCondition, ElseCondition, Equal


class AsmOutputStream:
    def __init__(self, name) -> None:
        self.name = name
        self.is_main = name == "main"
        self.output_stream = [
            """
.text
    .global _start
_start:
            """            
        ] if self.name == "main" else [
f"""
{name}: 
    movl $0, %eax
"""]

    def append(self, text):
        self.output_stream.append(text)

def create_sys_exit(exit_code):
    if isinstance(exit_code, NumericValue):
        return f"""
    movl    ${exit_code}, %ebx
    movl    $1, %eax
    int     $0x80
        """
    elif isinstance(exit_code, VariableReference):
        return f"""
    movl    {exit_code.variable}, %ebx
    movl    $1, %eax
    int     $0x80
        """
    else:
        # Hm - not ideal way to implement this but works
        return f"""
    movl    {exit_code}, %ebx
    movl    $1, %eax
    int     $0x80
        """


class Ast2Asm:
    def __init__(self, ast: File) -> None:
        self.ast = ast
        """
        We could also do section .data
        """
        self.output_asm = [
        ]
        self.data_sections = [
"""
.data
"""
        ]

        # TODO: Make this part of the node instead
        self.current_function = None
        self.built_in_functions = {
            "write":SyswriteMapping()
        }
        self.message_counter = 2


    def get_asm(self):
        """
        Okay, currently we don't have any root_file which maybe is an issue ?
        """
        # we need to start from the main file ? 
        print(self.ast)
        assert isinstance(self.ast, File)
        assert "main" in self.ast.functions
        
        main_function_output = AsmOutputStream(
            name="main"
        )
        self.convert_nodes(self.ast.functions["main"], main_function_output)
        other_functions = []
        for i in self.ast.functions:
            if i != "main":
                function_code = AsmOutputStream(
                    name=i
                )
                self.convert_nodes(self.ast.functions[i], function_code)
                print(self.ast.functions[i], function_code.output_stream)
                other_functions += function_code.output_stream


        # Need to insert one new lien at the end else the compiler is mad
        combined = main_function_output.output_stream + other_functions + self.data_sections
        return "\n".join(list(filter(lambda x: len(x.strip()) > 0, "\n".join(combined).split("\n")))) + "\n"

    def convert_nodes(self, node, output: AsmOutputStream):
        if isinstance(node, File):
            return self.convert_nodes(node, output)
        elif isinstance(node, FunctionDefinition):
            if not output.is_main:
                pass
             #   output.append("\tpushq   %rbp")
                #for argument in node.parameters.child_nodes:
                # we need to pop this off the stack at once ?
                # Well I can do a pop, but I don't want that 
                # I want to keep the values on the tack until we do the ret ..
                 #   pass
                 #   output.append("\tpushq $4")
                #if len(node.parameters.child_nodes):
                #    output.append("\tmovl 8(%rsp), %eax")
            self.current_function = node
            self.convert_nodes(node.body, output)


        elif isinstance(node, VariableDeclaration):
            # TODO: Doing this just because it is easier to deal with
            # Likely we should do some stack allocations etc depending on context 
            self.data_sections.append(
                f"\t{node.name}: .long 0"
            )
            if not node.value is None:
                # Else the node has to write the data to %eax at some point during the evaluation
                self.convert_nodes(node.value, output) 
                output.append(
                    f"\tmovl %eax, {node.name}"
                )
        elif isinstance(node, FunctionBody):
            for i in node.child_nodes:
                self.convert_nodes(i, output)
                if isinstance(i, Conditionals):
                    output.append("end_of_if:")
        elif isinstance(node, ReturnDefinition):
            if output.is_main:
                # technically it should only be a exit if this is the main opcode ...
                if isinstance(node.value, MathOp):
                    # Unwrap it ... push add push add ..
                    # We will store the results into memory ...
                    self.convert_nodes(node.value, output)
                    output.append(create_sys_exit("eax"))
                else:
                    output.append(create_sys_exit(node.value))
            else:
                if isinstance(node.value, NumericValue):
                    # We return a static value ? 
                    # okay 
                    output.append(f"\tmovl    ${node.value}, %eax")
                elif isinstance(node.value, MathOp):
                    self.convert_nodes(node.value, output)
                
                output.append("\tret")

        elif isinstance(node, MathOp):
            """
            The add opcode from assembly is like this
            ADD immediate value to a register
            """
            # We write to EAX, but should be able to do more dynamic allocations soon
            self.handle_math_opcodes(node.expr_1, output)
            self.handle_math_opcodes(node.expr_2, output)

        elif isinstance(node, VariableAssignment):
            # This should also zero out eax ....
            # ^ technically I think we should zero eax at a different point, but okay
            output.append(
                f"\tmovl $0, {node.v_reference}"
            )
            output.append(
                f"\tmovl $0, %eax"
            )
            # do the math
            if isinstance(node.value, NumericValue):
                output.append(
                    f"\tmovl ${node.value.value}, {node.v_reference}"
                )
            else:
                self.convert_nodes(node.value, output)
                output.append(
                    f"\tmovl %eax, {node.v_reference}"
                )
        elif isinstance(node, FunctionCall):
               if node.function_name in self.built_in_functions:
                    self.built_in_functions[node.function_name].convert(
                        node.parameters.child_nodes,
                        self,
                        output
                    )
               else:
                    for i in node.parameters.child_nodes:
                        if isinstance(i, NumericValue):
                            output.append(f"\tpush ${i.value}")
                        elif isinstance(i, StringValue):
                            print("WRITE STRINGS To RO SECTION!")
                        else:
                            raise Exception("Unknown parameter")
                    output.append(
                        f"\tcall {node.function_name}"
                    )
        elif isinstance(node, Conditionals):
            self.convert_nodes(node.if_condition, output)
            # Then we need to jump 
            # Then we can next condition, but not write to it yet.  
           # b_else_condition = AsmOutputStream()
            self.convert_nodes(node.else_condition, output)

        elif isinstance(node, IfCondition):
            self.convert_nodes(node.condition, output)
            output.append("loc_a:")
            self.convert_nodes(node.body, output)
            output.append("\tjmp end_of_if")
        elif isinstance(node, ElseCondition):
            output.append("loc_b:")
            # else:
            self.convert_nodes(node.body, output)
        elif isinstance(node, Equal):
            # I want to simple resolve here, variable reference are hard to think about ... 
            a: VariableReference = node.a 
            b: NumericValue = node.b
            output.append(
                f"\tcmpl ${b.value}, {a.variable}"
            )
            # todo: hardcoded ... fix
            output.append(
                f"\tjne loc_b"
            )
        else:
            print(node)
            raise Exception("Unknown node " + str(node))    
    
    def handle_math_opcodes(self, node, output):
        if isinstance(node, NumericValue):
            output.append(f"\taddl ${node}, %eax")
        elif isinstance(node, MathOp):
            self.convert_nodes(node, output)                
        elif isinstance(node, FunctionCall):
            self.backup_eax_then_add_restore(node, output)
        elif node is None:
            pass
        elif isinstance(node, VariableReference):
            # This way of looking up the arguments should be made illegal, plz fix it.
            for index, i in enumerate(self.current_function.parameters.child_nodes):
                if i.name == node.variable:
                    output.append(f"\taddl {8 * (index + 1)}(%rsp), %eax")
                    break
            #raise Exception(f"Unknown math op node ({node})")
        else:
            raise Exception(f"Unknown math op node ({node})")
        
    def backup_eax_then_add_restore(self, node, output):
        output.append("\tmovl %eax, %ebx") # copy over the value
        self.convert_nodes(node, output)
        output.append(
            f"\taddl %ebx, %eax"
        )


class SyswriteMapping:
    def __init__(self) -> None:
        pass

    def convert(self, parameters, asm_root: Ast2Asm, output: AsmOutputStream):
        assert isinstance(parameters[0], NumericValue)
        assert isinstance(parameters[1], NumericValue)
        assert isinstance(parameters[2], StringValue)
        string_value = parameters[2].value
        message_id = f"message{asm_root.message_counter}"
        output.append(
            "\txor     %eax, %eax",
        )
        output.append(
            "\txor     %ebx, %ebx",
        )

        asm_root.message_counter += 1
        asm_root.data_sections.append(
            f"\t{message_id}:  .ascii  \"{string_value}\""
        )
        output.append(
            "\tmov     $1, %rax",
        )
        output.append(
            "\tmov     $1, %rdi",
        )
#        output.append(
#            f"\tlea     {message_id}(%si), %rsi",
#        )
        output.append(
            f"\tlea     {message_id}(%rip), %rsi",
        )
        output.append(
            f"\tmov     ${len(string_value)}, %rdx"
        )
        output.append(
            "\tsyscall"
        )
