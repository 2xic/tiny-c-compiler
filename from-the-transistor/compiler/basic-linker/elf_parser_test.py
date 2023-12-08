from elf_parser import ElfParser

def test_should_be_able_to_read_and_write(bytes_raw):
    elf = ElfParser(bytes_raw)
    assert elf.modify_text_section(elf.sections[1].data).hex() == bytes_raw.hex()

def run_test_first():
    with open("bins/main.o", "rb") as file:
        test_should_be_able_to_read_and_write(file.read())
    print("test passed")

    
if __name__ == "__main__":
    run_test_first()

    with open("bins/main.o", "rb") as file:
        bytes_raw = file.read()
        elf = ElfParser(bytes_raw)
        # If I modify a header, then I need to adjust all the headers that is within this scope ? Right ? 
        print(elf.sections[1].data)
        print("recounstrcted output")
        new_elf = elf.modify_text_section(
            b'AJ'
        #    elf.sections[1].data + elf.sections[1].data
        )
        print(new_elf.hex())
        print("=" * 32)
        print("Real output")
        print(bytes_raw.hex())
        with open("./bins/new_elf.o", "wb") as file:
            file.write(new_elf)
