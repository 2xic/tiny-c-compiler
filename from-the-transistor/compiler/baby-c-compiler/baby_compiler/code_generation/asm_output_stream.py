from ..ast import StructMemberAccess, StructMemberDereferenceAccess

class AsmOutputStream:
    def __init__(self, name, global_variables, output_stream) -> None:
        self.name = name
        self.debug = True
        self.is_main = name == "main"
        self.output_stream = output_stream
        self.variables_stack_location = {}
        # TODO: I don't want this to be retracked here
        self.variable_2_type = {}
        self.global_variables = global_variables
        self.stack_location_offset = 0
        # We will never pop it off the stack, 
        self.data_sections = []

    @staticmethod
    def main_function(global_variables):
        return AsmOutputStream("main", global_variables,  [
            """
            .text
                .global _start
            _start:
            """            
        ])
    
    @staticmethod
    def text_section(global_variables):
        return AsmOutputStream("text", global_variables,  [
            """
            .text
            """            
        ])
    
    @staticmethod
    def defined_function(name, global_variables):
        return AsmOutputStream(name, global_variables,  [
            f"""
                .globl	{name}
                .type	{name}, @function
                {name}: 
                    movl $0, %eax
            """            
        ])

    @staticmethod
    def create_global_variables():
        return AsmOutputStream("var", {},  [])
    
    def get_or_set_stack_location(self, name, value):
        if isinstance(name, StructMemberAccess):
            name = name.get_path()
        elif isinstance(name, StructMemberDereferenceAccess):
            """
            The struct variable would be a segment reference.
            
            We need to know our pointer size position for the alignment
            """
            raise Exception("Not supported member access references")
        
        assert len(name.split(" ")) == 1, "Bad name"

        if not name in self.variables_stack_location:
            self.variables_stack_location[name] = (len(self.variables_stack_location) + 1)
            self.stack_location_offset += 1     
        # Size of the stack - location of the variable is where we should read :) 
        # Depending on the size of the stack is how far we need to look back!
        # Memory reference
        if value is None:
            return self.get_stack_value(name)
        elif type(value) == int or  value.isnumeric():
            return f"pushq ${value}"
        else:
            return f"pushq {value}"
        
    def get_stack_value(self, name, pushed_offset=0):
        if isinstance(name, StructMemberAccess):
            name = name.get_path()
        # Note: In this case we do dereference the value
        location = self.get_variable_offset(name) + pushed_offset
        return f"{location}(%rsp)"
        
    def get_argument_stack_offset(self, index, size):
        # Argument would be at the location 1 + {size - index}
        location = ((size - index) ) * 8 # Always add one for the ret
        return f"{location}"

    def get_memory_offset(self, name):
        # This should reference the memory address
        # THIS SHOULD NOT DEREFERENCE
        location = self.get_variable_offset(name)
        #assert location == 0, "Bad location"
        #return f"%rsp"
        return location

    def get_variable_offset(self, name):
        index = -1
        if isinstance(name, StructMemberAccess):
            name = name.get_path()
        
        if name in self.variables_stack_location:
            #print(f"Used variable stack location for position ({name})")
            index = self.variables_stack_location[name]
        else:
            #print(f"Tried to find variable ({name})", self.variables_stack_location)
            # TODO: This is added for handling the access of the struct root member
            # This should find the last entry of the value ...
            keys = list(self.variables_stack_location.keys())
            for key_index, i in enumerate(keys):
                has_next_entry = (key_index + 1) < len(keys)
                get_name = lambda x: x + "."
                if has_next_entry and get_name(name) in keys[key_index + 1]:
                    continue
                if get_name(name) in i:
                    index = self.variables_stack_location[i]
                    break

        if index == -1:
            raise Exception("Not found " + str(name))

        delta = (self.stack_location_offset - index)
        location = delta  * 8
        return location

    def append(self, text, comment=None):
        if self.debug:
            if comment is None:
                self.output_stream.append(text)
            else:
                self.output_stream.append(text + " # " + comment)
        else:
            self.output_stream.append(text)
