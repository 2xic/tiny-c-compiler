

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
        is_waiting_for_string_termination = False
        while index < len(source_code):
            char = source_code[index]
            if is_waiting_for_new_line and char != "\n":
                index += 1
                continue
            elif is_waiting_for_new_line:
                is_waiting_for_new_line = False
            elif is_waiting_for_string_termination and char != '"':
                index += 1
                token += char 
                continue
            elif is_waiting_for_string_termination and char == '"':
                index += 1
                tokens.append(token)
                tokens.append(char)
                token = ""
                is_waiting_for_string_termination = False
                continue

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
            elif char == '"':
                if len(token):
                    tokens.append(token)
                tokens.append(char)
                is_waiting_for_string_termination = True
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
