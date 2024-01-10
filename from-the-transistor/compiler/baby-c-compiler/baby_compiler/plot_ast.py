"""
Debug util / visualization tool for the people!
"""
from .ast import Nodes, NumericValue, StringValue
import graphviz
from .ast import AST, File
from .tokenizer import Tokenizer
import sys

class PlotAst:
    def __init__(self, node: File) -> None:
        self.node = node


    def plot(self):
        dot = graphviz.Digraph('nodes', comment='nodes', format='png')

        nodes = []
        for i in self.node.functions.values():
            nodes.append(i)

        while len(nodes):
            # pass
            current_node = nodes.pop(0)
            if current_node is None:
                continue
            if current_node.id is None:
                print(str(current_node))
                raise Exception("Missing id")
            name = current_node.__class__.__name__
            ## TODO: Add more custom rendering ? 
            if isinstance(current_node, NumericValue):
                dot.node(str(current_node.id), name + "\nValue: " + str(current_node.value))
            elif isinstance(current_node, StringValue):
                dot.node(str(current_node.id), name + "\nValue: " + str(current_node.value))
            else:
                dot.node(str(current_node.id), name)
            for i in current_node.child_nodes:
                if isinstance(i, Nodes):
                    dot.edge(str(current_node.id), str(i.id))
                    nodes.append(i)
        dot.render('example', cleanup=True)

if __name__ == "__main__":
    input_file = sys.argv[1]
    # Simple debug tool
    with open(input_file, "r") as file:
        tokenizer = Tokenizer(
            file.read()
        )
        file_node = AST(tokenizer.tokens).build_ast()
        PlotAst(file_node).plot()
