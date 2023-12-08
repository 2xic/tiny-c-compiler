"""
No libraries that I can easily modify the .text section with - I'm so sad

I'll make it myself
"""

class BytesValue:
    def __init__(self, value) -> None:
        self.value = value
        self.bytes = value
        self.numeric_value = int.from_bytes(value, byteorder='little')

    def __bytes__(self):
        return self.value
    

class Steamer:
    def __init__(self, bytes) -> None:
        self.bytes = bytes
        self.index = 0
        
    def read(self, size):
        content = self.bytes[self.index:self.index + size]
        self.index += size
        return BytesValue(content + b'')
    
    def read_numeric(self, size):
        bytes = self.read(size)
        return bytes.numeric_value
    
    def conditional_read(self, is_64_bit, bit_32, bit_64):
        if is_64_bit:
            return self.read(bit_64)
        else:
            return self.read(bit_32)
        
    def stream(self, from_offset, entries):
        a = Steamer(self.bytes + b'')
        a.index = from_offset
        return [
            a for _ in range(entries)
        ]
    
class FileHeader:
    def __init__(self, bytes: Steamer) -> None:
        self.magic_bytes = bytes.read(4)
        assert self.magic_bytes.value == b"\x7fELF", self.magic_bytes
        self.is_64_bit_bytes = bytes.read(1)
        # numeric debug
        self.is_64_bit = self.is_64_bit_bytes.numeric_value == 2
        
        self.big_endianness_bytes = bytes.read(1)
        # nuermic debug
        self.big_endianness = self.big_endianness_bytes.numeric_value == 2
        
        self.version = bytes.read(1) 
        self.os = bytes.read(1) # this is a lookup lsit
        self.abi_version = bytes.read(1)
        self.padding = bytes.read(7)
        self.object_type = bytes.read(2) 
        self.machine = bytes.read(2)
        self.elf_version = bytes.read(4)

        assert bytes.index in [0x18], bytes.index # before the split

        self.entry = bytes.conditional_read(
            is_64_bit=self.is_64_bit,
            bit_32=4,
            bit_64=8
        )       
        self.phoff = bytes.conditional_read(
            is_64_bit=self.is_64_bit,
            bit_32=4,
            bit_64=8
        )     
        self.shoff = bytes.conditional_read( # e_shoff
            is_64_bit=self.is_64_bit,
            bit_32=4,
            bit_64=8
        )      
        self.flags = bytes.read(4)
        self.ehsize = bytes.read(2)
        self.phentsize = bytes.read(2)
        self.phnum = bytes.read(2)
        self.shentsize = bytes.read(2)
        self.shnum = bytes.read(2) # shnum
        self.shstrndx = bytes.read(2)
        assert bytes.index in [0x34, 0x40], bytes.index # 32 bit or 64 bit

    def get_entry_point(self):
        return self.entry

    def get_sections(self, streamer: Steamer):
        return streamer.stream(
            self.shoff.numeric_value,
            self.shnum.numeric_value,
        )

    def get_program_header(self, streamer: Steamer):
        return streamer.stream(
            (self.phoff.numeric_value),
            (self.phentsize.numeric_value),
        )

    def get_section_names_index(self):
        return (self.shstrndx.numeric_value)

    def __bytes__(self):
        output = bytes(
            self.magic_bytes.bytes +\
            self.is_64_bit_bytes.bytes +\
            self.big_endianness_bytes.bytes +\
            self.version.bytes +\
            self.os.bytes +\
            self.abi_version.bytes +\
            self.padding.bytes +\
            self.object_type.bytes +\
            self.machine.bytes +\
            self.elf_version.bytes +\
            self.entry.bytes +\
            self.phoff.bytes +\
            self.shoff.bytes +\
            self.flags.bytes +\
            self.ehsize.bytes +\
            self.phentsize.bytes +\
            self.phnum.bytes +\
            self.shentsize.bytes +\
            self.shnum.bytes +\
            self.shstrndx.bytes
        )
       # assert len(output) in [0x34, 0x40], len(output)
        return output
