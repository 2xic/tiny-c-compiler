from ..ast import NumericValue

class MathExpressionsOperations:
    def __init__(self) -> None:
        self.operation = {
            "+": "addl",
            "-": "subl"
        }
        self.is_loaded = False

    def load_value(self, operation):
        if self.is_loaded:
            return self.operation[operation]
        else:
            self.is_loaded = True
            return "addl"
