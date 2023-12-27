import re

def format_asm_output(unformatted_asm):
    # TODO: Make this nicer and ideally part of the output logic
    for index in range(len(unformatted_asm)):
        output = []
        lines = unformatted_asm[index].split("\n")
        for i in lines:
            clean_text = re.sub(r"^\s+","", i)
            clean_text = re.sub(' +', ' ', clean_text)
            if not ":" in clean_text and not "." in clean_text:
                clean_text = "\t" + clean_text
            output.append(clean_text)
        unformatted_asm[index] = "\n".join(output)
    return "\n".join(list(filter(lambda x: len(x.strip()) > 0, "\n".join(unformatted_asm).split("\n")))) + "\n"
