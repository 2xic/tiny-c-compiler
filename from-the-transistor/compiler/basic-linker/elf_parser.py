"""
No libraries that I can easily modify the .text section with - I'm so sad

I'll make it myself

https://dev.to/icyphox/python-for-reverse-engineering-1-elf-binaries-1fo4

"""

class BytesValue:
    def __init__(self, value) -> None:
        self.value = value
        self.bytes = value
        self.numeric_value = int.from_bytes(value, byteorder='little')

    def __bytes__(self):
        return self.value
    
    @staticmethod
    def from_numeric(value, bytes_size):
        encoded = (value).to_bytes( bytes_size, byteorder='little') 
#        padding = b"\x00" * (bytes_size - len(encoded))
        return BytesValue( encoded  )
    
    def set_value(self, value):
        if type(value) == bytes:
            assert len(value) == len(self.value)
            return BytesValue(value)
        else:
            return BytesValue.from_numeric(value, len(self.value))


class Steamer:
    def __init__(self, bytes) -> None:
        self.bytes = bytes
        self.index = 0
        
    def read(self, size):
        if size == 0:
            return BytesValue(b'')
        content = self.bytes[self.index:self.index + size]
        self.index += size
        return BytesValue(content + b'')
        
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

# Fake streamer to simplify the life of constructing an ELF binary
class StreamerWrite:
    def __init__(self) -> None:
        pass

    def read(self, size):
        return BytesValue(b"\x00" * size)

    
class FileHeader:
    def __init__(self, streamer: Steamer) -> None:
        self.magic_bytes = streamer.read(4)
        if isinstance(streamer, Steamer):
            assert self.magic_bytes.value == b"\x7fELF", self.magic_bytes
        self.is_64_bit_bytes = streamer.read(1)
        # numeric debug
        self.is_64_bit = self.is_64_bit_bytes.numeric_value == 2
        
        self.big_endianness_bytes = streamer.read(1)
        # nuermic debug
        self.big_endianness = self.big_endianness_bytes.numeric_value == 2
        
        self.version = streamer.read(1) 
        self.os = streamer.read(1) # this is a lookup list
        self.abi_version = streamer.read(1)
        self.padding = streamer.read(7)
        self.object_type = streamer.read(2) 
        self.machine = streamer.read(2)
        self.elf_version = streamer.read(4)

        if isinstance(streamer, Steamer):
            assert streamer.index in [0x18], streamer.index # before the split

        self.entry = streamer.conditional_read(
            is_64_bit=self.is_64_bit,
            bit_32=4,
            bit_64=8
        )       
        self.phoff = streamer.conditional_read(
            is_64_bit=self.is_64_bit,
            bit_32=4,
            bit_64=8
        )     
        self.shoff = streamer.conditional_read( # e_shoff
            is_64_bit=self.is_64_bit,
            bit_32=4,
            bit_64=8
        )      
        self.flags = streamer.read(4)
        self.ehsize = streamer.read(2)
        self.phentsize = streamer.read(2)
        self.phnum = streamer.read(2)
        self.shentsize = streamer.read(2)
        self.shnum = streamer.read(2) # shnum
        self.shstrndx = streamer.read(2)

        if isinstance(streamer, Steamer):
            assert streamer.index in [0x34, 0x40], bytes.index # 32 bit or 64 bit

        expected_size = 0x40 if self.is_64_bit else 0x34
        assert bytes(self).hex() == streamer.bytes[streamer.index-expected_size:streamer.index].hex()

    def get_entry_point(self):
        return self.entry

    def get_sections(self, streamer: Steamer):
        return streamer.stream(
            self.shoff.numeric_value,
            self.shnum.numeric_value,
        )

    def get_program_header(self, streamer: Steamer):
