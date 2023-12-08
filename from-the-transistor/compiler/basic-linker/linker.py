"""
Simple linker, but it is a linker
"""

from elftools.elf.elffile import ELFFile, RelocationSection

class Linker:
    def __init__(self, object_files) -> None:
        self.object_files = object_files
        self.symbol_table = {}
        self.reallocation = {}
        for i in self.object_files:
            self.get_reallocation_section(i)
        print(self.symbol_table)
        print(self.reallocation)

    def get_reallocation_section(self, file):
        print(file)
        with open(file, 'rb') as f:
            e = ELFFile(f)
            for section in e.iter_sections():
                #print(hex(section["sh_addr"]), section.name)
                #print(section.data())
                #print(section.data().hex())
                #print("")

                if isinstance(section, RelocationSection):
                    symbol_table = e.get_section(section['sh_link'])
                    for relocation in section.iter_relocations():
                        symbol = symbol_table.get_symbol(relocation['r_info_sym'])
                        addr = hex(relocation['r_offset'])
                     #   print(f'{symbol.name} {addr}')
                        self.reallocation[symbol.name] = addr
                elif section.name == ".text":
                    print(section.data())
                elif section.name == '.symtab':
                    for symbol in section.iter_symbols():
                      #  print(symbol.entry)
                        symbol_name = symbol.name
                        symbol_address = symbol['st_value']
                        symbol_size = symbol['st_size']
                        offset = symbol_address - section['sh_addr']
                      #  print(offset)
                      #  print(section['sh_offset'])
                        f.seek(section['sh_offset'] + offset)
                        symbol_data = f.read(symbol_size)
                        print(symbol_data)
                        self.symbol_table[symbol_name] = {
                            'address': symbol_address,
                            'size': symbol_size
                        }

    def merge_in_changes(self):
        pass


if __name__ == "__main__":
    Linker([
        "./bins/main.o",
        "./bins/testPrint.o",
    ])

