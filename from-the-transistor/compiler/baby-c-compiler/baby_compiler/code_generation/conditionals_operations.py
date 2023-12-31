from ..ast import Equal, NotEqual, LessThanEqual, LessThan, GreaterThan, GreaterThanEqual, ConditionalType

def get_conditional_instruction(node: ConditionalType):
    if isinstance(node, Equal):
        return "je"
    elif isinstance(node, NotEqual):
        return "jne"
    elif isinstance(node, LessThan):
        return "jl"
    elif isinstance(node, LessThanEqual):
        return "jle"
    elif isinstance(node, GreaterThan):
        return "jg"
    elif isinstance(node, GreaterThanEqual):
        return "jge"
    else:
        raise Exception("Unknown ?")

    
