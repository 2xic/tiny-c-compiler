from elf_parser import ElfParser

def test_should_be_able_to_read_and_write(bytes_raw):
    elf = ElfParser(bytes_raw)
    return elf.modify_text_section(
        elf.sections[1].data + elf.sections[1].data
    ).hex() == bytes_raw.hex()

if __name__ == "__main__":
    with open("bins/main.o", "rb") as file:
        test_should_be_able_to_read_and_write(file.read())
