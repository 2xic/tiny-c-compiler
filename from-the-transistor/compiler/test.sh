#cd baby-libc && make tests

cd baby-libc && make tests && cd .. && cd baby-c-compiler && make tests  && python3 -m baby_compiler.tests 

# cd baby-c-compiler && make tests  && python3 -m baby_compiler.tests 
