from keystone import *
CODE = "\n".join([
    "movl $2, a"
])
ks = Ks(KS_ARCH_X86, KS_MODE_64)
ks.syntax = KS_OPT_SYNTAX_INTEL
encoding, count = ks.asm(CODE)
print(encoding)