#        print(self.phoff.numeric_value)
        assert self.phoff.numeric_value in [0x34, 0x40, 0x0] # This is normally where it starts, but could be different
        return streamer.stream(
            self.phoff.numeric_value,
            self.phnum.numeric_value,
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

    @staticmethod
    def create():
        file_header = FileHeader(StreamerWrite())
        file_header.magic_bytes = file_header.magic_bytes.set_value("b\x7fELF")
        file_header.is_64_bit_bytes = file_header.is_64_bit_bytes.set_value("\x02")
        file_header.big_endianness_bytes = file_header.is_64_bit_bytes.set_value("\x01")
        file_header.elf_version.bytes = file_header.is_64_bit_bytes.set_value("\x01")
        file_header.abi_version.bytes = file_header.is_64_bit_bytes.set_value("\x00")
        file_header.object_type.bytes = file_header.is_64_bit_bytes.set_value("\x02")
        file_header.machine.bytes = file_header.is_64_bit_bytes.set_value("\x3e\x00")
        # entry point ?
        file_header.phoff.bytes =  file_header.is_64_bit_bytes.set_value("\x40\x00\x00\x00")
        return file_header

class ProgramHeader:
    def __init__(self, is_64_bit, streamer: Steamer) -> None:
        # Notes from https://en.wikipedia.org/wiki/Executable_and_Linkable_Format#Program_header
        start_offset = streamer.index
        self.p_type = streamer.read(4) # Identifies the type of the segment. 
        self.p_flags_64 = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=0,
            bit_64=4
        ) # Segment-dependent flags (position for 64-bit structure)
        self.p_offset = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        ) # Offset of the segment in the file image. 
        self.p_vaddr = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        ) # Virtual address of the segment in memory. 
        self.p_paddr = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        ) # On systems where physical address is relevant, reserved for segment's physical address. 
        self.p_filesz = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        ) # Size in bytes of the segment in the file image. May be 0. 
        self.p_memsz = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8
        ) # Size in bytes of the segment in memory. May be 0. 
        self.p_flags_32 = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=0,
        ) # Segment-dependent flags (position for 32-bit structure). See above p_flags field for flag definitions. 
        self.p_align = streamer.conditional_read(
            is_64_bit=is_64_bit,
            bit_32=4,
            bit_64=8,
        ) # 0 and 1 specify no alignment. Otherwise should be a positive, integral power of 2, with p_vaddr equating p_offset modulus p_align. 
        assert (streamer.index - start_offset) in [0x20, 0x38], (streamer.index - start_offset) # 32 bit or 64 bit        
        expected_size = 0x38 if is_64_bit else 0x20
        assert bytes(self).hex() == streamer.bytes[streamer.index-expected_size:streamer.index].hex()

    def __str__(self) -> str:
        program_header_type = {
            0x00000000: "PT_NULL",
            0x00000001: "PT_LOAD",
            0x00000002: "PT_DYNAMIC",
            0x00000003: "PT_INTERP",
            0x00000004: "PT_NOTE",
            0x00000005: "PT_SHLIB",
            0x00000006: "PT_PHDR",
            0x00000007: "PT_TLS",
            0x60000000: "PT_LOOS",
            0x6FFFFFFF: "PT_HIOS",
            0x70000000: "PT_LOPROC",
            0x7FFFFFFF: "PT_HIPROC",
        }
        type = program_header_type.get(self.p_type.numeric_value, None)
        return f"Program header {type} "

    def __bytes__(self):
        return bytes(
            self.p_type.bytes +\
            self.p_flags_64.bytes +\
            self.p_offset.bytes +\
            self.p_vaddr.bytes +\
            self.p_paddr.bytes +\
            self.p_filesz.bytes +\
            self.p_memsz.bytes +\
            self.p_flags_32.bytes +\
            self.p_align.bytes
        )

    @staticmethod
    def create():
        file_header = ProgramHeader(StreamerWrite())
        file_header.p_type = file_header.p_type.set_value(b"\x01\x00\x00\x00")
        file_header.p_flags_64 = file_header.p_flags_64.set_value(b"\x05\x00\x00\x00")
        # offset = 0
        file_header.p_vaddr = file_header.p_flags_64.set_value(b"\x00\x00\x40\x00\x00\x00\x00\x00")
        file_header.p_paddr = file_header.p_flags_64.set_value(b"\x00\x00\x40\x00\x00\x00\x00\x00")
        file_header.p_filesz = file_header.p_flags_64.set_value(b"\xB0\x00\x00\x00\x00\x00\x00\x00")
        file_header.p_memsz = file_header.p_flags_64.set_value(b"\xB0\x00\x00\x00\x00\x00\x00\x00")
        file_header.p_align = file_header.p_flags_64.set_value(b"\x00\x00\20\x00\x00\x00\x00\x00")
                
        return file_header

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
        ) # Offset of the section in the file image. 
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

        self.start_offset = self.sh_offset.numeric_value
        self.end_offset = self.start_offset + self.sh_size.numeric_value
        self.data = streamer.bytes[self.start_offset:self.end_offset]

        expected_size = 0x40 if is_64_bit else 0x28
        assert bytes(self).hex() == streamer.bytes[streamer.index-expected_size:streamer.index].hex()

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
    def __init__(self, raw_bytes):
        self.raw_bytes = raw_bytes + b''
        self.bytes = Steamer(raw_bytes)
        self.file_header = FileHeader(self.bytes)
        self.sections = []
        self.program_header = []

        self.is_modified = False
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
        sorted_sections =  sorted(self.sections, key=lambda x: x.sh_offset.numeric_value )

        self._modify_text_sections(sorted_sections, new_bytes)
        self._modify_program_sections()

        return self.__bytes__()
    
    def __bytes__(self):
        sorted_sections =  sorted(self.sections, key=lambda x: x.sh_offset.numeric_value )
        sorted_program_headers = self.program_header #sorted(self.program_header, key=lambda x: x.p_offset.numeric_value )
        output = bytes()
        # file header
        output += bytes(self.file_header)
        # program headers
        for i in sorted_program_headers:
            print(i)
            output += bytes(i)
            assert self.is_modified or self.raw_bytes[:len(output)].hex() == output.hex()
        delta_sections = 0
        use_align = True
        # SECTION DATA
        current_offset = len(output)
        for index, i in enumerate(sorted_sections):
            need_to_align = 0
            if index > 1 and use_align:
                need_to_align = i.sh_offset.numeric_value - delta_sections
                if need_to_align > 0:
                    output += b"\x00" * need_to_align        
                elif need_to_align < 0:
                    # wtf ? I don't think this is how to do it ??? 
                    output = output[:need_to_align]        

            output += i.data
            delta_sections = len(output)            
            assert self.is_modified or self.raw_bytes[current_offset:len(output)].hex() == output[current_offset:].hex(), f"Failed at index {index} ({i.name})"
            current_offset = len(output)

        # Need to align ? Maybe ? 
        if use_align:
            delta = self.file_header.shoff.numeric_value - len(output)
            output += b"\x00" * delta
        # SECTIONS HEADERS
        for i in self.sections:
            output += bytes(i)
        return output
        

    def _modify_text_sections(self, sorted_sections, new_bytes):
        # Turn offs additional validation when converting back to bytes
        self.is_modified  =True
        delta_sections = 0
        size = 0
        for _, i in enumerate(sorted_sections):
            if i.name.decode('utf-8') == ".text":
                delta = len(new_bytes) - len(i.data)
                print("Modified at offsets -> ", i.sh_offset.numeric_value, i.sh_offset.numeric_value + i.sh_size.numeric_value)
                i.sh_size = BytesValue.from_numeric(len(new_bytes), len(i.sh_size.value))
                i.data = new_bytes
                delta_sections += delta
                self.modify_sections_at_index = (
                    i.sh_offset.numeric_value,
                     i.sh_offset.numeric_value + i.sh_size.numeric_value,
                    delta    
                )
            else:
                current_offset = i.sh_offset
                i.sh_offset = BytesValue.from_numeric(delta_sections + current_offset.numeric_value, len(current_offset.bytes))
                if delta_sections:
                    print("Moved the section a bit ...", i.name, delta_sections)
            size += i.sh_size.numeric_value
        return size
        
    def _modify_program_sections(self):
        for i in self.program_header:
            #print((i.p_offset.numeric_value, i.p_offset.numeric_value + i.p_size.numeric_value))
            (start, old_size, delta) = self.modify_sections_at_index
            if i.p_offset.numeric_value <= start:
                i.p_filesz = BytesValue.from_numeric(i.p_filesz.numeric_value - delta, len(i.p_filesz.value))
                print("Moved one section ", i)
 