class ProgramHeader:
    def __init__(self, is_64_bit, streamer: Steamer) -> None:
        start_offset = streamer.index
        self.p_type = streamer.read(4)
        self.p_flags = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=0,
            bit_64=4
        )
        self.p_offset = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        )
        self.p_vaddr = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        )
        self.p_paddr = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        )
        self.p_filesz = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        )
        self.p_memsz = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        )
        self.p_flags = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=0,
        )
        self.p_align = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        assert (streamer.index - start_offset) in [0x20, 0x38], (streamer.index - start_offset) # 32 bit or 64 bit

    def __bytes__(self):
        return bytes(
            self.p_type +\
            self.p_flags +\
            self.p_offset +\
            self.p_vaddr +\
            self.p_paddr +\
            self.p_filesz +\
            self.p_memsz +\
            self.p_flags +\
            self.p_align
        )

class SectionHeader:
    def __init__(self, is_64_bit, streamer: Steamer) -> None:
        self.name = None
        start_offset = streamer.index
        self.sh_name = streamer.read(4)
        self.sh_type = streamer.read(4)
        self.sh_flags = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        self.sh_addr = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        self.sh_offset = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        self.sh_size = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        self.sh_link = streamer.read(4)
        self.sh_info = streamer.read(4)
        self.sh_addralign = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        self.sh_entsize = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        )
        assert (streamer.index - start_offset) in [0x28, 0x40], (streamer.index - start_offset) # 32 bit or 64 bit

        start_offset = self.sh_offset.numeric_value
        end_offset = start_offset + self.sh_size.numeric_value
        self.data = streamer.bytes[start_offset:end_offset]

    def __bytes__(self):
        return bytes(
            self.sh_name.bytes +\
            self.sh_type.bytes +\
            self.sh_flags.bytes +\
            self.sh_addr.bytes +\
            self.sh_offset.bytes +\
            self.sh_size.bytes +\
            self.sh_link.bytes +\
            self.sh_info.bytes +\
            self.sh_addralign.bytes +\
            self.sh_entsize.bytes
        )

    def get_content(self):
        self.data = self.data

    def __str__(self):
        return self.name.decode('utf-8')
    
    def __repr__(self) -> str:
        return self.__str__()

class ElfParser:
    def __init__(self, bytes):
        self.bytes = Steamer(bytes)
        self.file_header = FileHeader(self.bytes)
        self.sections = []
        self.program_header = []

        self._load_sections()
        self._load_program_header()

    def _load_sections(self):
        output = []
        for streamer in self.file_header.get_sections(self.bytes):
            output.append(
                SectionHeader(
                    is_64_bit=self.file_header.is_64_bit,
                    streamer=streamer,
                )
            )  
        section_names = self.file_header.get_section_names_index()
        for i in output:
            # IS THIS A HACK ?
            index = i.sh_name.numeric_value
            if i.sh_name == 0:
                index = 1 
            section = output[section_names].data[index:]
            i.name = section[:section.index(b"\0")]

        self.sections = output

    def _load_program_header(self):
        output = []
        for streamer in self.file_header.get_program_header(self.bytes):
            output.append(
                ProgramHeader(
                    is_64_bit=self.file_header.is_64_bit,
                    streamer=streamer,
                )
            )
        self.program_header = output  
    
    def modify_text_section(self, new_bytes):
        """
        Structure of the ELF
        - ELF Header
        - Program Header (?)
        - Sections of data and code
        - Sections header
        """
        output = bytes()
        output += bytes(self.file_header)
        for i in self.program_header:
            output += bytes(i)
        delta_sections = 0
        for index, i in enumerate( sorted(self.sections, key=lambda x: x.sh_offset.numeric_value )):
            if index > 1:
                if (i.sh_offset.numeric_value - delta_sections) > 0:
                    output += b"\x00" * (i.sh_offset.numeric_value - delta_sections)                
            output += i.data
            delta_sections = (i.sh_offset.numeric_value + i.sh_size.numeric_value)
        ## output += bytes.fromhex("f00dbabe")
        delta = self.file_header.shoff.numeric_value - len(output)
        output += b"\x00" * delta
        print((delta))
        for i in self.sections:
            output += bytes(i)
        return output

    
if __name__ == "__main__":
    with open("bins/main.o", "rb") as file:
        bytes_raw = file.read()
        elf = ElfParser(bytes_raw)
        # If I modify a header, then I need to adjust all the headers that is within this scope ? Right ? 
        print(elf.sections[1].data)
        print("recounstrcted output")
        print(elf.modify_text_section(
            elf.sections[1].data + elf.sections[1].data
        ).hex())
        print("=" * 32)
        print("Real output")
        print(bytes_raw.hex())
