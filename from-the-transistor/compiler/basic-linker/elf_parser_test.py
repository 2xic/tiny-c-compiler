from elf_parser import ElfParser
from capstone import *
from keystone import *

def test_should_be_able_to_read_and_write(bytes_raw):
    elf = ElfParser(bytes_raw)
    reconstructed = bytes(elf).hex()
    truth = bytes_raw.hex()
    print(reconstructed)
    print(truth)

    assert reconstructed == truth, f"{len(bytes(elf))} vs {len(bytes_raw)}"

def run_test_first():
    for test_file in [
        "bins/main.o",
        "bins/testPrint.o",
#        "bins/runnable",
    ]:
        with open(test_file, "rb") as file:
            test_should_be_able_to_read_and_write(file.read())
        print(f"{test_file} passed")
    print("all test passed")

def dissemble_text_section(code):
  #  section = elf.sections[1].data # .text
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for i in md.disasm(code, 0x1000):
        print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))

def assemble_text(code):
    try:
        ks = Ks(KS_ARCH_X86, KS_MODE_64)
        encoding, _ = ks.asm(code)
        return (bytes(encoding))
    except KsError as e:
        print("ERROR: %s" %e)

if __name__ == "__main__":
    run_test_first()

    print(assemble_text(b'INC ecx; DEC edx'))
    print(dissemble_text_section(assemble_text(b'INC ecx; DEC edx')))
    

    with open("bins/main.o", "rb") as file:
        bytes_raw = file.read()
        elf = ElfParser(bytes_raw)
        # If I modify a header, then I need to adjust all the headers that is within this scope ? Right ? 
        print(elf.sections[1].data)
        print("reconstructed output")
            
        new_elf = elf.modify_text_section(
            assemble_text(b'INC ecx; DEC edx')
        )
        print(new_elf.hex())
        print("=" * 32)
        print("Real output")
        print(bytes_raw.hex())
        with open("./bins/new_elf.o", "wb") as file:
            file.write(new_elf)
